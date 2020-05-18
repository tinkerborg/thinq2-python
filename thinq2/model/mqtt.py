from datetime import datetime
from dataclasses import field

from marshmallow_dataclass import dataclass

from thinq2.model.common import Route
from thinq2.model.thinq import IOTRegistration
from thinq2.schema import CamelCaseSchema


@dataclass
class MQTTConfiguration:
    route: Route
    registration: IOTRegistration
    ca_cert: str
    private_key: str
    csr: str


@dataclass
class MQTTMessageDeviceState:
    desired: dict = field(default_factory=dict)
    reported: dict = field(default_factory=dict)


@dataclass(base_schema=CamelCaseSchema)
class MQTTMessageDeviceData:
    state: MQTTMessageDeviceState


@dataclass(base_schema=CamelCaseSchema)
class MQTTMessage:
    device_id: str
    message_type: str = field(metadata=dict(data_key="type"))
    data: MQTTMessageDeviceData
    timestamp: datetime = None
