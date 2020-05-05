from marshmallow_dataclass import dataclass

from thinqtt.schema import CamelCaseSchema

from .base import Device


@dataclass(base_schema=CamelCaseSchema)
class LaundryDevice(Device):
    washer_dryer: dict
