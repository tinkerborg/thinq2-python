from enum import Enum
from dataclasses import field
from typing import List

from marshmallow import Schema, fields, post_load
from marshmallow_dataclass import dataclass
from marshmallow_enum import EnumField

from thinqtt.schema import CamelCaseSchema
from thinqtt.model.device import Device, device_types


@dataclass(base_schema=CamelCaseSchema)
class DeviceDescriptor:
    device_id: str
    model_name: str
    device_type: int
    alias: str
    model_country_code: str
    country_code: str
    fw_ver: str
    image_file_name: str
    image_url: str
    small_image_url: str
    ssid: str
    mac_address: str
    network_type: str
    timezone_code: str
    timezone_code_alias: str
    utc_offset: int
    utc_offset_display: str
    dst_offset: int
    dst_offset_display: str
    cur_offset: int
    cur_offset_display: str
    new_reg_yn: str
    remote_control_type: str
    user_no: str
    model_json_ver: float
    model_json_uri: str
    app_module_ver: float
    app_module_uri: str
    app_restart_yn: str
    app_module_size: float
    lang_pack_product_type_ver: float
    lang_pack_product_type_uri: str
    device_state: str
    online: bool
    area: int
    reg_dt: float
    blackbox_yn: bool
    model_protocol: str
    order: int
    dr_service_yn: str
    guide_type_yn: str
    guide_type: str
    reg_dt_utc: str
    groupable_yn: str
    controllable_yn: str
    combined_product_yn: str
    master_yn: str
    tclcount: int
    snapshot: Device

    class Meta(CamelCaseSchema.Meta):
        polymorph = dict(snapshot=lambda x: device_types.get(x.device_type))


@dataclass(base_schema=CamelCaseSchema)
class DeviceCollection:
    items: List[DeviceDescriptor] = field(metadata=dict(data_key="item"))


@dataclass(base_schema=CamelCaseSchema)
class IOTRegistration:
    certificate_pem: str
    subscriptions: List[str]


class ThinQResultCode(Enum):
    OK = "0000"
    PARTIAL_OK = "0001"
    OPERATION_IN_PROGRESS_DEVICE = "0103"
    PORTAL_INTERWORKING_ERROR = "0007"
    PROCESSING_REFRIGERATOR = "0104"
    RESPONSE_DELAY_DEVICE = "0111"
    SERVICE_SERVER_ERROR = "8107"
    SSP_ERROR = "8102"
    TIME_OUT = "9020"
    WRONG_XML_OR_URI = "9000"

    AWS_IOT_ERROR = "8104"
    AWS_S3_ERROR = "8105"
    AWS_SQS_ERROR = "8106"
    BASE64_DECODING_ERROR = "9002"
    BASE64_ENCODING_ERROR = "9001"
    CLIP_ERROR = "8103"
    CONTROL_ERROR_REFRIGERATOR = "0105"
    CREATE_SESSION_FAIL = "9003"
    DB_PROCESSING_FAIL = "9004"
    DM_ERROR = "8101"
    DUPLICATED_ALIAS = "0013"
    DUPLICATED_DATA = "0008"
    DUPLICATED_LOGIN = "0004"
    EMP_AUTHENTICATION_FAILED = "0102"
    ETC_COMMUNICATION_ERROR = "8900"
    ETC_ERROR = "9999"
    EXCEEDING_LIMIT = "0112"
    EXPIRED_CUSTOMER_NUMBER = "0119"
    EXPIRES_SESSION_BY_WITHDRAWAL = "9005"
    FAIL = "0100"
    INACTIVE_API = "8001"
    INSUFFICIENT_STORAGE_SPACE = "0107"
    INVAILD_CSR = "9010"
    INVALID_BODY = "0002"
    INVALID_CUSTOMER_NUMBER = "0118"
    INVALID_HEADER = "0003"
    INVALID_PUSH_TOKEN = "0301"
    INVALID_REQUEST_DATA_FOR_DIAGNOSIS = "0116"
    MISMATCH_DEVICE_GROUP = "0014"
    MISMATCH_LOGIN_SESSION = "0114"
    MISMATCH_NONCE = "0006"
    MISMATCH_REGISTRED_DEVICE = "0115"
    MISSING_SERVER_SETTING_INFORMATION = "9005"
    NOT_AGREED_TERMS = "0110"
    NOT_CONNECTED_DEVICE = "0106"
    NOT_CONTRACT_CUSTOMER_NUMBER = "0120"
    NOT_EXIST_DATA = "0010"
    NOT_EXIST_DEVICE = "0009"
    NOT_EXIST_MODEL_JSON = "0117"
    NOT_REGISTERED_SMART_CARE = "0121"
    NOT_SUPPORTED_COMMAND = "0012"
    NOT_SUPPORTED_COUNTRY = "8000"
    NOT_SUPPORTED_SERVICE = "0005"
    NO_INFORMATION_DR = "0109"
    NO_INFORMATION_SLEEP_MODE = "0108"
    NO_PERMISSION = "0011"
    NO_PERMMISION_MODIFY_RECIPE = "0113"
    NO_REGISTERED_DEVICE = "0101"
    NO_USER_INFORMATION = "9006"


class ThinQException(Exception):
    pass


class BaseThinQResult(Schema):
    result_code = EnumField(
        ThinQResultCode, data_key="resultCode", load_by=EnumField.VALUE
    )
    result = fields.Nested(Schema)


class ThinQResultSuccess(BaseThinQResult):
    result = fields.Raw()

    @post_load
    def is_successful(self, data, **kwargs):
        return data["result_code"] == ThinQResultCode.OK


class ThinQResult(BaseThinQResult):
    def __init__(self, result_class):
        self._result_schema = result_class.Schema()
        super().__init__()

    def on_bind_field(self, field_name, field):
        if isinstance(field, fields.Nested):
            # field = fields.Str()
            field.nested = self._result_schema

    @post_load
    def unwrap_result(self, data, **kwargs):
        if data["result_code"] != ThinQResultCode.OK:
            raise ThinQException(ThinQResultCode(data["result_code"]))
        return data["result"]
