"""Tests for Blanks module."""
from __future__ import annotations

import pytest
from src.core.symbol import Symbol
from src.core.expression import Expression
from src.pattern.blanks import (
    Blank, BlankSequence, BlankNullSequence,
    blank, blank_seq, blank_null_seq,
    is_blank, is_blank_sequence, is_blank_null_sequence,
    is_any_blank, is_sequence_blank,
    blank_head_constraint, blank_matches_head,
    blank_min_length, blank_max_length, blank_can_match_empty,
    get_blank, get_blank_seq, get_blank_null_seq,
)


Integer = Symbol("Integer")
List = Symbol("List")


class TestBlankConstructors:
    def test_blank_unconstrained(self):
        b = blank()
        assert b.head == Blank
        assert len(b.args) == 0

    def test_blank_with_head(self):
        b = blank(Integer)
        assert b.head == Blank
        assert b.args[0] == Integer

    def test_blank_bad_head_type(self):
        with pytest.raises(TypeError, match="Symbol"):
            blank("bad")

    def test_blank_seq_unconstrained(self):
        b = blank_seq()
        assert b.head == BlankSequence
        assert len(b.args) == 0

    def test_blank_seq_with_head(self):
        b = blank_seq(Integer)
        assert b.head == BlankSequence
        assert b.args[0] == Integer

    def test_blank_seq_bad_head(self):
        with pytest.raises(TypeError, match="Symbol"):
            blank_seq(42)

    def test_blank_null_seq_unconstrained(self):
        b = blank_null_seq()
        assert b.head == BlankNullSequence

    def test_blank_null_seq_with_head(self):
        b = blank_null_seq(Integer)
        assert b.args[0] == Integer

    def test_blank_null_seq_bad_head(self):
        with pytest.raises(TypeError, match="Symbol"):
            blank_null_seq(3.14)


class TestBlankPredicates:
    def test_is_blank(self):
        assert is_blank(blank())
        assert is_blank(blank(Integer))
        assert not is_blank(blank_seq())

    def test_is_blank_sequence(self):
        assert is_blank_sequence(blank_seq())
        assert not is_blank_sequence(blank())

    def test_is_blank_null_sequence(self):
        assert is_blank_null_sequence(blank_null_seq())
        assert not is_blank_null_sequence(blank_seq())

    def test_is_any_blank(self):
        assert is_any_blank(blank())
        assert is_any_blank(blank_seq())
        assert is_any_blank(blank_null_seq())
        assert not is_any_blank(Symbol("x"))

    def test_is_sequence_blank(self):
        assert is_sequence_blank(blank_seq())
        assert is_sequence_blank(blank_null_seq())
        assert not is_sequence_blank(blank())


class TestBlankUtilities:
    def test_head_constraint_none(self):
        assert blank_head_constraint(blank()) is None

    def test_head_constraint_present(self):
        assert blank_head_constraint(blank(Integer)) == Integer

    def test_head_constraint_bad_type(self):
        with pytest.raises(TypeError, match="blank"):
            blank_head_constraint(Symbol("x"))

    def test_matches_head_no_constraint(self):
        assert blank_matches_head(blank(), 42)
        assert blank_matches_head(blank(), "hello")

    def test_matches_head_integer_constraint(self):
        assert blank_matches_head(blank(Integer), 42)
        assert not blank_matches_head(blank(Integer), 3.14)

    def test_matches_head_list_constraint(self):
        expr = Expression(List, 1, 2)
        assert blank_matches_head(blank(List), expr)
        assert not blank_matches_head(blank(List), 42)

    def test_min_length(self):
        assert blank_min_length(blank()) == 1
        assert blank_min_length(blank_seq()) == 1
        assert blank_min_length(blank_null_seq()) == 0

    def test_max_length(self):
        assert blank_max_length(blank()) == 1
        assert blank_max_length(blank_seq()) == float('inf')
        assert blank_max_length(blank_null_seq()) == float('inf')

    def test_can_match_empty(self):
        assert not blank_can_match_empty(blank())
        assert not blank_can_match_empty(blank_seq())
        assert blank_can_match_empty(blank_null_seq())


class TestCachedBlanks:
    def test_get_blank_returns_same(self):
        assert get_blank() is get_blank()

    def test_get_blank_seq_returns_same(self):
        assert get_blank_seq() is get_blank_seq()

    def test_get_blank_null_seq_returns_same(self):
        assert get_blank_null_seq() is get_blank_null_seq()
