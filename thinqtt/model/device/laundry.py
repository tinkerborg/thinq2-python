from dataclasses import field
from marshmallow_dataclass import dataclass

from thinqtt.schema import CamelCaseSchema

from .base import Device


@dataclass(base_schema=CamelCaseSchema)
class LaundryDevice(Device):
    state: dict = field(metadata=dict(data_key="washerDryer"))
