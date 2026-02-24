"""
Atoms - Primitive self-evaluating values.

Atoms are the leaves of expression trees — values that evaluate to themselves.
This module defines:
    - Type aliases for atom types
    - Type predicates for checking atom kinds
    - Head symbols for each atom type

Atom Types:
    - Integer (int): Whole numbers
    - Real (float): Floating-point numbers
    - Complex (complex): Complex numbers
    - String (str): Text strings
    - Boolean (bool): True/False (mapped to symbols)
    - NoneType: Represents Null

Note:
    Python's native types are used directly as atoms rather than wrapping
    them in a Literal class. This keeps the implementation simple and
    allows natural interoperability with Python.
"""

from __future__ import annotations
from typing import Union

from .symbol import Symbol
from .expression import Expression


# TYPE ALIASES

# Atomic types (self-evaluating)
Atom = Union[int, float, complex, str, bool, None]

# Numeric atoms
NumericAtom = Union[int, float, complex]

# All element types
Element = Union[Atom, Symbol, Expression]



# TYPE PREDICATES

def is_atom(obj: object) -> bool:
    return isinstance(obj, (int, float, complex, str, bool, type(None)))


def is_integer(obj: object) -> bool:
    return isinstance(obj, int) and not isinstance(obj, bool)


def is_real(obj: object) -> bool:
    return isinstance(obj, float)


def is_complex(obj: object) -> bool:
    return isinstance(obj, complex)


def is_string(obj: object) -> bool:
    return isinstance(obj, str)


def is_boolean(obj: object) -> bool:
    return isinstance(obj, bool)


def is_null(obj: object) -> bool:
    return obj is None


def is_numeric(obj: object) -> bool:
    if isinstance(obj, bool):
        return False
    return isinstance(obj, (int, float, complex))


def is_exact(obj: object) -> bool:
    """
    Check if an object is an exact numeric value (integer or rational).
    """
    return is_integer(obj)


def is_inexact(obj: object) -> bool:
    """
    Check if an object is an inexact numeric value (float or complex).
    """
    return isinstance(obj, (float, complex))


# HEAD SYMBOLS
def atom_head(obj: Atom) -> "Symbol":
    """
    Get the head symbol for an atom.

    Maps Python types to their Wolfram-style head symbols:
        int     → Integer
        float   → Real
        complex → Complex
        str     → String
        bool    → Symbol (True/False)
        None    → Symbol (Null)

    Args:
        obj: An atom value.

    Returns:
        The Symbol representing the atom's head.

    Raises:
        TypeError: If obj is not an atom.
    """
    from .symbol import Symbol

    # Check bool before int since bool is subclass of int
    if isinstance(obj, bool):
        return Symbol("Symbol")  # True/False are symbols
    if isinstance(obj, int):
        return Symbol("Integer")
    if isinstance(obj, float):
        return Symbol("Real")
    if isinstance(obj, complex):
        return Symbol("Complex")
    if isinstance(obj, str):
        return Symbol("String")
    if obj is None:
        return Symbol("Symbol")  # Null is a symbol

    raise TypeError(f"Not an atom: {type(obj).__name__}")


# CONVERSION UTILITIES
def to_numeric(obj: object) -> NumericAtom:
    """
    Convert an object to a numeric atom if possible.

    Args:
        obj: The object to convert.

    Returns:
        The numeric value.

    Raises:
        TypeError: If obj cannot be converted to numeric.
    """
    if isinstance(obj, bool):
        raise TypeError("Cannot convert bool to numeric")
    if isinstance(obj, (int, float, complex)):
        return obj
    if isinstance(obj, str):
        try:
            if "." in obj or "e" in obj.lower():
                return float(obj)
            return int(obj)
        except ValueError:
            pass
    raise TypeError(f"Cannot convert {type(obj).__name__} to numeric")


def numeric_tower_promote(*values: NumericAtom) -> type:
    """
    Determine the appropriate numeric type for a set of values.

    Follows the numeric tower: int < float < complex

    Args:
        *values: Numeric values to consider.

    Returns:
        The type that can represent all values without loss.

    Examples:
        >>> numeric_tower_promote(1, 2, 3)
        <class 'int'>
        >>> numeric_tower_promote(1, 2.0, 3)
        <class 'float'>
        >>> numeric_tower_promote(1, 2+3j)
        <class 'complex'>
    """
    has_complex = any(isinstance(v, complex) for v in values)
    has_float = any(isinstance(v, float) for v in values)

    if has_complex:
        return complex
    if has_float:
        return float
    return int
