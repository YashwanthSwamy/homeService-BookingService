from logging import getLogger
from pika.channel import Channel
from pika.connection import Connection

from src.externalServices.messageQueue.constants import MessageQExchanges, MessageQExchangesTypes

Logger = getLogger(__name__)


class ChannelInitializer:
    """ Initializes all channel related setup for publisher """
    _channel_tx = None
    _is_ready = False
    _publisher_connection: Connection
    error: callable

    @property
    def is_open(self):
        return self._is_ready

    def __init__(self, on_error_callback: callable, connection: Connection):
        Logger.info("[RQ] TX creating channel...")
        self._publisher_connection = connection
        self.error = on_error_callback
        self.create_transmission_channel()

    def close_transmission_channel(self):
        """ Invoke this command to close the channel with RabbitMQ by sending
            the Channel.Close
        """
        if self._channel_tx is not None:
            Logger.info('[RQ] TX Closing the channel')
            self._channel_tx.close()
            self._is_ready = False

    def create_transmission_channel(self):
        """ This method creates the transmission channel for the producer if
        there is a producer connection established """
        if self._publisher_connection is not None and not self._publisher_connection.is_closed:
            self._publisher_connection.channel(
                channel_number=10,
                on_open_callback=self.on_tx_channel_open)
        else:
            msg = "[RQ] TX There is no open publisher connection connection to create a channel"
            Logger.error(msg)
            self.error(msg)

    def on_tx_channel_open(self, channel):
        """ The callback when the channel is opened. The callback will be
        invoked with the Channel instance as its only argument.
        https://pika.readthedocs.io/en/stable/modules/connection.html """

        Logger.info("[RQ] TX Transmission channel opened...")
        self._channel_tx = channel
        try:
            self._channel_tx.add_on_close_callback(self.on_tx_channel_closed)

            self._channel_tx.exchange_declare(exchange=MessageQExchanges.COLLECTED,
                                              exchange_type=MessageQExchangesTypes.TOPIC,
                                              durable=True, auto_delete=False)
            self._channel_tx.exchange_declare(exchange=MessageQExchanges.EVENTS,
                                              exchange_type=MessageQExchangesTypes.TOPIC,
                                              durable=True, auto_delete=False)
            # Enabled delivery confirmations
            # self._channel_tx.confirm_delivery()
            self._is_ready = True
            Logger.info(f"[RQ] TX channel created successfully")
        except Exception as e:
            msg = f"[RQ] TX failed to create channels, {e}"
            Logger.error(msg)
            self.error(msg)

    def on_tx_channel_closed(self, channel: Channel, exception=None):
        """ a callback function that will be called when the channel is closed.
        The callback function will receive the channel and an exception
        describing why the channel was closed.
        https://pika.readthedocs.io/en/stable/modules/channel.html """

        Logger.warning(f"[RQ] TX Channel {channel} is closed due to "
                       f"exception: {exception}")
        if self._publisher_connection.is_closed or \
                self._publisher_connection.is_closing:
            Logger.info(f"[RQ] TX New Channel will be created along with the connection")
        else:
            self._is_ready = False
            Logger.info(f"[RQ] TX Channel was closed without calling connection close"
                        f"Trying to create the channel again")
            self.create_transmission_channel()

    def publish(self, **kwargs):
        self._channel_tx.basic_publish(**kwargs)
