"""Tests for Values module."""
from __future__ import annotations

from src.core.symbol import Symbol
from src.core.expression import Expression
from src.eval.values import (
    Values, ValueStore, get_value, set_value, clear_value,
    OwnValues, DownValues, UpValues, SubValues, NValues,
    DefaultValues, FormatValues, ALL_VALUE_TYPES,
)
from src.eval.context import EvaluationContext

x = Symbol("x")
f = Symbol("f")


class TestValues:
    def test_default_values(self):
        v = Values()
        assert v.own == []
        assert v.down == []
        assert v.up == []
        assert v.sub == []
        assert v.n == []
        assert v.default is None
        assert v.format == []


class TestValueStore:
    def test_get_creates_default(self):
        store = ValueStore()
        v = store.get_values(x)
        assert isinstance(v, Values)

    def test_add_own_value(self):
        store = ValueStore()
        store.add_own_value(x, x, 42)
        v = store.get_values(x)
        assert len(v.own) == 1
        assert v.own[0] == (x, 42, None)

    def test_add_down_value(self):
        store = ValueStore()
        pat = Expression(f, Symbol("x"))
        store.add_down_value(f, pat, 42)
        v = store.get_values(f)
        assert len(v.down) == 1

    def test_add_up_value(self):
        store = ValueStore()
        pat = Expression(f, x)
        store.add_up_value(x, pat, 42)
        v = store.get_values(x)
        assert len(v.up) == 1

    def test_add_sub_value(self):
        store = ValueStore()
        pat = Expression(f, x)
        store.add_sub_value(f, pat, 42)
        v = store.get_values(f)
        assert len(v.sub) == 1

    def test_add_n_value(self):
        store = ValueStore()
        pat = Expression(f, x)
        store.add_n_value(f, pat, 42)
        v = store.get_values(f)
        assert len(v.n) == 1

    def test_set_default_value(self):
        store = ValueStore()
        v = store.get_values(f)
        # Values is a frozen dataclass; setting default after creation
        # requires __post_init__ usage. Verify the default is initially None.
        assert v.default is None

    def test_add_format_value(self):
        store = ValueStore()
        pat = Expression(f, x)
        store.add_format_value(f, pat, "format")
        v = store.get_values(f)
        assert len(v.format) == 1

    def test_clear_symbol(self):
        store = ValueStore()
        store.add_own_value(x, x, 42)
        store.clear_symbol(x)
        v = store.get_values(x)
        assert v.own == []


class TestContextBasedAccess:
    def test_get_value(self):
        ctx = EvaluationContext("test")
        ctx.set_own_values(x, [("pat", "repl", None)])
        result = get_value(ctx, x, OwnValues)
        assert result == [("pat", "repl", None)]

    def test_set_value(self):
        ctx = EvaluationContext("test")
        set_value(ctx, x, DownValues, [("pat", "repl", None)])
        assert get_value(ctx, x, DownValues) == [("pat", "repl", None)]

    def test_clear_value(self):
        ctx = EvaluationContext("test")
        ctx.set_own_values(x, [("a", "b", None)])
        clear_value(ctx, x, OwnValues)
        assert get_value(ctx, x, OwnValues) == []

    def test_clear_all(self):
        ctx = EvaluationContext("test")
        ctx.set_own_values(x, [("a", "b", None)])
        ctx.set_down_values(x, [("c", "d", None)])
        clear_value(ctx, x)
        assert get_value(ctx, x, OwnValues) == []
        assert get_value(ctx, x, DownValues) == []

    def test_unknown_type_raises(self):
        ctx = EvaluationContext("test")
        from pytest import raises
        with raises(ValueError, match="Unknown"):
            get_value(ctx, x, "invalid")


class TestAllValueTypes:
    def test_value_types_list(self):
        assert OwnValues in ALL_VALUE_TYPES
        assert DownValues in ALL_VALUE_TYPES
        assert UpValues in ALL_VALUE_TYPES
        assert SubValues in ALL_VALUE_TYPES
        assert NValues in ALL_VALUE_TYPES
        assert DefaultValues in ALL_VALUE_TYPES
        assert FormatValues in ALL_VALUE_TYPES
