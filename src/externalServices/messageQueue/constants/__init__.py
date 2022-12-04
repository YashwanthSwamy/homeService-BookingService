from types import SimpleNamespace

MessageQEvents = SimpleNamespace(
    EVENT_CUSTOMER_CREATED="event.customer.created",
)

MessageQQueues = SimpleNamespace(
    BOOKING_SERVICE_QUEUE="BookingServiceQueue"
)
MessageQExchanges = SimpleNamespace(
    COLLECTED="collected",
    EVENTS="events",
)

MessageQExchangesTypes = SimpleNamespace(
    TOPIC="topic",
)

MessageQChannels = SimpleNamespace(
    BOOKING_PUBLISHER_CONNECTION="booking-publisher-connection"
)