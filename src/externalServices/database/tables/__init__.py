from .bookingServiceCustomerInfo import CustomerInfo
from .bookingServiceSlots import Slot
from .bookingServiceBookings import Bookings


def init_app():
    """
    Load models to them get loaded with the correct db "session"
    """
    CustomerInfo.init_app()
    Slot.init_app()
    Bookings.init_app()
