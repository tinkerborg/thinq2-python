import re
import inspect

from dataclasses import is_dataclass

from attrdict import AttrDict
from marshmallow import EXCLUDE, Schema
from inflection import camelize

from thinq2.util import memoize


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


class AbstractController:
    pass


def controller_class(data_type, **children):
    schema = data_type.Schema()

    def merge_args(self, kwargs):
        attrs = {
            k: getattr(self, k, None) for k in schema.fields.keys() if not k in kwargs
        }
        defaults = schema.dump({k: v for k, v in attrs.items() if v is not None})
        return {**defaults, **kwargs}

    class Controller(AbstractController):
        _data: data_type = None

        # XXX - fix infinite recursion error if called w/ no args
        def __init__(self, data=None, *args, **kwargs):
            init = inspect.signature(super().__init__)
            pass_keys = AttrDict(
                filter(self._param_filter, init.parameters.items())
            ).keys()
            pass_params = {k: v for k, v in kwargs.items() if k in pass_keys}

            super().__init__(**pass_params)

            if data is None:
                self._data = AttrDict(kwargs)
                args = AttrDict(filter(self._args_filter, kwargs.items()))
                self._data = schema.load(merge_args(self, args))
            else:
                if is_dataclass(data):
                    self._data = data
                else:
                    self._data = schema.load(data)

        def _args_filter(self, item):
            key, value = item
            return not isinstance(value, AbstractController)

        def _param_filter(self, item):
            name, param = item
            return param.kind in [param.POSITIONAL_OR_KEYWORD, param.KEYWORD_ONLY]

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
    field_name = func.__name__

    @property
    @memoize
    def inner(self, *args, **kwargs):
        if isinstance(self._data, dict):
            existing = self._data.get(field_name, None)
        else:
            existing = getattr(self._data, field_name, None)

        if isinstance(existing, AbstractController):
            """ If it's already a controller, return it """
            return existing

        return func(self, existing)

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

        value = getattr(data, obj.__name__, None) or obj(self)
        setattr(data, obj.__name__, value)
        return value

    return inner
