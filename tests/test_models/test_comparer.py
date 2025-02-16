from quickping.models import AndComparer, AttributeComparer, OrComparer


def test_basic(test_light):
    # Create a new comparer
    comparer = AttributeComparer(
        thing=test_light,
        checks={
            "state": "on",
            "brightness": 255,
        },
    )

    assert comparer


def test_boolean(test_light):
    # Create a new comparer
    comparer = AttributeComparer(
        thing=test_light,
        checks={
            "state": "on",
        },
    )
    comparer_2 = AttributeComparer(
        thing=test_light,
        checks={
            "brightness": 255,
        },
    )

    comparer_3 = AttributeComparer(
        thing=test_light,
        checks={
            "state": "off",
        },
    )

    assert comparer
    assert comparer_2
    assert not comparer_3
    assert comparer & comparer_2
    assert comparer | comparer_2
    assert not (comparer & comparer_3)
    assert comparer & comparer_3 | comparer_2
