import re

from marshmallow import EXCLUDE, Schema
from inflection import camelize


class BaseSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    def on_bind_field(self, field_name, field):
        field.data_key = self.transform(field.data_key or field_name)

    def transform(self, field_name):
        return field_name


class CamelCaseSchema(BaseSchema):
    def transform(self, field_name):
        return camelize(field_name, uppercase_first_letter=False)


# XXX - bad pun
class CamelIDSchema(CamelCaseSchema):
    def transform(self, field_name):
        return re.sub(r"(?<=[a-z])Id(?=[A-Z]|$)", "ID", super().transform(field_name))


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
