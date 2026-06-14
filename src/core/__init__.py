"""
Minimatic Core - Fundamental data structures for symbolic computation.

This module provides the foundational types:
    - Symbol: Immutable symbolic identifiers
    - Expr: Immutable symbolic expressions (head + arguments + attributes)
    - Atoms: Numeric and string literals

All core types are tuple-based for immutability, hashability, and efficiency.
"""

from .atoms import (
    Atom,
    Element,
    atom_head,
    is_atom,
    is_integer,
    is_numeric,
    is_real,
    is_string,
)
from .attributes import (
    ALL_ATTRIBUTES,
    # Attribute sets
    HOLD_ATTRIBUTES,
    PROTECTION_ATTRIBUTES,
    STRUCTURAL_ATTRIBUTES,
    Constant,
    # Structural
    Flat,
    # Hold attributes
    Hold,
    HoldAll,
    HoldAllComplete,
    HoldFirst,
    HoldRest,
    Listable,
    Locked,
    # Function types
    NumericFunction,
    OneIdentity,
    Orderless,
    # Protection
    Protected,
    ReadProtected,
    SequenceHold,
    Temporary,
)
from .expression import (
    Expression,
    attrs_of,
    has_attr,
    head_of,
    is_expr,
    tail_of,
)
from .symbol import (
    Symbol,
    clear_symbol_cache,
    gensym,
    is_symbol,
    symbol,
)

__all__ = [
    # Symbol
    "Symbol",
    "symbol",
    "is_symbol",
    "gensym",
    "clear_symbol_cache",
    # Expression
    "Expression",
    "is_expr",
    "head_of",
    "tail_of",
    "attrs_of",
    "has_attr",
    # Atoms
    "Atom",
    "Element",
    "is_atom",
    "is_integer",
    "is_real",
    "is_string",
    "is_numeric",
    "atom_head",
    # Attributes
    "Protected",
    "ReadProtected",
    "Locked",
    "Constant",
    "Temporary",
    "Hold",
    "HoldAll",
    "HoldFirst",
    "HoldRest",
    "HoldAllComplete",
    "SequenceHold",
    "Flat",
    "Orderless",
    "OneIdentity",
    "Listable",
    "NumericFunction",
    "HOLD_ATTRIBUTES",
    "STRUCTURAL_ATTRIBUTES",
    "PROTECTION_ATTRIBUTES",
    "ALL_ATTRIBUTES",
]
