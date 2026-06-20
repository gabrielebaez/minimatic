"""Tests for Bindings module."""

from __future__ import annotations

import pytest

from minimatic.core.symbol import Symbol
from minimatic.pattern.bindings import (
    BindingConflict,
    Bindings,
    bindings_compatible,
    bindings_from_pairs,
    empty_bindings,
    single_binding,
)

x = Symbol("x")
y = Symbol("y")
z = Symbol("z")


class TestBindingsCreation:
    def test_empty(self):
        b = empty_bindings()
        assert len(b) == 0
        assert not b

    def test_from_dict(self):
        b = Bindings({x: 42, y: "hello"})
        assert len(b) == 2

    def test_from_dict_non_symbol_key_raises(self):
        with pytest.raises(TypeError, match="Symbols"):
            Bindings({"bad": 42})

    def test_single_binding(self):
        b = single_binding(x, 42)
        assert len(b) == 1
        assert b[x] == 42

    def test_from_parts(self):
        b = Bindings._from_parts(frozenset({(x, 1), (y, 2)}))
        assert len(b) == 2


class TestBindingsProtocol:
    def test_getitem(self):
        b = Bindings({x: 42})
        assert b[x] == 42

    def test_getitem_keyerror(self):
        b = empty_bindings()
        with pytest.raises(KeyError):
            b[x]

    def test_contains(self):
        b = Bindings({x: 42})
        assert x in b
        assert y not in b

    def test_iter(self):
        b = Bindings({x: 1, y: 2})
        assert set(b) == {x, y}

    def test_len(self):
        b = Bindings({x: 1, y: 2, z: 3})
        assert len(b) == 3

    def test_get_with_default(self):
        b = Bindings({x: 42})
        assert b.get(x) == 42
        assert b.get(y) is None
        assert b.get(y, 0) == 0

    def test_keys_values_items(self):
        b = Bindings({x: 1, y: 2})
        assert set(b.keys()) == {x, y}
        assert set(b.values()) == {1, 2}
        assert set(b.items()) == {(x, 1), (y, 2)}


class TestBindingsImmutability:
    def test_bind_returns_new(self):
        b = empty_bindings()
        b2 = b.bind(x, 42)
        assert len(b) == 0
        assert len(b2) == 1

    def test_bind_all_returns_new(self):
        b = empty_bindings()
        b2 = b.bind_all({x: 1, y: 2})
        assert len(b) == 0
        assert len(b2) == 2

    def test_unbind_returns_new(self):
        b = Bindings({x: 1, y: 2})
        b2 = b.unbind(x)
        assert len(b) == 2
        assert len(b2) == 1
        assert x not in b2

    def test_unbind_nonexistent(self):
        b = Bindings({x: 1})
        b2 = b.unbind(y)
        assert b is b2

    def test_merge_returns_new(self):
        b1 = Bindings({x: 1})
        b2 = Bindings({y: 2})
        b3 = b1.merge(b2)
        assert len(b1) == 1
        assert len(b2) == 1
        assert len(b3) == 2


class TestBindingConflict:
    def test_same_value_ok(self):
        b = Bindings({x: 42})
        b2 = b.bind(x, 42)
        assert b is b2

    def test_different_value_raises(self):
        b = Bindings({x: 42})
        with pytest.raises(BindingConflict):
            b.bind(x, 99)

    def test_merge_conflict_raises(self):
        b1 = Bindings({x: 1})
        b2 = Bindings({x: 2})
        with pytest.raises(BindingConflict):
            b1.merge(b2)


class TestBindingsEquality:
    def test_equal_same_bindings(self):
        b1 = Bindings({x: 1, y: 2})
        b2 = Bindings({x: 1, y: 2})
        assert b1 == b2

    def test_not_equal_different(self):
        b1 = Bindings({x: 1})
        b2 = Bindings({x: 2})
        assert b1 != b2

    def test_hashable(self):
        b1 = Bindings({x: 1, y: 2})
        b2 = Bindings({x: 1, y: 2})
        assert hash(b1) == hash(b2)

    def test_usable_in_set(self):
        b1 = Bindings({x: 1})
        b2 = Bindings({x: 1})
        s = {b1, b2}
        assert len(s) == 1


class TestBindingsCompatibility:
    def test_compatible(self):
        b1 = Bindings({x: 1})
        b2 = Bindings({y: 2})
        assert b1.is_compatible_with(b2)

    def test_compatible_same_values(self):
        b1 = Bindings({x: 1})
        b2 = Bindings({x: 1})
        assert b1.is_compatible_with(b2)

    def test_incompatible(self):
        b1 = Bindings({x: 1})
        b2 = Bindings({x: 2})
        assert not b1.is_compatible_with(b2)

    def test_compatible_function(self):
        b1 = Bindings({x: 1})
        b2 = Bindings({y: 2})
        assert bindings_compatible(b1, b2)


class TestBindingsMisc:
    def test_to_dict(self):
        b = Bindings({x: 42})
        d = b.to_dict()
        assert d == {x: 42}
        assert not isinstance(d, Bindings)

    def test_repr_empty(self):
        assert repr(empty_bindings()) == "Bindings({})"

    def test_repr_nonempty(self):
        b = Bindings({x: 42})
        r = repr(b)
        assert "Bindings" in r
        assert "42" in r

    def test_str_empty(self):
        assert str(empty_bindings()) == "{}"

    def test_str_nonempty(self):
        b = Bindings({x: 42})
        s = str(b)
        assert "42" in s

    def test_bool_empty(self):
        assert not empty_bindings()

    def test_bool_nonempty(self):
        assert Bindings({x: 1})

    def test_merge_empty_left(self):
        b = Bindings({x: 1})
        assert empty_bindings().merge(b) is b

    def test_merge_empty_right(self):
        b = Bindings({x: 1})
        assert b.merge(empty_bindings()) is b

    def test_bindings_from_pairs(self):
        b = bindings_from_pairs((x, 1), (y, 2))
        assert len(b) == 2
        assert b[x] == 1
        assert b[y] == 2
