from .bookingsRoute import BookingsRoutes
from .slotsRoute import SlotsRoutes
from .customerInfoRoute import CustomerInfoRoutes


def load_config_routes(app):
    app.add_url_rule("/api/v1/booking/all-bookings",
                     view_func=BookingsRoutes.as_view("bookings_api"))
    app.add_url_rule("/api/v1/booking/customerInfo",
                     view_func=CustomerInfoRoutes.as_view("customerInfo_api"))
    app.add_url_rule("/api/v1/booking/slots",
                     view_func=SlotsRoutes.as_view("slots_api"))
