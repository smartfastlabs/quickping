from quickping.utils.comparer import CallableComparer


def test_basic(test_light):
    # Create a new comparer
    comparer = CallableComparer(
        lambda: test_light.state.value == "on",
    )

    assert comparer


def test_boolean(test_light):
    # Create a new comparer
    comparer = CallableComparer(
        lambda: test_light.state.value == "on",
    )
    comparer_2 = test_light.brightness == 255

    comparer_3 = CallableComparer(
        lambda: test_light.state.value == "off",
    )

    assert comparer
    assert comparer_2
    assert not comparer_3
    assert comparer & comparer_2
    assert comparer | comparer_2
    assert not (comparer & comparer_3)
    assert comparer & comparer_3 | comparer_2
