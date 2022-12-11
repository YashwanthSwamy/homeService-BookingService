from dataclasses import dataclass
import datetime as dt

from ..services.database import Database


@dataclass
class SlotParameter(object):
    """
    Auxiliary class to handle the high amount of class parameters.
    """
    customer_id: str
    user_name: str
    start: str
    end: str
    booked: bool


class Slot(Database.get_db().Model):
    __tablename__ = "BookingServiceSlots"
    ID = Database.get_db().Column(
        Database.get_db().Integer(),
        autoincrement=True,
        nullable=False,
        primary_key=True
    )
    ServiceProviderID = Database.get_db().Column(
        Database.get_db().String(255),
        nullable=False,
        unique=True
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
    Booked = Database.get_db().Column(
        Database.get_db().Boolean(),
        nullable=False)

    def __init__(self, service_provider_id, service_provider_name, start, end, booked):
        self.ServiceProviderID = service_provider_id
        self.ServiceProviderName = service_provider_name
        self.Start = start
        self.End = end
        self.Booked = booked

    def _create(self):
        try:
            with Database.session_manager() as session:
                session.add(self)
        except Exception:
            print(f"[DB] Failed to create in: {self.__tablename__}")

    @staticmethod
    def save(service_provider_id, service_provider_name, start, end, booked):
        customer_info = Slot(service_provider_id, service_provider_name, start, end, booked)
        customer_info._create()

    @staticmethod
    def update(id, booked):
        try:
            with Database.session_manager() as session:
                slot = session.query(Slot).filter(
                    Slot.ID == id).first()
                slot.Booked = booked
                session.add(slot)
                return slot.json()
        except Exception:
            print(f"[DB] Failed to update")

    @classmethod
    def get_slots(cls, service_provider_id = None):
        with Database.session_manager() as session:
            if service_provider_id is not None:
                slots = session.query(Slot).filter(
                    Slot.ServiceProviderID == service_provider_id).all()
                session.expunge_all()
                return {'Slots': list(x.json() for x in slots)}
            slots = session.query(Slot).all()
            session.expunge_all()
            return {'Slots': list(x.json() for x in slots)}

    def json(self):
        return {
            "ID": self.ID,
            "ServiceProviderID": self.ServiceProviderID,
            "ServiceProviderName": self.ServiceProviderName,
            "Start": self.Start,
            "End": self.End,
            "Booked": self.Booked
        }

    @staticmethod
    def init_app():
        print("[DB] Slot initialisation done")
