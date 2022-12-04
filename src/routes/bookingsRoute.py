from flask.views import MethodView
from flask import jsonify


class BookingsRoutes(MethodView):
    """

    """

    def get(self):
        """"""
        print("Received get all bookings")
        return jsonify(message="Hello Bro"), 200
