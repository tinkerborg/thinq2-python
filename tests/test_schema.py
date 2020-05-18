import pytest

from marshmallow_dataclass import dataclass

from thinq2 import schema


def test_base_schema_ignores_unknown_fields():
    model = schema.BaseSchema().load(dict(foo="bar"))
    assert model == {}


def test_controller_can_be_constructed_from_dict(Controller, valid_data):
    controller = Controller(valid_data)
    assert isinstance(controller, Controller)


def test_controller_can_be_constructed_from_kwargs(Controller, valid_data):
    controller = Controller(**valid_data)
    assert isinstance(controller, Controller)


def test_controller_can_be_constructed_from_model(Controller, Model, valid_data):
    model = Model(**valid_data)
    controller = Controller(model)
    assert isinstance(controller, Controller)


def test_controller_as_dict_equals_model_data(Controller, valid_data):
    controller = Controller(valid_data)
    assert vars(controller) == valid_data


def test_controller_constructor_styles_are_equivalent(Controller, Model, valid_data):
    controller_from_dict = Controller(valid_data)
    controller_from_kwargs = Controller(**valid_data)
    controller_from_model = Controller(Model(**valid_data))
    assert vars(controller_from_dict) == vars(controller_from_kwargs)
    assert vars(controller_from_dict) == vars(controller_from_model)


def test_controller_instances_with_identical_data_are_not_equal(Controller, valid_data):
    controller_a = Controller(valid_data)
    controller_b = Controller(valid_data)
    assert controller_a != controller_b


def test_initialzer_decorator_sets_default_value(Controller, data_with_missing_quux):
    quux = 43

    class QuuxedController(Controller):
        @schema.initializer
        def quux(self):
            return quux

    controller = QuuxedController(**data_with_missing_quux)
    assert controller.quux == quux


def test_initialzer_ignored_when_value_supplied(Controller, data_with_missing_quux):
    quux = 43
    data = {**data_with_missing_quux, **dict(quux=quux + 1)}

    class QuuxedController(Controller):
        @schema.initializer
        def quux(self):
            return quux

    controller = QuuxedController(data)
    assert controller.quux != quux


def test_initialize_nested_controller(ParentController, Controller, nested_data):
    controller = ParentController(nested_data)
    assert isinstance(controller.child, Controller)


def test_nested_controller_as_dict_matches_data(ParentController, nested_data):
    controller = ParentController(nested_data)
    assert nested_data == vars(controller)


@pytest.fixture
def Model():
    @dataclass
    class Model:
        foo: str
        quux: int

    return Model


@pytest.fixture
def Controller(Model):
    @schema.controller(Model)
    class Controller:
        pass

    return Controller


@pytest.fixture
def ParentModel(Model):
    @dataclass
    class ParentModel:
        baz: str
        child: Model

    return ParentModel


@pytest.fixture
def ParentController(ParentModel, Controller):
    @schema.controller(ParentModel)
    class ParentController:
        @schema.controller
        def child(self, child):
            return Controller(child)

    return ParentController


@pytest.fixture
def valid_data():
    return dict(foo="bar", quux=42)


@pytest.fixture
def data_with_missing_quux():
    return dict(foo="bar")


@pytest.fixture
def nested_data(valid_data):
    return dict(baz="xyzzy", child=valid_data)
