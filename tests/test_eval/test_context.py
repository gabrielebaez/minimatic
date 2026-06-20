"""Tests for Context module."""

from __future__ import annotations

from minimatic.core.symbol import Symbol
from minimatic.eval.context import (
    ContextChain,
    EvaluationContext,
    GlobalContext,
    get_current_context,
    with_context,
)


class TestEvaluationContext:
    def test_creation(self):
        ctx = EvaluationContext("Test")
        assert ctx.name == "Test"
        assert ctx.parent is None

    def test_symbol_interning(self):
        ctx = EvaluationContext("Test")
        x = Symbol("x")
        ctx.intern_symbol("x", x)
        assert ctx.get_symbol("x") is x

    def test_symbol_lookup_parent(self):
        parent = EvaluationContext("Parent")
        child = EvaluationContext("Child", parent=parent)
        x = Symbol("x")
        parent.intern_symbol("x", x)
        assert child.get_symbol("x") is x

    def test_symbol_not_found(self):
        ctx = EvaluationContext("Test")
        assert ctx.get_symbol("missing") is None


class TestAttributes:
    def test_set_get_attributes(self):
        ctx = EvaluationContext("Test")
        x = Symbol("x")
        Flat = Symbol("Flat")
        ctx.set_attributes(x, frozenset({Flat}))
        assert ctx.get_attributes(x) == frozenset({Flat})

    def test_attributes_empty_default(self):
        ctx = EvaluationContext("Test")
        assert ctx.get_attributes(Symbol("x")) == frozenset()

    def test_clear_attributes(self):
        ctx = EvaluationContext("Test")
        x = Symbol("x")
        ctx.set_attributes(x, frozenset({Symbol("Flat")}))
        ctx.clear_attributes(x)
        assert ctx.get_attributes(x) == frozenset()

    def test_has_attribute(self):
        ctx = EvaluationContext("Test")
        x = Symbol("x")
        Flat = Symbol("Flat")
        ctx.set_attributes(x, frozenset({Flat}))
        assert ctx.has_attribute(x, Flat)
        assert not ctx.has_attribute(x, Symbol("Orderless"))


class TestValueStorage:
    def test_own_values(self):
        ctx = EvaluationContext("Test")
        x = Symbol("x")
        ctx.set_own_values(x, [("pat", "repl", None)])
        assert ctx.get_own_values(x) == [("pat", "repl", None)]

    def test_down_values(self):
        ctx = EvaluationContext("Test")
        f = Symbol("f")
        ctx.set_down_values(f, [("pat", "repl", None)])
        assert ctx.get_down_values(f) == [("pat", "repl", None)]

    def test_up_values(self):
        ctx = EvaluationContext("Test")
        x = Symbol("x")
        ctx.set_up_values(x, [("pat", "repl", None)])
        assert ctx.get_up_values(x) == [("pat", "repl", None)]

    def test_sub_values(self):
        ctx = EvaluationContext("Test")
        f = Symbol("f")
        ctx.set_sub_values(f, [("pat", "repl", None)])
        assert ctx.get_sub_values(f) == [("pat", "repl", None)]

    def test_n_values(self):
        ctx = EvaluationContext("Test")
        f = Symbol("f")
        ctx.set_n_values(f, [("pat", "repl", None)])
        assert ctx.get_n_values(f) == [("pat", "repl", None)]

    def test_default_value(self):
        ctx = EvaluationContext("Test")
        f = Symbol("f")
        ctx.set_default_value(f, "default")
        assert ctx.get_default_value(f) == "default"

    def test_format_values(self):
        ctx = EvaluationContext("Test")
        f = Symbol("f")
        ctx.set_format_values(f, [("pat", "repl", None)])
        assert ctx.get_format_values(f) == [("pat", "repl", None)]

    def test_clear_all_values(self):
        ctx = EvaluationContext("Test")
        x = Symbol("x")
        ctx.set_own_values(x, [("a", "b", None)])
        ctx.set_down_values(x, [("c", "d", None)])
        ctx.clear_all_values(x)
        assert ctx.get_own_values(x) == []
        assert ctx.get_down_values(x) == []


class TestContextStack:
    def test_get_current_context(self):
        ctx = get_current_context()
        assert ctx is GlobalContext

    def test_with_context(self):
        custom = EvaluationContext("Custom")
        before = get_current_context()
        with with_context(custom):
            assert get_current_context() is custom
        assert get_current_context() is before

    def test_nested_contexts(self):
        c1 = EvaluationContext("C1")
        c2 = EvaluationContext("C2")
        with with_context(c1):
            assert get_current_context() is c1
            with with_context(c2):
                assert get_current_context() is c2
            assert get_current_context() is c1


class TestContextChain:
    def test_chain_lookup(self):
        c1 = EvaluationContext("C1")
        c2 = EvaluationContext("C2")
        x = Symbol("x")
        c1.intern_symbol("x", x)
        chain = ContextChain(c1, c2)
        assert chain[x] is x

    def test_chain_not_found(self):
        c1 = EvaluationContext("C1")
        c2 = EvaluationContext("C2")
        chain = ContextChain(c1, c2)
        from pytest import raises

        with raises(KeyError):
            chain[Symbol("missing")]
