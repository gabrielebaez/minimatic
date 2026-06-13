"""Tests for Transforms module."""
from __future__ import annotations

from src.core.symbol import Symbol
from src.core.expression import Expression
from src.eval.transforms import (
    flatten_sequences, apply_flat, apply_orderless,
    apply_listable, canonical_sort, _get_depth, _leaf_count,
)
from src.core.attributes import Flat, Orderless, Listable

Plus = Symbol("Plus")
Times = Symbol("Times")
List = Symbol("List")
Sequence = Symbol("Sequence")
x = Symbol("x")
y = Symbol("y")


class TestFlattenSequences:
    def test_no_sequence(self):
        expr = Expression(Plus, 1, 2)
        result = flatten_sequences(expr)
        assert result == expr

    def test_with_sequence(self):
        seq = Expression(Sequence, 1, 2)
        expr = Expression(Plus, 0, seq, 3)
        result = flatten_sequences(expr)
        assert result.args == (0, 1, 2, 3)

    def test_empty_sequence(self):
        seq = Expression(Sequence)
        expr = Expression(Plus, 0, seq, 3)
        result = flatten_sequences(expr)
        assert result.args == (0, 3)

    def test_hold_sequence(self):
        seq = Expression(Sequence, 1, 2)
        expr = Expression(Plus, 0, seq, 3)
        result = flatten_sequences(expr, hold_sequence=True)
        assert result == expr

    def test_non_expression(self):
        result = flatten_sequences(42)
        assert result == 42


class TestApplyFlat:
    def test_flat_nested(self):
        inner = Expression(Plus, 1, 2)
        outer = Expression(Plus, inner, 3)
        result = apply_flat(outer, is_flat=True)
        assert result.args == (1, 2, 3)

    def test_flat_multiple_nesting(self):
        inner1 = Expression(Plus, 1, 2)
        inner2 = Expression(Plus, 3, 4)
        outer = Expression(Plus, inner1, inner2)
        result = apply_flat(outer, is_flat=True)
        assert result.args == (1, 2, 3, 4)

    def test_flat_not_needed(self):
        expr = Expression(Plus, 1, 2)
        result = apply_flat(expr, is_flat=True)
        assert result == expr

    def test_flat_disabled(self):
        inner = Expression(Plus, 1, 2)
        outer = Expression(Plus, inner, 3)
        result = apply_flat(outer, is_flat=False)
        assert result == outer

    def test_flat_preserves_attrs(self):
        inner = Expression(Plus, 1, 2)
        outer = Expression(Plus, inner, 3, _attrs={Flat})
        result = apply_flat(outer, is_flat=True)
        assert Flat in result.attributes


class TestApplyOrderless:
    def test_orderless_sort(self):
        expr = Expression(Plus, 3, 1, 2)
        result = apply_orderless(expr, is_orderless=True)
        assert result.args == (1, 2, 3)

    def test_orderless_same_order(self):
        expr = Expression(Plus, 1, 2)
        result = apply_orderless(expr, is_orderless=True)
        assert result == expr

    def test_orderless_disabled(self):
        expr = Expression(Plus, 3, 1, 2)
        result = apply_orderless(expr, is_orderless=False)
        assert result == expr

    def test_orderless_single_arg(self):
        expr = Expression(Plus, 1)
        result = apply_orderless(expr, is_orderless=True)
        assert result == expr

    def test_orderless_preserves_attrs(self):
        expr = Expression(Plus, 3, 1, _attrs={Orderless})
        result = apply_orderless(expr, is_orderless=True)
        assert Orderless in result.attributes


class TestCanonicalSort:
    def test_numbers_before_symbols(self):
        result = canonical_sort((Symbol("a"), 3, 1, Symbol("b")))
        assert result[0] == 1
        assert result[1] == 3
        assert isinstance(result[2], Symbol)

    def test_symbols_sorted_alphabetically(self):
        result = canonical_sort((Symbol("b"), Symbol("a")))
        assert result[0].name == "a"
        assert result[1].name == "b"

    def test_strings_before_symbols(self):
        result = canonical_sort((Symbol("a"), "hello"))
        assert result[0] == "hello"
        assert isinstance(result[1], Symbol)


class TestApplyListable:
    def test_listable_single_list(self):
        expr = Expression(Plus, Expression(List, 1, 2, 3), 10)
        result = apply_listable(expr, is_listable=True)
        assert result.head == List
        assert len(result.args) == 3
        for arg in result.args:
            assert arg.head == Plus

    def test_listable_no_lists(self):
        expr = Expression(Plus, 1, 2)
        result = apply_listable(expr, is_listable=True)
        assert result == expr

    def test_listable_disabled(self):
        expr = Expression(Plus, Expression(List, 1, 2), 10)
        result = apply_listable(expr, is_listable=False)
        assert result == expr

    def test_listable_result_is_list(self):
        expr = Expression(Plus, Expression(List, 1, 2), 10, _attrs={Listable})
        result = apply_listable(expr, is_listable=True)
        assert result.head == List
        assert len(result.args) == 2


class TestHelperFunctions:
    def test_get_depth_atom(self):
        assert _get_depth(42) == 0

    def test_get_depth_expression(self):
        expr = Expression(Plus, 1, 2)
        assert _get_depth(expr) == 1

    def test_get_depth_nested(self):
        inner = Expression(Plus, 1, 2)
        outer = Expression(Plus, inner, 3)
        assert _get_depth(outer) == 2

    def test_leaf_count_atom(self):
        assert _leaf_count(42) == 1

    def test_leaf_count_expression(self):
        expr = Expression(Plus, 1, 2)
        assert _leaf_count(expr) == 2

    def test_leaf_count_nested(self):
        inner = Expression(Plus, 1, 2)
        outer = Expression(Plus, inner, 3)
        assert _leaf_count(outer) == 3
