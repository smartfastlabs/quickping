from quickping import Device, QuickpingApp


def test_build_args_thing(test_quickping, test_light):
    def dummy_func(foo: test_light, quickping) -> None:
        pass

    args = test_quickping.build_args(dummy_func)
    assert args == [test_light, test_quickping]


def test_build_args_collection(test_quickping, test_light, TestCollectionTwo):
    def dummy_func(
        quickping: QuickpingApp,
        collection: TestCollectionTwo,
        other_collection: TestCollectionTwo = TestCollectionTwo,
        second_light=TestCollectionTwo.light_2,
        light: Device = TestCollectionTwo.light,
    ) -> None:
        assert collection is other_collection
        assert other_collection.light == test_light
        assert collection.light == test_light
        assert light == test_light
        assert quickping == test_quickping
        assert second_light == test_light

    dummy_func(*test_quickping.build_args(dummy_func))
