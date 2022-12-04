from typing import Callable

from pika import BasicProperties
from pika.connection import Connection

from src.externalServices.messageQueue.constants import MessageQChannels
from src.externalServices.messageQueue.exceptions import PublishMessageError
from src.externalServices.messageQueue import Connection as MessageQConnection
from ..publisher.ChannelInitializer import ChannelInitializer


class Publisher(MessageQConnection):
    """ inherits MessageQConnection and setups publisher connection """

    publisher_connection: Connection
    publisher_channel: ChannelInitializer
    error: Callable

    def __init__(self,
                 connection_url: str,
                 on_error_callback: Callable):
        super().__init__(connection_url,
                         MessageQChannels.BOOKING_PUBLISHER_CONNECTION,
                         self._on_publisher_connection_open,
                         self._on_publisher_connection_open_error,
                         self._on_publisher_connection_closed
                         )
        self.error = on_error_callback
        print("[RQ] TX opening publisher connection...")

    def publisher_error(self, message):
        self.error(message)

    def _on_publisher_connection_open(self, connection: Connection):
        """ The callback executed when publisher connection has opened. The
        callback will be passed the connection instance as its only arg.
        https://pika.readthedocs.io/en/stable/modules/connection.html """

        print(f"[RQ] TX publisher connection opened...")
        self.publisher_connection = connection
        self.add_on_connection_blocked_callback(
            self._on_publisher_connection_blocked)
        self.add_on_connection_unblocked_callback(
            self._on_publisher_connection_unblocked)

        self.publisher_channel = ChannelInitializer(on_error_callback=self.publisher_error,
                                                    connection=self.publisher_connection)

    def _on_publisher_connection_open_error(self, connection: Connection,
                                            exception=None):
        """callback notification when the publisher connection can't open
        https://pika.readthedocs.io/en/stable/modules/connection.html """

        self.publisher_connection = connection

        print(f"[RQ] TX unable to open publisher connection: {connection} "
                       f"with exception: {str(exception)}")
        self.publisher_error("[RQ] TX unable to open publisher connection")

    def _on_publisher_connection_closed(self, connection: Connection,
                                        exception=None):
        """ callback notification when the publisher connection has closed. """
        self.publisher_connection = connection
        msg = f"[RQ] TX Publisher connection closed, connection: " \
              f"{connection} due to exception: {exception}"
        print(msg)
        self.publisher_error(msg)

    def _on_publisher_connection_blocked(self, connection: Connection, frame_method):
        """ callback to be notified when the connection gets blocked
        (Connection.Blocked received from RabbitMQ) due to the broker running
        low on resources (memory or disk).
        https://pika.readthedocs.io/en/stable/modules/connection.html """

        print(f"[RQ] TX connection: {connection} is {frame_method}")
        print("[RQ] TX it’s a good idea for publishers receiving this "
                       "notification to suspend publishing ")

    def _on_publisher_connection_unblocked(self, connection: Connection, frame_method):
        """ a callback to be notified when the connection gets unblocked
        (Connection.Unblocked frame is received from RabbitMQ) letting
        publishers know it’s ok to start publishing again.
        https://pika.readthedocs.io/en/stable/modules/connection.html """
        print(f"[RQ] TX connection: {connection} is {frame_method}")

    def publish_message(self, exchange, routing_key, body, properties=None,
                        mandatory=False):
        """
        publishing messages to provided MessageQ exchanges and routing keys
        with retry mechanism support
        """
        if properties is None:
            properties = BasicProperties(delivery_mode=2)
        elif isinstance(properties, BasicProperties) and \
                properties.delivery_mode != 2:
            properties.delivery_mode = 2
        try:
            self.publisher_channel.publish(
                exchange=exchange,
                routing_key=routing_key,
                body=body,
                properties=properties,
                mandatory=mandatory
            )
            print(f"[RQ] TX message published to exchange successfully")
            return "ok"
        except Exception as e:
            print(f"[RQ] TX message could be published due to exception: {e}")
            raise PublishMessageError from e
