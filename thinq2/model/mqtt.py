from marshmallow_dataclass import dataclass

from thinq2.model.auth import ThinQSession
from thinq2.model.common import Route
from thinq2.model.thinq import IOTRegistration


@dataclass
class MQTTConfiguration:
    auth: ThinQSession
    route: Route
    registration: IOTRegistration
    ca_cert: str
    private_key: str
    csr: str
