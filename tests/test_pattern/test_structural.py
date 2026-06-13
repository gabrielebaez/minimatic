"""Tests for Structural patterns module."""
from __future__ import annotations

import pytest
from src.core.symbol import Symbol
from src.core.expression import Expression
from src.pattern.blanks import blank, blank_seq, Blank, BlankSequence
from src.pattern.structural import (
    Pattern, Condition, Alternatives, PatternTest, Optional as OptionalPattern,
    Repeated, RepeatedNull, Except, Verbatim, HoldPattern,
    pattern, condition, alternatives, pattern_test, optional,
    repeated, repeated_null, except_pattern, verbatim, hold_pattern,
    is_pattern, is_condition, is_alternatives, is_pattern_test,
    is_optional, is_repeated, is_repeated_null, is_except,
    is_verbatim, is_hold_pattern, is_pattern_construct,
    pattern_name, pattern_blank, get_default_value,
    get_condition_test, get_condition_pattern,
    unwrap_hold_pattern, collect_pattern_names,
)

x = Symbol("x")
y = Symbol("y")
Integer = Symbol("Integer")


class TestPatternConstructors:
    def test_pattern_unconstrained(self):
        p = pattern(x)
        assert p.head == Pattern
        assert p.args[0] == x
        assert p.args[1].head == Blank

    def test_pattern_with_blank(self):
        p = pattern(x, blank(Integer))
        assert p.args[1].head == Blank
        assert p.args[1].args[0] == Integer

    def test_pattern_bad_name(self):
        with pytest.raises(TypeError, match="Symbol"):
            pattern("x")

    def test_condition(self):
        test_expr = Expression(Symbol("Greater"), x, 0)
        p = condition(pattern(x), test_expr)
        assert p.head == Condition
        assert p.args[0].head == Pattern
        assert p.args[1] == test_expr

    def test_alternatives(self):
        a, b = Symbol("a"), Symbol("b")
        p = alternatives(a, b)
        assert p.head == Alternatives
        assert len(p.args) == 2

    def test_alternatives_too_few(self):
        with pytest.raises(ValueError, match="at least 2"):
            alternatives(x)

    def test_pattern_test(self):
        NumberQ = Symbol("NumberQ")
        p = pattern_test(pattern(x), NumberQ)
        assert p.head == PatternTest
        assert p.args[1] == NumberQ

    def test_optional(self):
        p = optional(pattern(x), 0)
        assert p.head == OptionalPattern
        assert p.args[1] == 0

    def test_optional_no_default(self):
        p = optional(pattern(x))
        assert p.head == OptionalPattern
        assert len(p.args) == 1

    def test_repeated(self):
        p = repeated(pattern(x))
        assert p.head == Repeated
        assert len(p.args) == 1

    def test_repeated_null(self):
        p = repeated_null(pattern(x))
        assert p.head == RepeatedNull

    def test_except_no_alt(self):
        p = except_pattern(0)
        assert p.head == Except
        assert len(p.args) == 1

    def test_except_with_alt(self):
        p = except_pattern(0, blank(Integer))
        assert p.head == Except
        assert len(p.args) == 2

    def test_verbatim(self):
        expr = Expression(Symbol("Plus"), 1, 2)
        p = verbatim(expr)
        assert p.head == Verbatim
        assert p.args[0] == expr

    def test_hold_pattern(self):
        expr = Expression(Symbol("Plus"), x, 1)
        p = hold_pattern(expr)
        assert p.head == HoldPattern
        assert p.args[0] == expr


class TestStructuralPredicates:
    def test_is_pattern(self):
        assert is_pattern(pattern(x))
        assert not is_pattern(blank())

    def test_is_condition(self):
        assert is_condition(condition(pattern(x), Symbol("True")))
        assert not is_condition(pattern(x))

    def test_is_alternatives(self):
        assert is_alternatives(alternatives(x, y))
        assert not is_alternatives(pattern(x))

    def test_is_pattern_test(self):
        assert is_pattern_test(pattern_test(pattern(x), Symbol("Q")))
        assert not is_pattern_test(pattern(x))

    def test_is_optional(self):
        assert is_optional(optional(pattern(x), 0))
        assert not is_optional(pattern(x))

    def test_is_repeated(self):
        assert is_repeated(repeated(pattern(x)))
        assert not is_repeated(pattern(x))

    def test_is_repeated_null(self):
        assert is_repeated_null(repeated_null(pattern(x)))
        assert not is_repeated_null(pattern(x))

    def test_is_except(self):
        assert is_except(except_pattern(0))
        assert not is_except(pattern(x))

    def test_is_verbatim(self):
        assert is_verbatim(verbatim(x))
        assert not is_verbatim(pattern(x))

    def test_is_hold_pattern(self):
        assert is_hold_pattern(hold_pattern(x))
        assert not is_hold_pattern(pattern(x))

    def test_is_pattern_construct(self):
        assert is_pattern_construct(pattern(x))
        assert is_pattern_construct(condition(pattern(x), Symbol("True")))
        assert is_pattern_construct(blank())
        assert is_pattern_construct(blank_seq())
        assert not is_pattern_construct(Symbol("x"))


class TestStructuralUtilities:
    def test_pattern_name(self):
        assert pattern_name(pattern(x)) == x
        assert pattern_name(blank()) is None

    def test_pattern_blank(self):
        p = pattern(x, blank(Integer))
        assert pattern_blank(p).head == Blank

    def test_get_default_value(self):
        p = optional(pattern(x), 42)
        assert get_default_value(p) == 42

    def test_get_default_value_none(self):
        p = optional(pattern(x))
        assert get_default_value(p) is None

    def test_get_condition_test(self):
        test = Symbol("True")
        p = condition(pattern(x), test)
        assert get_condition_test(p) == test

    def test_get_condition_pattern(self):
        p = condition(pattern(x), Symbol("True"))
        assert get_condition_pattern(p).head == Pattern

    def test_unwrap_hold_pattern(self):
        expr = Expression(Symbol("Plus"), x, 1)
        p = hold_pattern(expr)
        assert unwrap_hold_pattern(p) == expr

    def test_unwrap_hold_pattern_no_hold(self):
        assert unwrap_hold_pattern(pattern(x)) == pattern(x)

    def test_collect_pattern_names(self):
        Plus = Symbol("Plus")
        p = Expression(Plus, pattern(x), pattern(y))
        names = collect_pattern_names(p)
        assert x in names
        assert y in names

    def test_collect_pattern_names_nested(self):
        inner = pattern(x)
        outer = pattern(y, inner)
        names = collect_pattern_names(outer)
        assert x in names
        assert y in names
