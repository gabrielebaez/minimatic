"""Tests for Matcher module."""

from __future__ import annotations

from minimatic.core.attributes import Flat, Orderless
from minimatic.core.expression import Expression
from minimatic.core.symbol import Symbol
from minimatic.pattern.bindings import Bindings, empty_bindings
from minimatic.pattern.blanks import blank, blank_null_seq, blank_seq
from minimatic.pattern.matcher import (
    NO_MATCH,
    find_all_matches,
    match,
    match_sequence,
    matches,
    replace_with_bindings,
    success,
)
from minimatic.pattern.structural import (
    alternatives,
    condition,
    except_pattern,
    hold_pattern,
    pattern,
    pattern_test,
    repeated,
    repeated_null,
    verbatim,
)

Plus = Symbol("Plus")
Times = Symbol("Times")
Integer = Symbol("Integer")
List = Symbol("List")
x = Symbol("x")
y = Symbol("y")
z = Symbol("z")


class TestMatchBasic:
    def test_blank_matches_anything(self):
        assert matches(blank(), 42)
        assert matches(blank(), "hello")
        assert matches(blank(), Symbol("x"))

    def test_typed_blank_matches(self):
        assert matches(blank(Integer), 42)
        assert not matches(blank(Integer), 3.14)

    def test_literal_match(self):
        assert matches(42, 42)
        assert not matches(42, 43)

    def test_symbol_match(self):
        assert matches(x, x)
        assert not matches(x, y)

    def test_expression_match(self):
        from minimatic.pattern.structural import pattern as mk_pattern

        pat = Expression(Plus, mk_pattern(x), mk_pattern(y))
        expr = Expression(Plus, 1, 2)
        result = match(pat, expr)
        assert result.success
        assert result[x] == 1
        assert result[y] == 2

    def test_expression_head_mismatch(self):
        pat = Expression(Plus, x, y)
        expr = Expression(Times, 1, 2)
        assert not matches(pat, expr)


class TestMatchNamedPatterns:
    def test_named_pattern_bind(self):
        pat = pattern(x)
        result = match(pat, 42)
        assert result.success
        assert result[x] == 42

    def test_named_typed_pattern(self):
        pat = pattern(x, blank(Integer))
        result = match(pat, 42)
        assert result.success
        assert result[x] == 42

    def test_named_typed_pattern_mismatch(self):
        pat = pattern(x, blank(Integer))
        result = match(pat, 3.14)
        assert not result.success


class TestMatchCondition:
    def test_condition_no_evaluator_fails_safe(self):
        pat = condition(pattern(x), Symbol("True"))
        result = match(pat, 42)
        assert not result.success

    def test_condition_with_evaluator(self):
        def evaluator(expr):
            return True

        pat = condition(pattern(x), Symbol("True"))
        result = match(pat, 42, evaluator=evaluator)
        assert result.success
        assert result[x] == 42


class TestMatchAlternatives:
    def test_alternatives_first(self):
        pat = alternatives(x, y)
        result = match(pat, x)
        assert result.success

    def test_alternatives_second(self):
        pat = alternatives(x, y)
        result = match(pat, y)
        assert result.success

    def test_alternatives_none(self):
        pat = alternatives(x, y)
        result = match(pat, z)
        assert not result.success


class TestMatchPatternTest:
    def test_pattern_test_no_evaluator_fails_safe(self):
        pat = pattern_test(pattern(x), Symbol("NumberQ"))
        result = match(pat, 42)
        assert not result.success

    def test_pattern_test_with_evaluator(self):
        def evaluator(expr):
            return True

        pat = pattern_test(pattern(x), Symbol("NumberQ"))
        result = match(pat, 42, evaluator=evaluator)
        assert result.success
        assert result[x] == 42


class TestMatchRepeated:
    def test_repeated_single(self):
        pat = repeated(pattern(x))
        result = match(pat, 42)
        assert result.success

    def test_repeated_null(self):
        pat = repeated_null(pattern(x))
        result = match(pat, 42)
        assert result.success

    def test_repeated_null_empty(self):
        pat = repeated_null(pattern(x))
        result = match(pat, Symbol("Other"))
        assert result.success


