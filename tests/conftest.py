import pytest
from dobles import InstanceDouble

from quickping import Device


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
