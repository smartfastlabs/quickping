def test_build_args(test_quickping, test_light):
    def dummy_func(foo: test_light, quickping) -> None:
        pass

    args = test_quickping.build_args(dummy_func)
    assert args == [test_light, test_quickping]
