from dataclasses import dataclass
import datetime as dt

from ..services.database import Database


@dataclass
class SlotParameter(object):
    """
    Auxiliary class to handle the high amount of class parameters.
    """
    user_id: str
    user_name: str
    start: dt.datetime
    end: dt.datetime
    booked: bool


class Slot(Database.get_db().Model):
    __tablename__ = "BookingServiceSlots"
    ID = Database.get_db().Column(
        Database.get_db().Integer(),
        autoincrement=True,
        nullable=False,
        primary_key=True
    )
    UserID = Database.get_db().Column(
        Database.get_db().String(255),
        nullable=False,
        unique=True
    )
    UserName = Database.get_db().Column(
        Database.get_db().String(255),
        nullable=False
    )
    Start = Database.get_db().Column(
        Database.get_db().Time(),
        nullable=False)
    End = Database.get_db().Column(
        Database.get_db().Time(),
        nullable=False)
    Booked = Database.get_db().Column(
        Database.get_db().Boolean(),
        nullable=False)

    def __init__(self, UserID, UserName, Start, End, Booked=False):
        self.UserID = UserID
        self.UserName = UserName
        self.Start = Start
        self.End = End
        self.Booked = Booked

    @staticmethod
    def init_app():
        print("[DB] Slot initialisation done")
