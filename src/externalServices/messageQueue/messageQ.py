from multiprocessing import JoinableQueue
import threading

from pika.adapters.asyncio_connection import AsyncioConnection
from pika.channel import Channel
from pika.connection import Connection
from pika.exceptions import ConnectionWrongStateError

from .services.getPikaConnectionParams import get_pika_connection_params

# Follows
# https://github.com/pika/pika/blob/master/examples/asynchronous_consumer_example.py

QueueName = "BookingServiceQueue"

CustomerInfo = {
    "ExchangeName": "events",
    "ExchangeType": "topic",
    "Topics": [
        "event.customer.created"
    ]
}


class MessageQueue:
    consumer_connection: Connection or None = None
    channel_rx: Channel or None = None
    closing = False
    pub_sub = []
    amqp_url = ""
    setup_ok: threading.Event = None
    events_handler_mq = None
    optimization_trigger_events = None

    internal_publish_queue: JoinableQueue

    @classmethod
    def init_app(cls, app, internal_publish_queue: JoinableQueue):
        from src.services.eventThread import EventsHandler

        cls.optimization_trigger_events = JoinableQueue()
        cls.internal_publish_queue = internal_publish_queue
        EventsHandler.init_app(internal_publish_queue)
        cls.setup_ok = app.config.get("SETUP_OK", None)
        cls.amqp_url = app.config.get("MESSAGE_QUEUE_URI", "")
        cls.consumer_connection = cls.connect_consumer()
        print("Consumer connection is successfully established")

    @classmethod
    def connect_consumer(cls):
        """ This method creates and returns the connection which is solely used
                for consuming of the messages from rabbitmq server"""

        client_properties = {
            'connection_name': 'booking-consumer-connection'
        }

        connection_parameters = get_pika_connection_params(cls.amqp_url, client_properties)
        return AsyncioConnection(
            parameters=connection_parameters,
            on_open_callback=cls.on_consumer_connection_open,
            on_open_error_callback=cls.on_consumer_connection_open_error,
            on_close_callback=cls.on_consumer_connection_closed
        )

    @classmethod
    def on_consumer_connection_open(cls, connection):
        """ The callback executed when consumer connection has opened. The
            callback will be passed the connection instance as its only arg.
            https://pika.readthedocs.io/en/stable/modules/connection.html """

        print(f"consumer connection opened, {connection}")
        cls.consumer_connection = connection
        cls.consumer_connection.add_on_connection_blocked_callback(
            cls.on_connection_blocked)
        cls.consumer_connection.add_on_connection_unblocked_callback(
            cls.on_connection_unblocked)
        cls.create_receiving_channel()

    @classmethod
    def create_receiving_channel(cls):
        """ This method creates the receiving channel for the consumers if
        there is a consumer connection established """

        print("Creating a receiving channel")
        if cls.consumer_connection is not None:
            try:
                cls.consumer_connection.channel(
                    channel_number=11,
                    on_open_callback=cls.on_rx_channel_open)
            except ConnectionWrongStateError:
                """raises this exception when connection is not open"""
                cls.connect_consumer()
        else:
            print('There is no open consumer connection to create a channel')
            cls.connect_consumer()

    @classmethod
    def on_rx_channel_open(cls, channel):
        """ The callback when the channel is opened. The callback will be
            invoked with the Channel instance as its only argument.
            https://pika.readthedocs.io/en/stable/modules/connection.html """

        print("Receiving channel opened")
        cls.channel_rx = channel
        cls.channel_rx.basic_qos(prefetch_count=100, global_qos=False)
        cls.channel_rx.add_on_close_callback(
            cls.on_rx_channel_closed)
        for element in CustomerInfo["Topics"]:
            cls.pub_sub.insert(
                0,
                RabbitMQSubscriber(
                    channel,
                    CustomerInfo["ExchangeName"],
                    CustomerInfo["ExchangeType"],
                    QueueName,
                    element,
                    cls.on_message
                )
            )

        if cls.channel_rx is not None:
            cls.setup_ok.set()

    @classmethod
    def on_rx_channel_closed(cls, channel: Channel, exception=None):
        """ a callback function that will be called when the channel is closed.
        The callback function will receive the channel and an exception
        describing why the channel was closed.
        https://pika.readthedocs.io/en/stable/modules/channel.html """

        print(f"Receiving channel {channel} is closed due to "
              f"exception: {exception}")
        if cls.consumer_connection.is_closed or \
                cls.consumer_connection.is_closing:
            print("doing nothing related to channel as it will be "
                        f"recreated along with the connection creation")
        else:
            cls.create_receiving_channel()

    @classmethod
    def on_consumer_connection_open_error(cls, connection: Connection,
                                          exception=None):
        """callback notification when the consumer connection can't open"""

        cls.consumer_connection = connection
        cls.channel_rx = None
        cls.pub_sub = []
        cls.setup_ok.set()
        print(f"unable to open consumer connection: {connection} with "
              f"exception: {exception}")

        cls.reconnect_consumer_connection()

    @classmethod
    def on_consumer_connection_closed(cls, connection: Connection,
                                      exception=None):
        """ callback notification when the consumer connection has closed. """

        cls.consumer_connection = connection
        cls.channel_rx = None
        cls.pub_sub = []
        print(f"Consumer connection closed, connection: {connection} "
                       f"due to exception: {exception}")
        cls.reconnect_consumer_connection()

    @staticmethod
    def on_connection_blocked(connection: Connection, frame_method):
        """ callback to be notified when the connection gets blocked
        (Connection.Blocked received from RabbitMQ) due to the broker running
        low on resources (memory or disk).
        https://pika.readthedocs.io/en/stable/modules/connection.html """

        print(f"connection: {connection} is {frame_method}")
        print("it’s a good idea for publishers receiving this "
              "notification to suspend publishing ")

    @staticmethod
    def on_connection_unblocked(connection: Connection, frame_method):
        """ a callback to be notified when the connection gets unblocked
        (Connection.Unblocked frame is received from RabbitMQ) letting
        publishers know it’s ok to start publishing again.
        https://pika.readthedocs.io/en/stable/modules/connection.html """

        print(f"connection: {connection} is {frame_method}")

    @classmethod
    def reconnect_consumer_connection(cls):
        """ This methods recreates the connection for consumers if the
        existing connection is closed or is being closed"""

        if cls.consumer_connection is None or \
                cls.consumer_connection.is_closing or \
                cls.consumer_connection.is_closed:
            print('Reconnecting! the consumer connection')
            cls.consumer_connection = cls.connect_consumer()
            print("Consumer connection was successfully reconnected")

    @classmethod
    def on_message(cls, received_channel, basic_deliver, properties, body):
        from src.services.eventThread import EventsHandler

        try:
            EventsHandler.event_handler(basic_deliver, body)
        except Exception as e:
            print(str(e))
        finally:
            received_channel.basic_ack(basic_deliver.delivery_tag)


