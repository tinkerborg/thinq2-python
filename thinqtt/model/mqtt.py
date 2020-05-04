from marshmallow_dataclass import dataclass

from thinqtt.model.auth import ThinQTTSession
from thinqtt.model.common import Route
from thinqtt.model.thinq import IOTRegistration


@dataclass
class MQTTConfiguration:
    auth: ThinQTTSession
    route: Route
    registration: IOTRegistration
    ca_cert: str
    private_key: str
    csr: str
