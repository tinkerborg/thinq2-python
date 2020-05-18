from marshmallow_dataclass import dataclass

from thinq2.model.auth import ThinQSession
from thinq2.model.mqtt import MQTTConfiguration


@dataclass
class ThinQConfiguration:
    auth: ThinQSession
    mqtt: MQTTConfiguration