class RabbitMQSubscriber(object):

    def __init__(self, channel, exchange_name, exchange_type, queue_name,
                 routing_key, on_message):
        self.channel: Channel = channel
        self.exchange_name = exchange_name
        self.exchange_type = exchange_type
        self.queue_name = queue_name
        self.routing_key = routing_key
        self.on_message = on_message
        self._consumer_tag = None

        self.channel.exchange_declare(callback=self.on_exchange_declare_ok,
                                      exchange=self.exchange_name,
                                      exchange_type=self.exchange_type,
                                      durable=True, auto_delete=False)

    def on_exchange_declare_ok(self, unused_frame):
        self.channel.queue_declare(
            queue=self.queue_name,
            callback=self.on_queue_declare_ok,
            durable=True
        )

    def on_queue_declare_ok(self, method_frame):
        print(f"Binding {self.exchange_name} to {self.queue_name} "
                    f"with {self.routing_key}")
        self.channel.queue_bind(callback=self.on_bind_ok,
                                queue=self.queue_name,
                                exchange=self.exchange_name,
                                routing_key=self.routing_key)

    def on_bind_ok(self, unused_frame):
        self.channel.add_on_cancel_callback(self.on_consumer_cancelled)
        self._consumer_tag = \
            self.channel.basic_consume(on_message_callback=self.on_message,
                                       queue=self.queue_name, auto_ack=False)

    def on_consumer_cancelled(self, method_frame):
        """ callback function that will be called when the basic_cancel is
        sent by the server """

        print("Consumer was cancelled remotely, shutting down: %r",
              method_frame)
        if self.channel.is_closing or self.channel.is_closed:
            print("Channel is closing or already closed")
        else:
            print("Closing connection")
            self.channel.close()
        MessageQueue.create_receiving_channel()
