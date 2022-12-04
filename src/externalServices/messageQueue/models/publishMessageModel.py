from dataclasses import dataclass
from typing import List, Dict


@dataclass
class PublishMessageModel(object):
    """the data class which defines the structure in which object is frame to pass into the
    publish queue to get published to rabbitmq"""

    exchange: str
    routing_key: str
    body: Dict
    mandatory: bool or None