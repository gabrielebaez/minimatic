"""Tests for Symbol module."""

from __future__ import annotations

import pytest

from minimatic.core.symbol import (
    Symbol,
    gensym,
    is_symbol,
    symbol,
)


class TestSymbolCreation:
    def test_create_symbol(self):
        s = Symbol("x")
        assert s.name == "x"

    def test_create_system_symbols(self):
        s = Symbol("Plus")
        assert s.name == "Plus"

    def test_empty_name_raises(self):
        with pytest.raises(ValueError, match="empty"):
            Symbol("")

    def test_non_string_raises(self):
        with pytest.raises(TypeError, match="str"):
            Symbol(123)


class TestSymbolInterning:
    def test_same_name_same_object(self):
        a = Symbol("x")
        b = Symbol("x")
        assert a is b

    def test_different_name_different_object(self):
        a = Symbol("x")
        b = Symbol("y")
        assert a is not b

    def test_factory_function_interns(self):
        a = symbol("foo")
        b = symbol("foo")
        assert a is b


class TestSymbolEquality:
    def test_equal_same_name(self):
        assert Symbol("x") == Symbol("x")

    def test_not_equal_different_name(self):
        assert Symbol("x") != Symbol("y")

    def test_not_equal_non_symbol(self):
        assert Symbol("x") != "x"

    def test_hash_same_for_equal(self):
        assert hash(Symbol("x")) == hash(Symbol("x"))

    def test_hash_consistent(self):
        s = Symbol("a")
        assert hash(s) == hash(s)


class TestSymbolOrdering:
    def test_lt(self):
        assert Symbol("a") < Symbol("b")

    def test_le(self):
        assert Symbol("a") <= Symbol("a")

    def test_gt(self):
        assert Symbol("b") > Symbol("a")

    def test_ge(self):
        assert Symbol("a") >= Symbol("a")

    def test_ordering_non_symbol_returns_not_implemented(self):
        result = Symbol("a").__lt__("x")
        assert result is NotImplemented


class TestSymbolPredicates:
    def test_is_symbol_true(self):
        assert is_symbol(Symbol("x"))

    def test_is_symbol_false(self):
        assert not is_symbol("x")
        assert not is_symbol(42)

    def test_isinstance_tuple(self):
        assert isinstance(Symbol("x"), tuple)


class TestGensym:
    def test_gensym_returns_unique(self):
        a = gensym()
        b = gensym()
        assert a is not b
        assert a.name != b.name

    def test_gensym_prefix(self):
        s = gensym("tmp")
        assert s.name.startswith("tmp")

    def test_gensym_default_prefix(self):
        s = gensym()
        assert s.name.startswith("G")

    def test_gensym_auto_increments(self):
        a = gensym("X")
        b = gensym("X")
        assert int(a.name[1:]) + 1 == int(b.name[1:])


class TestSymbolRepresentation:
    def test_repr(self):
        assert repr(Symbol("x")) == 'Symbol("x")'

    def test_str(self):
        assert str(Symbol("x")) == "x"
