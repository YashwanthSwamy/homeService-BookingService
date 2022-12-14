from typing import Dict
from multiprocessing import JoinableQueue
import json

from src.externalServices.database.tables import CustomerInfo
from src.externalServices.messageQueue.messageQ import CustomerInfoMessages
from src.externalServices.messageQueue.models.publishMessageModel import PublishMessageModel


class EventsHandler:
    terminate_request = False
    message_handlers = {}
    internal_publish_queue: JoinableQueue

    @classmethod
    def init_app(cls, internal_publish_queue: JoinableQueue):

        cls.internal_publish_queue = internal_publish_queue
        cls.configure_message_handlers()
        print(f"{__name__} has been initialized")

    @classmethod
    def push_to_internal_queue(cls, exchange: str, routing_key: str, body: Dict):
        try:
            print("publishing message!!")
            message = PublishMessageModel(exchange, routing_key, body, None)
            cls.internal_publish_queue.put(message)
        except Exception:
            print("failed to publish message as internal queue is not available")

    @classmethod
    def event_handler(cls, basic_deliver, body):
        message_in = ''
        routing_key = ''
        try:
            routing_key = basic_deliver.routing_key
            message_in = json.loads(body.decode())
            if basic_deliver.routing_key in cls.message_handlers:
                cls.message_handlers[routing_key](routing_key, message_in)
            else:
                print(f"[RQ] unknown routing key: {routing_key}, for: {body}")
        except json.decoder.JSONDecodeError:
            print("[RQ] Error decoding JSON of incoming message for "
                         f"routing key: {routing_key}")

    @classmethod
    def configure_message_handlers(cls):
        cls.message_handlers = {
            "event.customer.created": cls.on_customer_created,
        }

    @classmethod
    def on_customer_created(cls, routing_key, message_in):
        print("customer created message received")
        print(f"[RQ] charger connected: {routing_key}, {message_in}")
        customer_id = message_in.get("customerId", "")
        customer_name = message_in.get("name", "")
        service_provided = message_in.get("offeredService", "")
        if service_provided is not None:
            CustomerInfo.save(customer_id, customer_name, service_provided)

    @classmethod
    def send_slot_info(cls, service_provider_id, service_provider_name):
        """
        """
        print("send_slot_info")
        exchange = CustomerInfoMessages["ExchangeName"]
        routing_key = "event.booking.slot"
        body = {
            "ServiceProviderID": service_provider_id,
            "ServiceProviderName": service_provider_name
        }
        cls.push_to_internal_queue(exchange, routing_key, body)

    @classmethod
    def send_booking_info(cls, customer_id, service_provider_id, customer_name, service_provider_name):
        """
        """
        print("send_booking_info")
        exchange = CustomerInfoMessages["ExchangeName"]
        routing_key = "event.booking.booked"
        body = {
            "CustomerID": customer_id,
            "ServiceProviderID": service_provider_id,
            "CustomerName": customer_name,
            "ServiceProviderName": service_provider_name
        }
        cls.push_to_internal_queue(exchange, routing_key, body)
