"""Shared test fixtures for minimatic."""

import pytest

from minimatic.core.symbol import Symbol, clear_symbol_cache
from minimatic.eval.context import EvaluationContext


@pytest.fixture(autouse=True)
def _clean_symbol_cache():
    """Clear symbol cache between tests to avoid cross-test contamination."""
    clear_symbol_cache()
    yield
    clear_symbol_cache()


@pytest.fixture
def ctx():
    """A fresh EvaluationContext for tests."""
    return EvaluationContext("test")


# Common symbols
@pytest.fixture
def Plus():
    return Symbol("Plus")


@pytest.fixture
def Times():
    return Symbol("Times")


@pytest.fixture
def Power():
    return Symbol("Power")


@pytest.fixture
def x():
    return Symbol("x")


@pytest.fixture
def y():
    return Symbol("y")


@pytest.fixture
def z():
    return Symbol("z")
