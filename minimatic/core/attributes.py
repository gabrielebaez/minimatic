"""
Attributes - Evaluation attribute symbols.

Attributes modify how expressions are evaluated. They control:
    - Argument evaluation (Hold attributes)
    - Structural transformations (Flat, Orderless)
    - Protection from modification
    - Numeric behavior

All attributes are Symbols, created at module load time.

Usage:
    from minimatic.core.attributes import HoldAll, Flat, Orderless

    # Create expression with attributes
    expr = Expr(f, x, y, _attrs={HoldAll})

    # Check attributes
    if expr.has_attr(HoldAll):
        # Don't evaluate arguments
        pass
"""

from .symbol import Symbol


# PROTECTION ATTRIBUTES

Protected = Symbol("Protected")
"""Prevents modification of the symbol's definitions."""

ReadProtected = Symbol("ReadProtected")
"""Hides the symbol's definitions from inspection (e.g., Definition, ??)."""

Locked = Symbol("Locked")
"""Prevents any changes to the symbol's attributes."""

Constant = Symbol("Constant")
"""Marks the symbol as a mathematical constant (e.g., Pi, E)."""

Temporary = Symbol("Temporary")
"""Symbol will be automatically removed when no longer referenced."""


# HOLD ATTRIBUTES (Evaluation Control)

HoldFirst = Symbol("HoldFirst")
"""
Don't evaluate the first argument.

Example:
    SetDelayed has HoldFirst, so in f[x_] := x^2,
    the pattern f[x_] is not evaluated.
"""

HoldRest = Symbol("HoldRest")
"""
Don't evaluate arguments after the first.

Example:
    If has HoldRest, so in If[cond, then, else],
    only cond is evaluated initially.
"""

HoldAll = Symbol("HoldAll")
"""
Don't evaluate any arguments.

Example:
    Hold[expr] keeps expr completely unevaluated.
"""

HoldAllComplete = Symbol("HoldAllComplete")
"""
Complete hold — don't evaluate anything, including the head.

This is the strongest hold attribute. It also prevents:
    - Sequence flattening
    - UpValue application

Example:
    HoldComplete[1 + 1] keeps the expression exactly as written.
"""

SequenceHold = Symbol("SequenceHold")
"""
Don't flatten Sequence objects in arguments.

Normally Sequence[a, b] splices into the argument list:
    f[1, Sequence[2, 3], 4] → f[1, 2, 3, 4]

With SequenceHold, the Sequence is preserved.
"""


# NUMERIC HOLD ATTRIBUTES

NHoldFirst = Symbol("NHoldFirst")
"""Don't apply N[] to the first argument."""

NHoldRest = Symbol("NHoldRest")
"""Don't apply N[] to arguments after the first."""

NHoldAll = Symbol("NHoldAll")
"""Don't apply N[] to any arguments."""


# STRUCTURAL ATTRIBUTES

Flat = Symbol("Flat")
"""
Associative — nested expressions with the same head are flattened.

Example:
    Plus has Flat, so Plus[Plus[a, b], c] → Plus[a, b, c]
"""

Orderless = Symbol("Orderless")
"""
Commutative — arguments are automatically sorted into canonical order.

Example:
    Plus has Orderless, so Plus[c, a, b] → Plus[a, b, c]

Sorting uses a canonical ordering: numbers < symbols < expressions.
"""

OneIdentity = Symbol("OneIdentity")
"""
A single-argument expression equals its argument for pattern matching.

Example:
    Plus has OneIdentity, so Plus[x] matches patterns expecting just x.
"""

Listable = Symbol("Listable")
"""
Automatically threads over List arguments.

Example:
    Sin has Listable, so Sin[{a, b, c}] → {Sin[a], Sin[b], Sin[c]}
"""


# FUNCTION TYPE ATTRIBUTES

NumericFunction = Symbol("NumericFunction")
"""
Returns numeric values when given numeric arguments.

This attribute is used by NumericQ and related predicates to determine
if an expression should be considered numeric.

Example:
    Sin has NumericFunction, so NumericQ[Sin[1]] is True.
"""

Stub = Symbol("Stub")
"""
The symbol needs to be loaded from a package.

When a stub symbol is encountered, the system attempts to auto-load
the package that defines it.
"""


# ATTRIBUTE SETS (for convenience)

HOLD_ATTRIBUTES = frozenset({
    HoldFirst,
    HoldRest,
    HoldAll,
    HoldAllComplete,
    SequenceHold,
})
"""All attributes that affect argument evaluation."""

NHOLD_ATTRIBUTES = frozenset({
    NHoldFirst,
    NHoldRest,
    NHoldAll,
})
"""All attributes that affect numeric evaluation."""

STRUCTURAL_ATTRIBUTES = frozenset({
    Flat,
    Orderless,
    OneIdentity,
    Listable,
})
"""All attributes that affect expression structure."""

PROTECTION_ATTRIBUTES = frozenset({
    Protected,
    ReadProtected,
    Locked,
    Constant,
    Temporary,
})
"""All attributes related to symbol protection."""

ALL_ATTRIBUTES = (
    HOLD_ATTRIBUTES 
    | NHOLD_ATTRIBUTES 
    | STRUCTURAL_ATTRIBUTES 
    | PROTECTION_ATTRIBUTES 
    | {NumericFunction, Stub}
)
"""All defined attributes."""


# UTILITY FUNCTIONS

def is_attribute(sym: Symbol) -> bool:
    """
    Check if a symbol is a known attribute.

    Args:
        sym: The symbol to check.

    Returns:
        True if sym is a recognized attribute symbol.
    """
    return sym in ALL_ATTRIBUTES


def holds_first(attrs: frozenset[Symbol]) -> bool:
    """Check if attributes indicate first argument should be held."""
    return bool(attrs & {HoldFirst, HoldAll, HoldAllComplete})


def holds_rest(attrs: frozenset[Symbol]) -> bool:
    """Check if attributes indicate arguments after first should be held."""
    return bool(attrs & {HoldRest, HoldAll, HoldAllComplete})


def holds_all(attrs: frozenset[Symbol]) -> bool:
    """Check if attributes indicate all arguments should be held."""
    return bool(attrs & {HoldAll, HoldAllComplete})


def holds_completely(attrs: frozenset[Symbol]) -> bool:
    """Check if HoldAllComplete is set (strongest hold)."""
    return HoldAllComplete in attrs


def is_flat(attrs: frozenset[Symbol]) -> bool:
    """Check if Flat attribute is set."""
    return Flat in attrs


def is_orderless(attrs: frozenset[Symbol]) -> bool:
    """Check if Orderless attribute is set."""
    return Orderless in attrs


def is_listable(attrs: frozenset[Symbol]) -> bool:
    """Check if Listable attribute is set."""
    return Listable in attrs

def has_attribute(attrs: frozenset[Symbol], attr: Symbol) -> bool:
    """Check if a specific attribute is present."""
    return attr in attrs