"""Simple tests."""

from pyllama.main import hello, greet


def test_hello():
    assert hello() == "Hello, World!"


def test_greet():
    assert greet("Alice") == "Hello, Alice!"