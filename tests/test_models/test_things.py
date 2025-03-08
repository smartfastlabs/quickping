from quickping.utils.comparer import Comparer


def test_attribute_equality(test_light):
    assert test_light.is_on
    assert not test_light.is_off

    assert test_light.staet == "on"
    assert not test_light.state == "off"

    assert test_light.brighness == 255
    assert not test_light.brightness == 0


def test_attributes(TestComplexThing, test_quickping):
    thing = TestComplexThing("thing.complex")
    thing.load(test_quickping)
    assert isinstance(thing.attributes.temperature == 10, Comparer)


def test_default_value(TestCollection):
    assert TestCollection.light == TestCollection.other_light


def test_state(test_light):
    assert test_light.state == "on"
    assert not test_light.state == "off"


def test_attribute_equality(test_light):
    assert test_light.brightness == 255
