from marshmallow_dataclass import dataclass

from thinqtt.schema import CamelCaseSchema


@dataclass(base_schema=CamelCaseSchema)
class DeviceStatic:
    device_type: int
    country_code: str


@dataclass(base_schema=CamelCaseSchema)
class Device:
    timestamp: float
    static: DeviceStatic
