from dataclasses import dataclass
import datetime as dt

from ..services.database import Database


@dataclass
class BookingsParameter(object):
    """
    Auxiliary class to handle the high amount of class parameters.
    """
    customer_name: str
    service_provider_name: str
    start: dt.datetime
    end: dt.datetime


class Bookings(Database.get_db().Model):
    __tablename__ = "BookingServiceBookings"
    BookingID = Database.get_db().Column(
        Database.get_db().Integer(),
        autoincrement=True,
        nullable=False,
        primary_key=True
    )
    UserName = Database.get_db().Column(
        Database.get_db().String(255),
        nullable=False
    )
    ServiceProviderName = Database.get_db().Column(
        Database.get_db().String(255),
        nullable=False
    )
    Start = Database.get_db().Column(
        Database.get_db().DateTime(),
        nullable=False)
    End = Database.get_db().Column(
        Database.get_db().DateTime(),
        nullable=False)

    def __init__(self, UserName, Start, End, ServiceProviderName):
        self.UserName = UserName
        self.ServiceProviderName = ServiceProviderName
        self.Start = Start
        self.End = End

    @staticmethod
    def init_app():
        print("[DB] Booking initialisation done")
