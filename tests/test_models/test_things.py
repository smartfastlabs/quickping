from quickping.utils.comparer import Comparer


def test_is(test_light):
    assert test_light.is_("on")
    assert not test_light.is_("off")

    assert test_light.is_(state="on")
    assert not test_light.is_(state="off")

    assert bool(test_light.is_(brightness=255))
    assert not test_light.is_(brightness=0)

    assert test_light.is_("on", brightness=255)
    assert not test_light.is_("off", brightness=255)
    assert not test_light.is_("on", brightness=0)
    assert not test_light.is_("off", brightness=0)
    assert test_light.is_(state="on", brightness=255)


def test_attributes(TestComplexThing, test_quickping):
    thing = TestComplexThing("thing.complex")
    thing.load(test_quickping)
    assert isinstance(thing.attributes.temperature == 10, Comparer)


def test_default_value(TestCollection):
    assert TestCollection.light == TestCollection.other_light


def test_state(test_light):
    assert test_light.state == "on"
    assert not test_light.state == "off"