class TestMatchExcept:
    def test_except_excluded(self):
        pat = except_pattern(0)
        result = match(pat, 0)
        assert not result.success

    def test_except_not_excluded(self):
        pat = except_pattern(0)
        result = match(pat, 42)
        assert result.success

    def test_except_with_alternative(self):
        pat = except_pattern(0, blank(Integer))
        result = match(pat, 42)
        assert result.success

    def test_except_alternative_fails(self):
        pat = except_pattern(0, blank(Integer))
        result = match(pat, "hello")
        assert not result.success


class TestMatchVerbatim:
    def test_verbatim_literal(self):
        expr = Expression(Plus, 1, 2)
        pat = verbatim(expr)
        result = match(pat, expr)
        assert result.success

    def test_verbatim_different(self):
        expr = Expression(Plus, 1, 2)
        pat = verbatim(expr)
        result = match(pat, Expression(Plus, 1, 3))
        assert not result.success


class TestMatchHoldPattern:
    def test_hold_pattern_unwraps(self):
        expr = Expression(Plus, x, 1)
        pat = hold_pattern(expr)
        result = match(pat, expr)
        assert result.success


class TestMatchSequence:
    def test_sequence_blank_single(self):
        pat = (blank(),)
        exprs = (42,)
        results = list(match_sequence(pat, exprs))
        assert len(results) == 1

    def test_sequence_blank_multiple(self):
        pat = (blank(), blank())
        exprs = (1, 2)
        results = list(match_sequence(pat, exprs))
        assert len(results) == 1

    def test_blank_seq_matches(self):
        pat = (blank_seq(),)
        exprs = (1, 2, 3)
        results = list(match_sequence(pat, exprs))
        assert len(results) >= 1

    def test_blank_null_seq_empty(self):
        pat = (blank_null_seq(),)
        exprs = ()
        results = list(match_sequence(pat, exprs))
        assert len(results) >= 1


class TestMatchFlat:
    def test_flat_attribute(self):
        from minimatic.pattern.structural import pattern as mk_pattern

        # Plus[Plus[1, 2]] with Flat flattens to Plus[1, 2]
        pat = Expression(Plus, mk_pattern(x), mk_pattern(y))
        expr = Expression(Plus, Expression(Plus, 1, 2))
        result = match(pat, expr, expr_attrs=frozenset({Flat}))
        assert result.success
        assert result[x] == 1
        assert result[y] == 2


class TestMatchOrderless:
    def test_orderless_attribute(self):
        from minimatic.pattern.structural import pattern as mk_pattern

        pat = Expression(Plus, mk_pattern(x), mk_pattern(y))
        expr = Expression(Plus, 2, 1)
        result = match(pat, expr, expr_attrs=frozenset({Orderless}))
        assert result.success
        assert result[x] == 2
        assert result[y] == 1


class TestReplaceWithBindings:
    def test_simple_replacement(self):
        b = Bindings({x: 42})
        result = replace_with_bindings(x, b)
        assert result == 42

    def test_expression_replacement(self):
        b = Bindings({x: 1, y: 2})
        expr = Expression(Plus, x, y)
        result = replace_with_bindings(expr, b)
        assert result.args == (1, 2)

    def test_list_flattening(self):
        b = Bindings({x: Expression(List, 1, 2, 3)})
        expr = Expression(Plus, x)
        result = replace_with_bindings(expr, b)
        assert result.args == (1, 2, 3)

    def test_no_bindings(self):
        result = replace_with_bindings(42, empty_bindings())
        assert result == 42


class TestFindMatches:
    def test_find_in_expression(self):
        expr = Expression(Plus, 1, Expression(Plus, 2, 3))
        results = find_all_matches(blank(Integer), expr)
        assert len(results) == 3

    def test_find_no_matches(self):
        expr = Expression(Plus, "a", "b")
        results = find_all_matches(blank(Integer), expr)
        assert len(results) == 0


class TestMatchResult:
    def test_bool_success(self):
        assert bool(success())

    def test_bool_no_match(self):
        assert not bool(NO_MATCH)

    def test_getitem(self):
        r = match(pattern(x), 42)
        assert r[x] == 42

    def test_get_default(self):
        r = match(pattern(x), 42)
        assert r.get(y, 0) == 0
