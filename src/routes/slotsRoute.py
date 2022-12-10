from flask.views import MethodView
from flask import request, jsonify

from ..externalServices.database.tables.bookingServiceSlots import Slot
from ..externalServices.database.tables.bookingServiceBookings import Bookings


class SlotsRoutes(MethodView):
    def get(self, service_provider_id):
        print(f"Received get slots {service_provider_id}")
        try:
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
            return jsonify(message="success"), 200
        except Exception:
            print(f"[Routes] failed to add slots", Exception)
            return jsonify(error=f"failed to add slots for service provider"), 400

    def post(self, service_provider_id):
        print(f"Received update slots {service_provider_id}")
        try:
            received = request.json
            result = Slot.update(received["ID"], received["Booked"])
            if received["Booked"]:
                Bookings.save(received["CustomerID"], result["ServiceProviderID"], received["CustomerName"],
                              result["ServiceProviderName"], result["Start"], result["End"])
            return jsonify(message="success"), 200
        except Exception:
            print(f"[Routes] failed to add slots", Exception)
            return jsonify(error=f"failed to add slots for service provider"), 400
