from quickping import when


def test_attribute_comparison(TestComplexThing):
    @when(TestComplexThing.attributes.temperature == 10)
    def test():
        assert True

    assert True
