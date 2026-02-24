"""
Minimatic Core - Fundamental data structures for symbolic computation.

This module provides the foundational types:
    - Symbol: Immutable symbolic identifiers
    - Expr: Immutable symbolic expressions (head + arguments + attributes)
    - Atoms: Numeric and string literals

All core types are tuple-based for immutability, hashability, and efficiency.
"""

from .symbol import (
    Symbol,
    symbol,
    is_symbol,
    gensym,
    clear_symbol_cache,
)

from .expression import (
    Expression,
    is_expr,
    head_of,
    tail_of,
    attrs_of,
    has_attr,
    map_args,
    replace_head,
    replace_tail,
    replace_attrs,
)

from .atoms import (
    Atom,
    Element,
    is_atom,
    is_integer,
    is_real,
    is_string,
    is_numeric,
    atom_head,
)

from .attributes import (
    # Protection
    Protected,
    ReadProtected,
    Locked,
    Constant,
    Temporary,
    # Hold attributes
    HoldFirst,
    HoldRest,
    HoldAll,
    HoldAllComplete,
    SequenceHold,
    # Numeric hold
    NHoldFirst,
    NHoldRest,
    NHoldAll,
    # Structural
    Flat,
    Orderless,
    OneIdentity,
    Listable,
    # Function types
    NumericFunction,
    # Attribute sets
    HOLD_ATTRIBUTES,
    STRUCTURAL_ATTRIBUTES,
    PROTECTION_ATTRIBUTES,
    ALL_ATTRIBUTES,
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
    "map_args",
    "replace_head",
    "replace_tail",
    "replace_attrs",
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
    "HoldFirst",
    "HoldRest",
    "HoldAll",
    "HoldAllComplete",
    "SequenceHold",
    "NHoldFirst",
    "NHoldRest",
    "NHoldAll",
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
