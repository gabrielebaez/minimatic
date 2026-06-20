"""Tests for Atoms module."""

from __future__ import annotations

import pytest

from minimatic.core.atoms import (
    atom_head,
    is_atom,
    is_boolean,
    is_complex,
    is_exact,
    is_inexact,
    is_integer,
    is_null,
    is_numeric,
    is_real,
    is_string,
    numeric_tower_promote,
    to_numeric,
)
from minimatic.core.symbol import Symbol


class TestTypePredicates:
    def test_is_atom_int(self):
        assert is_atom(42)

    def test_is_atom_float(self):
        assert is_atom(3.14)

    def test_is_atom_complex(self):
        assert is_atom(1 + 2j)

    def test_is_atom_string(self):
        assert is_atom("hello")

    def test_is_atom_bool(self):
        assert is_atom(True)

    def test_is_atom_none(self):
        assert is_atom(None)

    def test_is_atom_symbol(self):
        assert not is_atom(Symbol("x"))

    def test_is_integer(self):
        assert is_integer(42)
        assert is_integer(-1)
        assert not is_integer(True)
        assert not is_integer(3.14)

    def test_is_real(self):
        assert is_real(3.14)
        assert not is_real(42)  # int is not float
        assert not is_real(1 + 2j)

    def test_is_complex(self):
        assert is_complex(1 + 2j)
        assert not is_complex(42)

    def test_is_string(self):
        assert is_string("hello")
        assert not is_string(42)

    def test_is_boolean(self):
        assert is_boolean(True)
        assert is_boolean(False)
        assert not is_boolean(1)

    def test_is_null(self):
        assert is_null(None)
        assert not is_null(0)

    def test_is_numeric(self):
        assert is_numeric(42)
        assert is_numeric(3.14)
        assert is_numeric(1 + 2j)
        assert not is_numeric(True)
        assert not is_numeric("x")

    def test_is_exact(self):
        assert is_exact(42)
        assert not is_exact(3.14)

    def test_is_inexact(self):
        assert is_inexact(3.14)
        assert is_inexact(1 + 2j)
        assert not is_inexact(42)


class TestAtomHead:
    def test_int(self):
        assert atom_head(42) == Symbol("Integer")

    def test_float(self):
        assert atom_head(3.14) == Symbol("Real")

    def test_complex(self):
        assert atom_head(1 + 2j) == Symbol("Complex")

    def test_string(self):
        assert atom_head("hello") == Symbol("String")

    def test_bool(self):
        assert atom_head(True) == Symbol("Symbol")

    def test_none(self):
        assert atom_head(None) == Symbol("Symbol")

    def test_non_atom_raises(self):
        with pytest.raises(TypeError, match="Not an atom"):
            atom_head(Symbol("x"))


class TestToNumeric:
    def test_int(self):
        assert to_numeric(42) == 42

    def test_float(self):
        assert to_numeric(3.14) == 3.14

    def test_complex(self):
        assert to_numeric(1 + 2j) == 1 + 2j

    def test_string_int(self):
        assert to_numeric("42") == 42

    def test_string_float(self):
        assert to_numeric("3.14") == 3.14

    def test_bool_raises(self):
        with pytest.raises(TypeError, match="bool"):
            to_numeric(True)

    def test_invalid_string_raises(self):
        with pytest.raises(TypeError, match="Cannot convert"):
            to_numeric("abc")


class TestNumericTower:
    def test_all_int(self):
        assert numeric_tower_promote(1, 2, 3) is int

    def test_has_float(self):
        assert numeric_tower_promote(1, 2.0, 3) is float

    def test_has_complex(self):
        assert numeric_tower_promote(1, 2 + 3j) is complex
