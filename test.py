class Foo:
    def __lt__(self, other):
        print(f"{self} < {other}")
        return True

    def __gt__(self, other):
        print(f"{self} > {other}")
        return True


print(1 < Foo() < 5)
