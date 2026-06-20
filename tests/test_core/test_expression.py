"""Tests for Expression module."""

from __future__ import annotations

import pytest

from minimatic.core.attributes import Flat, HoldAll, Orderless
from minimatic.core.expression import (
    Expression,
    attrs_of,
    has_attr,
    head_of,
    is_expr,
    tail_of,
)
from minimatic.core.symbol import Symbol

Plus = Symbol("Plus")
x = Symbol("x")
y = Symbol("y")


class TestExpressionConstruction:
    def test_basic_expression(self):
        expr = Expression(Plus, 1, 2, 3)
        assert expr.head == Plus
        assert expr.args == (1, 2, 3)
        assert expr.tail == (1, 2, 3)

    def test_no_args(self):
        expr = Expression(Plus)
        assert expr.args == ()

    def test_expression_head_must_be_symbol_or_expr(self):
        with pytest.raises(TypeError, match="Symbol or Expression"):
            Expression("bad", 1)

    def test_attrs_none_default(self):
        expr = Expression(Plus, 1)
        assert expr.attributes == frozenset()

    def test_attrs_frozenset(self):
        expr = Expression(Plus, 1, _attrs=frozenset({Flat}))
        assert Flat in expr.attributes

    def test_attrs_set_converted(self):
        expr = Expression(Plus, 1, _attrs={Flat, Orderless})
        assert Flat in expr.attributes
        assert Orderless in expr.attributes

    def test_attrs_non_symbol_raises(self):
        with pytest.raises(TypeError, match="attributes must be Symbols"):
            Expression(Plus, 1, _attrs={"bad"})


class TestExpressionProperties:
    def test_len(self):
        assert len(Expression(Plus, 1, 2)) == 2

    def test_iter(self):
        expr = Expression(Plus, 1, 2)
        assert list(expr) == [1, 2]

    def test_contains(self):
        expr = Expression(Plus, 1, 2)
        assert 1 in expr
        assert 3 not in expr


class TestExpressionAttributes:
    def test_has_attr_true(self):
        expr = Expression(Plus, 1, _attrs={Flat})
        assert expr.has_attr(Flat)

    def test_has_attr_false(self):
        expr = Expression(Plus, 1)
        assert not expr.has_attr(Flat)

    def test_has_any_attr(self):
        expr = Expression(Plus, 1, _attrs={Flat})
        assert expr.has_any_attr(Flat, Orderless)
        assert not expr.has_any_attr(Orderless, HoldAll)

    def test_has_all_attrs(self):
        expr = Expression(Plus, 1, _attrs={Flat, Orderless})
        assert expr.has_all_attrs(Flat, Orderless)
        assert not expr.has_all_attrs(Flat, HoldAll)


class TestExpressionTransformations:
    def test_with_head(self):
        expr = Expression(Plus, 1, 2)
        Times = Symbol("Times")
        new = expr.with_head(Times)
        assert new.head == Times
        assert new.args == (1, 2)

    def test_with_tail(self):
        expr = Expression(Plus, 1, 2)
        new = expr.with_tail(3, 4)
        assert new.args == (3, 4)
        assert new.head == Plus

    def test_with_attrs(self):
        expr = Expression(Plus, 1)
        new = expr.with_attrs(Flat)
        assert Flat in new.attributes

    def test_without_attrs(self):
        expr = Expression(Plus, 1, _attrs={Flat, Orderless})
        new = expr.without_attrs(Flat)
        assert Flat not in new.attributes
        assert Orderless in new.attributes

    def test_with_only_attrs(self):
        expr = Expression(Plus, 1, _attrs={Flat})
        new = expr.with_only_attrs(Orderless)
        assert new.attributes == frozenset({Orderless})

    def test_map_args(self):
        expr = Expression(Plus, 1, 2, 3)
        new = expr.map_args(lambda x: x * 2)
        assert new.args == (2, 4, 6)

    def test_map_args_indexed(self):
        expr = Expression(Plus, 10, 20, 30)
        new = expr.map_args_indexed(lambda i, x: x + i)
        assert new.args == (10, 21, 32)

    def test_append(self):
        expr = Expression(Plus, 1)
        new = expr.append(2, 3)
        assert new.args == (1, 2, 3)

    def test_prepend(self):
        expr = Expression(Plus, 3)
        new = expr.prepend(1, 2)
        assert new.args == (1, 2, 3)


class TestExpressionEquality:
    def test_equal_same_structure(self):
        a = Expression(Plus, 1, 2)
        b = Expression(Plus, 1, 2)
        assert a == b

    def test_not_equal_different_args(self):
        a = Expression(Plus, 1, 2)
        b = Expression(Plus, 1, 3)
        assert a != b

    def test_not_equal_different_head(self):
        Times = Symbol("Times")
        a = Expression(Plus, 1)
        b = Expression(Times, 1)
        assert a != b

    def test_not_equal_different_attrs(self):
        a = Expression(Plus, 1, _attrs={Flat})
        b = Expression(Plus, 1)
        assert a != b

    def test_hash_consistent(self):
        a = Expression(Plus, 1, 2)
        b = Expression(Plus, 1, 2)
        assert hash(a) == hash(b)


class TestExpressionRepresentation:
    def test_str(self):
        expr = Expression(Plus, 1, 2)
        assert str(expr) == "Plus[1, 2]"

    def test_repr_without_attrs(self):
        expr = Expression(Plus, 1)
        r = repr(expr)
        assert "Plus[1]" in r
        assert "attrs" not in r

    def test_repr_with_attrs(self):
        expr = Expression(Plus, 1, _attrs={Flat})
        r = repr(expr)
        assert "attrs" in r


class TestModuleFunctions:
    def test_is_expr(self):
        assert is_expr(Expression(Plus, 1))
        assert not is_expr(42)

    def test_head_of_expression(self):
        expr = Expression(Plus, 1, 2)
        assert head_of(expr) == Plus

    def test_head_of_symbol(self):
        assert head_of(x) == Symbol("Symbol")

    def test_head_of_int(self):
        assert head_of(42) == Symbol("Integer")

    def test_head_of_float(self):
        assert head_of(3.14) == Symbol("Real")

    def test_head_of_string(self):
        assert head_of("hello") == Symbol("String")

    def test_tail_of_expression(self):
        expr = Expression(Plus, 1, 2)
        assert tail_of(expr) == (1, 2)

    def test_tail_of_atom(self):
        assert tail_of(42) == ()

    def test_attrs_of_expression(self):
        expr = Expression(Plus, 1, _attrs={Flat})
        assert Flat in attrs_of(expr)

    def test_attrs_of_atom(self):
        assert attrs_of(42) == frozenset()

    def test_has_attr_function(self):
        expr = Expression(Plus, 1, _attrs={Flat})
        assert has_attr(expr, Flat)
        assert not has_attr(42, Flat)
