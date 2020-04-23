import re

import marshmallow_dataclass
from marshmallow import Schema, fields, pre_load, post_load, EXCLUDE
from inflection import camelize


class BaseSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    @classmethod
    def wrap(cls, data_class):
        return marshmallow_dataclass.class_schema(data_class, base_schema=cls)

#
class TransformSchema(BaseSchema):
    def on_bind_field(self, field_name, field):
        field.data_key = self._transform(field.data_key or field_name)

    def _transform(self, field_name):
       return field_name

class CamelCaseSchema(TransformSchema):
    def _transform(self, field_name):
        return camelize(field_name, uppercase_first_letter=False)


# XXX - make this DRY
class ProfileResponse(CamelCaseSchema):

    account = fields.Nested(Schema)

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
            field.nested = self._nested.Schema

    @post_load
    def unwrap(self, data, **kwargs):
        return data["result"]


def controller(data_type):

    schema = data_type.Schema()

    def merge_args(self, kwargs):
        attrs = {
            k: getattr(self, k, None) for k in schema.fields.keys() if not k in kwargs
        }
        defaults = schema.dump({k: v for k, v in attrs.items() if v is not None})
        return {**defaults, **kwargs}

    class AttrDict(dict):
        def __getattr__(self, attr):
            return self.get(attr, None)

    class DataHolder(object):
        _data: data_type = None

        def __init__(self, data=None, **kwargs):
            if data is None:
                self._data = AttrDict(kwargs)
                self._data = schema.load(merge_args(self, kwargs))
            else:
                self._data = data

        @classmethod
        def load(cls, data):
            return cls(schema.load(data))

        @property
        def __dict__(self):
            return schema.dump(self._data)

        def __getattr__(self, attr):
            if hasattr(self._data, attr):
                return getattr(self._data, attr)
            # XXX - fail if super doesn't havegetattr?
            return super().__getattr__(self, attr)

        def __setattr__(self, attr, value):
            if isinstance(self._data, data_type) and hasattr(self._data, attr):
                setattr(self._data, attr, value)
            else:
                super().__setattr__(attr, value)

    def class_wrapper(base_class):
        return type(base_class.__name__, (DataHolder, base_class), {})

    return class_wrapper


def initializer(obj, attr="_data"):
    @property
    def inner(self):
        data = getattr(self, attr)
        if data is None:
            return obj(self)

        value = getattr(data, obj.__name__)
        if value is not None:
            return value

        value = obj(self)
        setattr(data, obj.__name__, value)
        return value

    return inner
