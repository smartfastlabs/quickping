from quickping.models import AndComparer, CallableComparer, OrComparer


def test_basic(test_light):
    # Create a new comparer
    comparer = CallableComparer(
        lambda: test_light.state == "on",
    )

    assert comparer


def test_boolean(test_light):
    # Create a new comparer
    comparer = CallableComparer(
        lambda: test_light.state == "on",
    )
    comparer_2 = CallableComparer(
        lambda: test_light.brightness == 255,
    )

    comparer_3 = CallableComparer(
        lambda: test_light.state == "off",
    )

    assert comparer
    assert comparer_2
    assert not comparer_3
    assert comparer & comparer_2
    assert comparer | comparer_2
    assert not (comparer & comparer_3)
    assert comparer & comparer_3 | comparer_2
