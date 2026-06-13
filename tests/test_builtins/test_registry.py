"""Tests for Builtin Registry module."""
from __future__ import annotations

from src.core.symbol import Symbol
from src.core.expression import Expression
from src.core.attributes import Flat, Orderless, Listable, NumericFunction
from src.builtins.registry import (
    register_builtin, get_builtin, has_builtin,
    builtin_attributes, clear_registry, BuiltinRegistry,
)
from src.eval.context import EvaluationContext

# Force registration of builtins by importing arithmetic
import src.builtins.arithmetic  # noqa: F401


class TestRegistry:
    def test_has_builtin(self):
        Plus = Symbol("Plus")
        assert has_builtin(Plus)

    def test_no_builtin(self):
        assert not has_builtin(Symbol("Unknown"))


class TestBuiltinAttributes:
    def test_plus_attributes(self):
        Plus = Symbol("Plus")
        attrs = builtin_attributes(Plus)
        assert Flat in attrs
        assert Orderless in attrs
        assert Listable in attrs
        assert NumericFunction in attrs

    def test_times_attributes(self):
        Times = Symbol("Times")
        attrs = builtin_attributes(Times)
        assert Flat in attrs
        assert Orderless in attrs

    def test_power_attributes(self):
        Power = Symbol("Power")
        attrs = builtin_attributes(Power)
        assert NumericFunction in attrs
        assert Listable in attrs
        assert Flat not in attrs

    def test_unknown_attributes(self):
        assert builtin_attributes(Symbol("Unknown")) == frozenset()


class TestGetBuiltin:
    def test_get_builtin(self):
        Plus = Symbol("Plus")
        builtin = get_builtin(Plus)
        assert builtin is not None
        assert builtin.symbol == Plus

    def test_get_builtin_unknown(self):
        assert get_builtin(Symbol("Unknown")) is None


class TestBuiltinRegistry:
    def test_custom_registry(self):
        registry = BuiltinRegistry()
        called = [False]

        def custom_impl(expr, ctx):
            called[0] = True
            return 42

        custom_sym = Symbol("Custom")
        registry.register(custom_sym, custom_impl, {Flat})
        assert registry.has(custom_sym)

        builtin = registry.get(custom_sym)
        assert builtin is not None
        assert Flat in builtin.attributes

    def test_registry_chain(self):
        parent = BuiltinRegistry()
        child = BuiltinRegistry(parent=parent)

        sym = Symbol("Test")
        called = [False]

        def impl(expr, ctx):
            called[0] = True
            return 42

        parent.register(sym, impl)
        assert child.has(sym)

    def test_registry_local_override(self):
        parent = BuiltinRegistry()
        child = BuiltinRegistry(parent=parent)

        sym = Symbol("Test")

        def parent_impl(expr, ctx):
            return "parent"

        def child_impl(expr, ctx):
            return "child"

        parent.register(sym, parent_impl)
        child.register(sym, child_impl)

        # Child should return child's version
        builtin = child.get(sym)
        assert builtin is not None


class TestClearRegistry:
    def test_clear_and_restore(self):
        # Save current state
        from src.builtins.registry import _registry
        saved = dict(_registry)
        try:
            clear_registry()
            assert not has_builtin(Symbol("Plus"))
        finally:
            # Restore registry
            _registry.update(saved)
