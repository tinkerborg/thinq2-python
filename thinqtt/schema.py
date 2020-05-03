import re

from dataclasses import is_dataclass
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


def controller(data_type, **children):
    schema = data_type.Schema()

    def merge_args(self, kwargs):
        attrs = {
            k: getattr(self, k, None) for k in schema.fields.keys() if not k in kwargs
        }
        defaults = schema.dump({k: v for k, v in attrs.items() if v is not None})
        return {**defaults, **kwargs}

    class AttrDict(dict):
        def __init__(self, *args, **kwargs):
            super(AttrDict, self).__init__(*args, **kwargs)
            self.__dict__ = self

    class Controller(object):
        _data: data_type = None
        _children: AttrDict = None

        # XXX - fix infinite recursion error if called w/ no args
        def __init__(self, data=None, **kwargs):
            self._children = AttrDict(
                {
                    key: Controller(kwargs[key])
                    for key, Controller in children.items()
                }
            )

            if data is None:
                self._data = AttrDict(kwargs)
                self._data = schema.load(merge_args(self, kwargs))
            elif is_dataclass(self._data):
                self._data = data
            else:
                self._data = schema.load(data)

        @classmethod
        def load(cls, data):
            return cls(schema.load(data))

        @property
        def __dict__(self):
            return schema.dump(self._data)

        # XXX - should throw attribute exception if attr not in schema
        def __getattr__(self, attr):
            if not attr.startswith("_"):
                for container in [self._children, self._data]:
                    if hasattr(container, attr):
                        return getattr(container, attr)

            # XXX - fail if super doesn't havegetattr?
            return super().__getattr__(attr)

        def __setattr__(self, attr, value):
            if isinstance(self._data, data_type) and hasattr(self._data, attr):
                if hasattr(self._children, attr):
                    if isinstance(value, children[attr]):
                        self._children[attr] = value
                    else:
                        self._children[attr] = children[attr](value)
                    setattr(self._data, attr, value)
                else:
                    setattr(self._data, attr, value)
            else:
                super().__setattr__(attr, value)

    def class_wrapper(base_class):
        return type(base_class.__name__, (Controller, base_class), {})

    return class_wrapper


def initializer(obj, attr="_data"):
    @property
    def inner(self):
        data = getattr(self, attr)
        if data is None:
            return obj(self)

        try:
            return getattr(data, obj.__name__)
        except AttributeError:
            value = obj(self)
            setattr(data, obj.__name__, value)
            return value

    return inner
