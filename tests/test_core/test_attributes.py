"""Tests for Attributes module."""

from __future__ import annotations

from src.core.attributes import (
    ALL_ATTRIBUTES,
    HOLD_ATTRIBUTES,
    PROTECTION_ATTRIBUTES,
    STRUCTURAL_ATTRIBUTES,
    Flat,
    Hold,
    HoldAll,
    HoldAllComplete,
    HoldFirst,
    HoldRest,
    Listable,
    Locked,
    OneIdentity,
    Orderless,
    Protected,
    SequenceHold,
    has_attribute,
    holds_all,
    is_attribute,
    is_flat,
    is_listable,
    is_orderless,
)
from src.core.symbol import Symbol


class TestAttributeSymbols:
    def test_all_are_symbols(self):
        for attr in ALL_ATTRIBUTES:
            assert isinstance(attr, Symbol)

    def test_attribute_set_completeness(self):
        assert len(ALL_ATTRIBUTES) >= 14


class TestAttributeSets:
    def test_structural(self):
        assert Flat in STRUCTURAL_ATTRIBUTES
        assert Orderless in STRUCTURAL_ATTRIBUTES
        assert OneIdentity in STRUCTURAL_ATTRIBUTES
        assert Listable in STRUCTURAL_ATTRIBUTES

    def test_protection(self):
        assert Protected in PROTECTION_ATTRIBUTES
        assert Locked in PROTECTION_ATTRIBUTES

    def test_hold(self):
        assert Hold in HOLD_ATTRIBUTES
        assert HoldAll in HOLD_ATTRIBUTES
        assert HoldFirst in HOLD_ATTRIBUTES
        assert HoldRest in HOLD_ATTRIBUTES
        assert HoldAllComplete in HOLD_ATTRIBUTES
        assert SequenceHold in HOLD_ATTRIBUTES


class TestUtilityFunctions:
    def test_is_attribute(self):
        assert is_attribute(Flat)
        assert is_attribute(Protected)
        assert not is_attribute(Symbol("Unknown"))

    def test_holds_all(self):
        assert holds_all(frozenset({Hold}))
        assert holds_all(frozenset({HoldAll}))
        assert holds_all(frozenset({HoldAllComplete}))
        assert not holds_all(frozenset({HoldFirst}))

    def test_is_flat(self):
        assert is_flat(frozenset({Flat}))
        assert not is_flat(frozenset())

    def test_is_orderless(self):
        assert is_orderless(frozenset({Orderless}))
        assert not is_orderless(frozenset())

    def test_is_listable(self):
        assert is_listable(frozenset({Listable}))
        assert not is_listable(frozenset())

    def test_has_attribute(self):
        attrs = frozenset({Flat, Orderless})
        assert has_attribute(attrs, Flat)
        assert not has_attribute(attrs, HoldAll)
