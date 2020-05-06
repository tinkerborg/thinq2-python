import re

from dataclasses import is_dataclass
from marshmallow import Schema, SchemaOpts, EXCLUDE, post_load
from inflection import camelize

from thinqtt.util import memoize


class BaseSchemaOpts(SchemaOpts):
    def __init__(self, meta, **kwargs):
        super().__init__(meta, **kwargs)
        self.polymorph = getattr(meta, "polymorph", {})


class BaseSchema(Schema):
    OPTIONS_CLASS = BaseSchemaOpts

    class Meta:
        unknown = EXCLUDE

    def on_bind_field(self, field_name, field):
        field.data_key = self.transform(field.data_key or field_name)

    def transform(self, field_name):
        return field_name

    @post_load(pass_original=True)
    def polymorphism(self, item, data, **kwargs):
        for field_name, factory in self.opts.polymorph.items():
            field_type = factory(item)
            field = self.fields.get(field_name)
            if is_dataclass(field_type):
                schema = field_type.Schema()
            elif isinstance(field_type, Schema):
                schema = field_type
            else:
                raise Exception("Polymorphed type isn't a dataclass or schema!")

            setattr(item, field_name, schema.load(data[field.data_key]))
        return item


class CamelCaseSchema(BaseSchema):
    def transform(self, field_name):
        return camelize(field_name, uppercase_first_letter=False)


# XXX - bad pun
class CamelIDSchema(CamelCaseSchema):
    def transform(self, field_name):
        return re.sub(r"(?<=[a-z])Id(?=[A-Z]|$)", "ID", super().transform(field_name))


def controller_class(data_type, **children):
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

        # XXX - fix infinite recursion error if called w/ no args
        def __init__(self, data=None, **kwargs):
            if data is None:
                self._data = AttrDict(kwargs)
                self._data = schema.load(merge_args(self, kwargs))
            elif is_dataclass(data):
                self._data = data
                super().__init__(**kwargs)
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
                if hasattr(self._data, attr):
                    return getattr(self._data, attr)

            # XXX - fail if super doesn't havegetattr?
            return super().__getattr__(attr)

        def __setattr__(self, attr, value):
            if isinstance(self._data, data_type) and hasattr(self._data, attr):
                setattr(self._data, attr, value)
            else:
                super().__setattr__(attr, value)

    def class_wrapper(base_class):
        return type(base_class.__name__, (Controller, base_class), {})

    return class_wrapper


def controller_factory(func):
    @property
    @memoize
    def inner(self, *args, **kwargs):
        return func(self, getattr(self._data, func.__name__))

    return inner


def controller(class_or_func, **children):
    if isinstance(class_or_func, type):
        return controller_class(class_or_func, **children)
    if callable(class_or_func):
        return controller_factory(class_or_func)


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
