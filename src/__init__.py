from flask import Flask
import asyncio
from multiprocessing import JoinableQueue
import threading
from .externalServices.database import tables
from .externalServices.database.services.database import Database
from .externalServices.messageQueue.messageQ import MessageQueue
from .externalServices.messageQueue.publisher.PublisherFactory import PublisherFactory
from . import routes
from . import services


def create_app(config):
    internal_publish_queue = JoinableQueue()

    app = Flask(__name__)
    app.config.from_object(config)
    print("CREATED APP INSTANCE!!\n\n")
    Database.init_app(app)
    print("DATABASE INITIALISED")
    tables.init_app()
    print("TABLES CREATED")
    services.init_app()
    print("VIEW INITIALIZED")
    routes.init_app(app)
    print("ROUTES INITIALISED")

    ready = threading.Event()
    app.config["SETUP_OK"] = ready

    print("Starting message queue connection thread for consumption of message..")
    mq_thread = threading.Thread(target=async_thread_message_queue,
                                 args=(app, internal_publish_queue))
    mq_thread.start()

    ready.wait()
    ready.clear()
    print("Message queue client has started")

    print("Starting publisher thread for publishing of message..")
    publisher_thread = threading.Thread(target=async_thread_message_publisher,
                                        args=(app, internal_publish_queue))
    publisher_thread.start()
    # Waits to publisher_thread setup
    ready.wait()
    ready.clear()
    print("Publisher thread has started")

    return app


def async_thread_message_queue(app, internal_publish_queue):
    """the thread runner which takes the internal queue required for publishing message as
    parameter, and then configures the rabbit mq consumer connection asynchronously via event
    loop in the called thread within the flask application context"""

    with app.app_context():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        MessageQueue.init_app(app, internal_publish_queue)
        loop.run_forever()


def async_thread_message_publisher(app, internal_publish_queue):
    """the thread runner which takes the internal queue required for publishing message as
    parameter, and then configures the rabbit mq publisher connection asynchronously via
    event loop in the called thread within the flask application context"""

    with app.app_context():
        loop = asyncio.new_event_loop()
        publisher_factory_instance = PublisherFactory(app, internal_publish_queue)
        loop.create_task(publisher_factory_instance.init(loop))
        asyncio.set_event_loop(loop)
        loop.run_forever()
        return publisher_factory_instance
