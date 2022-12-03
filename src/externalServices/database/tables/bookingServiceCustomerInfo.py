from dataclasses import dataclass

from ..services.database import Database


@dataclass
class CustomerInfoParameter(object):
    """
    Auxiliary class to handle the high amount of class parameters.
    """
    user_id: str
    user_name: str
    service_provided: str


class CustomerInfo(Database.get_db().Model):
    __tablename__ = "BookingServiceSCustomerInfo"
    UserID = Database.get_db().Column(
        Database.get_db().String(255),
        nullable=False,
        unique=True,
        primary_key=True
    )
    UserName = Database.get_db().Column(
        Database.get_db().String(255),
        nullable=False
    )
    Service_Provided = Database.get_db().Column(
        Database.get_db().String(255),
        nullable=True
    )

    def __init__(self, UserID, UserName, Service_Provided):
        self.UserID = UserID
        self.UserName = UserName
        self.Service_Provided = Service_Provided

    @staticmethod
    def init_app():
        print("[DB] Customer Info initialisation done")
