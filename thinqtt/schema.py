import re

import marshmallow_dataclass
from marshmallow import Schema, fields, pre_load, post_load, EXCLUDE
from inflection import camelize

from thinqtt.model.auth import OAuthProfile


class DataSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    @classmethod
    def wrap(cls, data_class):
        return marshmallow_dataclass.class_schema(data_class, base_schema=cls)


class CamelDataSchema(DataSchema):
    def on_bind_field(self, field_name, field):
        field.data_key = self._transform(field_name)

    def _transform(self, field_name):
        return camelize(field_name, uppercase_first_letter=False)

# XXX - make this DRY
class ProfileResponse(CamelDataSchema):

    account = fields.Nested(marshmallow_dataclass.class_schema(OAuthProfile))

    def _transform(self, field_name):
        return re.sub(r"(?<=[a-z])Id(?=[A-Z]|$)", "ID", super()._transform(field_name))

    @pre_load
    def unwrap_result(self, data, **kwargs):
        return data["account"]


class ThinQResponse(Schema):

    result_code = fields.Str(data_key="resultCode")
    result = fields.Nested(Schema)

    def __init__(self, nested=None, **kwargs):
        self._nested = nested
        super().__init__(**kwargs)

    def on_bind_field(self, field_name, field):
        if field_name is "result" and self._nested != None:
            field.nested = CamelDataSchema.wrap(self._nested)

    @post_load
    def unwrap_result(self, data, **kwargs):
        return data["result"]
