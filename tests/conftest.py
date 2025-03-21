from typing import Annotated

import pytest
from dobles import InstanceDouble

from quickping import (
    Attribute,
    Attributes,
    Collection,
    Device,
    FancyLight,
    Light,
    QuickpingApp,
)


@pytest.fixture
def test_quickping():
    return QuickpingApp()


@pytest.fixture
def test_light_entity():
    return InstanceDouble(
        "appdaemon.entity.Entity",
        id="light.test_light",
        state="on",
        brightness=255,
    )


@pytest.fixture
def TestComplexThing():
    class Inner(Device):
        class A(Attributes):
            temperature: Annotated[Attribute, int]
            color: Annotated[Attribute, str]

        attributes: A

    return Inner


@pytest.fixture
def test_light(test_light_entity):
    result: FancyLight = FancyLight("light.test_light")
    result.state.value = "on"
    result.brightness.value = 255
    return result


@pytest.fixture
def TestCollection(test_light):
    class Inner(Collection):
        light: Annotated[Device, test_light.id]
        other_light: Device = test_light

    return Inner


@pytest.fixture
def TestCollectionTwo(
    test_collection,
    TestCollection,
    test_light,
    test_quickping,
):
    class OtherCollection(Collection):
        light: Annotated[Device, "light.other"]

    class Inner(Collection):
        # TODO: HANDLE IN METACLASS AT CREATION NOT AT __getatrribute__
        light: Annotated[Device, test_collection.light]
        light_2: Annotated[Device, TestCollection.light]
        light_3: Annotated[Device, "light.test_light"]
        other: OtherCollection
        other_light: Annotated[Device, OtherCollection.light]

    return Inner


@pytest.fixture
def test_collection(TestCollection, test_quickping):
    result = TestCollection()

    result.load(test_quickping)
    return result
