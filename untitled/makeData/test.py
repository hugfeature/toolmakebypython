import pytest


def inc(x):
    return x + 1


def test_answer():
    assert inc(4) == 5


class TestClass:
    def test_one(self):
        x = "this"
        assert "h" in x

    def test_two(self):
        x = "hello"
        assert hasattr(x, "check")


