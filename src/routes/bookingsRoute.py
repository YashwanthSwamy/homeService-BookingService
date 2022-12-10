from flask.views import MethodView
from flask import request, jsonify

from src.externalServices.database.tables.bookingServiceBookings import Bookings


class BookingsRoutes(MethodView):
    def get(self, customer_id):
        print(f"Received get bookings {customer_id}")
        try:
            read_value = request.args.get('ServiceProviderID', default=None)
            if read_value is not None:
                result = Bookings.get_service_provider_bookings(read_value)
                return jsonify(result), 200
            result = Bookings.get_bookings(customer_id)
            return jsonify(result), 200
        except Exception:
            print(f"[ROUTES] Non-existent bookings for : {customer_id}")
            return jsonify(error=f"failed to fetch bookings for customer"), 400

    def put(self, customer_id):
        print(f"Received add booking {customer_id}")
        try:
            received = request.json
            Bookings.save(customer_id, received["ServiceProviderID"], received["CustomerName"],
                          received["ServiceProviderName"], received["Start"], received["End"])
            return jsonify(message="success"), 200
        except Exception:
            print(f"[Routes] failed to add bookings", Exception)
            return jsonify(error=f"failed to add booking for customer"), 400
