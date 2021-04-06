from .base import Device
from .laundry import LaundryDevice

device_types = {
    201: LaundryDevice,
    202: LaundryDevice,
    # REFRIGERATOR = 101
    # KIMCHI_REFRIGERATOR = 102
    # WATER_PURIFIER = 103
    # WASHER = 201
    # DRYER = 202
    # STYLER = 203
    # DISHWASHER = 204
    # TOWER_WASHER = 221
    # TOWER_DRYER = 222
    # OVEN = 301
    # MICROWAVE = 302
    # COOKTOP = 303
    # HOOD = 304
    # AC = 401
    # AIR_PURIFIER = 402
    # DEHUMIDIFIER = 403
    # ROBOT_KING = 501
    # TV = 701
    # BOILER = 801
    # SPEAKER = 901
    # HOMEVU = 902
    # ARCH = 1001
    # MISSG = 3001
    # SENSOR = 3002
    # SOLAR_SENSOR = 3102
    # IOT_LIGHTING = 3003
    # IOT_MOTION_SENSOR = 3004
    # IOT_SMART_PLUG = 3005
    # IOT_DUST_SENSOR = 3006
    # EMS_AIR_STATION = 4001
    # AIR_SENSOR = 4003
    # PURICARE_AIR_DETECTOR = 4004
    # V2PHONE = 6001
    # HOMEROBOT = 9000
    # UNKNOWN = STATE_OPTIONITEM_UNKNOWN
}
