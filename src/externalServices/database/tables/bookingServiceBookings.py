from dataclasses import dataclass
import datetime as dt

from ..services.database import Database
from sqlalchemy.exc import IntegrityError


@dataclass
class BookingsParameter(object):
    """
    Auxiliary class to handle the high amount of class parameters.
    """
    customer_id: str
    service_provider_id: str
    customer_name: str
    service_provider_name: str
    start: str
    end: str


class Bookings(Database.get_db().Model):
    __tablename__ = "BookingServiceBookings"
    BookingID = Database.get_db().Column(
        Database.get_db().Integer(),
        autoincrement=True,
        nullable=False,
        primary_key=True
    )
    CustomerID = Database.get_db().Column(
        Database.get_db().String(255),
        nullable=False
    )
    ServiceProviderID = Database.get_db().Column(
        Database.get_db().String(255),
        nullable=False
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

    def __init__(self, customer_id, service_provider_id, customer_name, service_provider_name, start, end):
        self.CustomerID = customer_id
        self.ServiceProviderID = service_provider_id
        self.UserName = customer_name
        self.ServiceProviderName = service_provider_name
        self.Start = start
        self.End = end

    @staticmethod
    def save(customer_id, service_provider_id, customer_name, service_provider_name, start, end):
        bookings = Bookings(customer_id, service_provider_id, customer_name,
                            service_provider_name, start, end)
        bookings._create()

    def _create(self):
        try:
            with Database.session_manager() as session:
                session.add(self)
        except Exception:
            print(f"[DB] Failed to create in: {self.__tablename__}")

    @classmethod
    def get_bookings(cls, customer_id):
        with Database.session_manager() as session:
            all_bookings = session.query(Bookings).filter(
                Bookings.CustomerID == customer_id).all()
            session.expunge_all()
            return {'Bookings': list(x.json() for x in all_bookings)}

    @classmethod
    def get_service_provider_bookings(cls, service_provider_id):
        with Database.session_manager() as session:
            all_bookings = session.query(Bookings).filter(
                Bookings.ServiceProviderID == service_provider_id).all()
            session.expunge_all()
            return {'Bookings': list(x.json() for x in all_bookings)}

    def json(self):
        return {
            "UserName": self.UserName,
            "ServiceProviderName": self.ServiceProviderName,
            "Start": self.Start,
            "End": self.End
        }

    @staticmethod
    def init_app():
        print("[DB] Booking initialisation done")
