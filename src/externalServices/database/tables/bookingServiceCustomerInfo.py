from dataclasses import dataclass

from ..services.database import Database


@dataclass
class CustomerInfoParameter(object):
    """
    Auxiliary class to handle the high amount of class parameters.
    """
    customer_id: str
    user_name: str
    service_provided: str


class CustomerInfo(Database.get_db().Model):
    __tablename__ = "BookingServiceCustomerInfo"
    CustomerID = Database.get_db().Column(
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

    def __init__(self, customer_id, user_name, service_provided):
        self.CustomerID = customer_id
        self.UserName = user_name
        self.Service_Provided = service_provided

    def _create(self):
        try:
            with Database.session_manager() as session:
                session.add(self)
        except Exception:
            print(f"[DB] Failed to create in: {self.__tablename__}")

    @staticmethod
    def save(customer_id, customer_name, service_provided):
        print("create customer")
        customer_info = CustomerInfo(customer_id, customer_name, service_provided)
        customer_info._create()

    @classmethod
    def get_customer_info(cls, customer_id):
        with Database.session_manager() as session:
            customer_info = session.query(CustomerInfo).filter(
                CustomerInfo.CustomerID == customer_id).first()
            session.expunge_all()
            return customer_info.json()

    def json(self):
        return {
            "CustomerID": self.CustomerID,
            "UserName": self.UserName,
            "Service_Provided": self.Service_Provided,
        }

    @staticmethod
    def init_app():
        print("[DB] Customer Info initialisation done")
