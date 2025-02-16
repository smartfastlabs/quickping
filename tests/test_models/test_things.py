def test_is(test_light):
    assert test_light.is_("on")
    assert not test_light.is_("off")

    assert test_light.is_(state="on")
    assert not test_light.is_(state="off")

    assert test_light.is_(brightness=255)
    assert not test_light.is_(brightness=0)

    assert test_light.is_("on", brightness=255)
    assert not test_light.is_("off", brightness=255)
    assert not test_light.is_("on", brightness=0)
    assert not test_light.is_("off", brightness=0)
    assert test_light.is_(state="on", brightness=255)
