from flask.views import MethodView
from flask import request, jsonify
from datetime import datetime

from ..externalServices.database.tables.bookingServiceSlots import Slot
from ..externalServices.database.tables.bookingServiceBookings import Bookings
from ..externalServices.messageQueue.services.eventThread import EventsHandler


class SlotsRoutes(MethodView):
    def get(self, service_provider_id):
        print(f"Received get slots {service_provider_id}")
        try:
            read_value = request.args.get('ServiceProviderID', default=None)
            if read_value is not None:
                result = Slot.get_slots(read_value)
                return jsonify(result), 200
            result = Slot.get_slots()
            return jsonify(result), 200
        except Exception:
            print(f"[ROUTES] Non-existent slots")
            return jsonify(error=f"failed to fetch slots for customer"), 400

    def put(self, service_provider_id):
        print(f"Received add slot {service_provider_id}")
        try:
            received = request.json
            Slot.save(service_provider_id, received["ServiceProviderName"], received["Start"],
                      received["End"], received["Booked"])
            EventsHandler.send_slot_info(service_provider_id, received["ServiceProviderName"])
            return jsonify(message="success"), 200
        except Exception:
            print(f"[Routes] failed to add slots", Exception)
            return jsonify(error=f"failed to add slots for service provider"), 400

    def post(self, service_provider_id):
        print(f"Received update slots {service_provider_id}")
        try:
            customer_id = service_provider_id
            received = request.json
            result = Slot.update(received["ID"], received["Booked"])
            print("result", result)
            if received["Booked"]:
                Bookings.save(customer_id, result["ServiceProviderID"], received["CustomerName"],
                              result["ServiceProviderName"], str(datetime.isoformat(result["Start"])+"Z"),
                              str(datetime.isoformat(result["End"]))+"Z")

                EventsHandler.send_booking_info(customer_id, result["ServiceProviderID"],
                                                received["CustomerName"], result["ServiceProviderName"])
            return jsonify(message="success"), 200
        except Exception:
            print(f"[Routes] failed to update slots", Exception)
            return jsonify(error=f"failed to update slots for service provider"), 400
