import asyncio
import json
from asyncio import AbstractEventLoop
from multiprocessing.queues import JoinableQueue
from src.externalServices.messageQueue.publisher import Publisher
from src.externalServices.messageQueue.models.publishMessageModel import PublishMessageModel

MESSAGE_QUEUE_URI = ""


class PublisherFactory:
    """ Maintains and retries publisher connection """
    _publisher: Publisher
    _internal_publish_queue: JoinableQueue
    _tries = 0
    _loop: AbstractEventLoop
    is_ready: any

    def __init__(self, app, internal_publish_queue):
        self._internal_publish_queue = internal_publish_queue
        self._tries = 0
        self.is_ready = app.config.get("SETUP_OK", None)

        global MESSAGE_QUEUE_URI
        MESSAGE_QUEUE_URI = app.config.get("MESSAGE_QUEUE_URI")

    async def init(self, loop: AbstractEventLoop):
        """ Setups publisher factory """
        self.connect_publisher()
        asyncio.ensure_future(self.look_for_message(), loop=loop)
        self._loop = loop

    def connect_publisher(self):
        """Connects publisher with retry"""
        self._tries += 1
        print(f"Connecting to {MESSAGE_QUEUE_URI} for consumer connection")
        self._publisher = Publisher(connection_url=MESSAGE_QUEUE_URI,
                                    on_error_callback=self.on_publisher_error)
        self.is_ready.set()

    def on_publisher_error(self, _message):
        """Handles publisher error and call reconnect"""
        PUBLISHER_RECONNECTION_TIMEOUT = 5
        print(f"[PublisherFactory] [Retry] {self._tries} publisher connection was "
              f"broken retrying after {PUBLISHER_RECONNECTION_TIMEOUT}"
              f" seconds")
        self._loop.call_later(PUBLISHER_RECONNECTION_TIMEOUT,
                              self.connect_publisher)

    async def look_for_message(self, force_exit_after_try=None):
        """ Handles publisher error and call reconnect """
        try_count_main = 1
        hard_true = True
        MESSAGE_PUBLISH_INTERVAL = 10
        while hard_true and not force_exit_after_try == try_count_main:
            try:
                try_count = 1
                if self._publisher.is_open and self._publisher.publisher_channel.is_open:
                    while not self._internal_publish_queue.empty() and \
                            not force_exit_after_try == try_count:
                        message_data: PublishMessageModel = \
                            self._internal_publish_queue.get(False)
                        self._publisher.publish_message(message_data.exchange,
                                                        message_data.routing_key,
                                                        json.dumps(message_data.body),
                                                        message_data.mandatory)
                        try_count += 1
                else:
                    print(
                        "[PublisherFactory] publisher not ready waiting for publisher connection "
                        "all new publish message will be stacked in publish queue")

            except Exception:
                """ Do not remove this  exception as Asyncio will exit by default if Exception 
                occurred in above code  """
                print("[PublisherFactory] Terrible error occurred in publishing")
            try_count_main += 1
            await asyncio.sleep(MESSAGE_PUBLISH_INTERVAL)
