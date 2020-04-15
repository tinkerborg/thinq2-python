import marshmallow_dataclass
from marshmallow import Schema, fields, post_load, EXCLUDE
from inflection import camelize

class DataSchema(Schema):
  class Meta:
    unknown = EXCLUDE

  def on_bind_field(self, field_name, field):
    field.data_key = camelize(field_name, uppercase_first_letter=False)

  @staticmethod
  def wrap(data_class):
    return marshmallow_dataclass.class_schema(data_class, base_schema=DataSchema)

class ThinQ2Response(Schema):

  result_code = fields.Str(data_key="resultCode")
  result = fields.Nested(Schema)

  def __init__(self, nested=None, **kwargs):
    self._nested = nested
    super().__init__(**kwargs)

  def on_bind_field(self, field_name, field):
    if field_name is "result" and self._nested != None:
      field.nested = DataSchema.wrap(self._nested)

  @post_load
  def unwrap_result(self, data, **kwargs):
    return data["result"]
