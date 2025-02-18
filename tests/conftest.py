from typing import Annotated

import pytest
from dobles import InstanceDouble

from quickping import Collection, Device, QuickpingApp


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
def test_light(test_light_entity):
    return Device("light.test_light", entity=test_light_entity)


@pytest.fixture
def TestCollection(test_light):
    class Inner(Collection):
        light: Annotated[Device, test_light.id]

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
