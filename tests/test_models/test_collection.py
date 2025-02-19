def test_types(
    test_quickping,
    test_light,
    TestCollectionTwo,
):
    assert TestCollectionTwo.light is test_light
    assert TestCollectionTwo.light_2 is test_light
    assert TestCollectionTwo.light_3 is test_light
    # assert TestCollectionTwo.other.light is TestCollectionTwo.other_light
