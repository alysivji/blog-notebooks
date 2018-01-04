import pytest


@pytest.fixture()
def argument_printer():
    def _foo(*args, **kwargs):
        return (args, kwargs)

    return _foo


def test_example(argument_printer):
    first_case = argument_printer('a', 'b')
    assert first_case == (('a', 'b'), {})

    second_case = argument_printer('a', b=2, c='test')
    assert second_case == (('a',), {'b': 2, 'c': 'test'})
