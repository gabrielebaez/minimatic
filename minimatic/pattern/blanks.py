"""
Blanks - Wildcard pattern primitives.

Blanks are the fundamental building blocks of pattern matching:
    - Blank (_): Matches any single expression
    - BlankSequence (__): Matches one or more expressions
    - BlankNullSequence (___): Matches zero or more expressions

Each blank type can optionally have a head constraint:
    - Blank[] matches anything
    - Blank[Integer] matches only integers
    - Blank[List] matches only lists

Implementation:
    Blanks are represented as Expression objects with special heads.
    This keeps them consistent with the rest of the expression system
    and allows them to be manipulated like any other expression.

Examples:
    _           →  Blank[]
    _Integer    →  Blank[Integer]
    __          →  BlankSequence[]
    ___Symbol   →  BlankNullSequence[Symbol]
"""

from __future__ import annotations
from typing import Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from minimatic.core.atoms import Element

from minimatic.core.symbol import Symbol
from minimatic.core.expression import Expression, is_expr, head_of


# ═══════════════════════════════════════════════════════════════════════════════
# BLANK HEAD SYMBOLS
# ═══════════════════════════════════════════════════════════════════════════════

# These symbols serve as heads for blank patterns
Blank = Symbol("Blank")
"""Head symbol for single-element wildcard patterns (_)."""

BlankSequence = Symbol("BlankSequence")
"""Head symbol for one-or-more sequence patterns (__)."""

BlankNullSequence = Symbol("BlankNullSequence")
"""Head symbol for zero-or-more sequence patterns (___)."""


# ═══════════════════════════════════════════════════════════════════════════════
# BLANK CONSTRUCTORS
# ═══════════════════════════════════════════════════════════════════════════════

def blank(head: Optional[Symbol] = None) -> Expression:
    """
    Create a Blank pattern that matches any single expression.

    Args:
        head: Optional head constraint. If provided, only matches
              expressions with this head.

    Returns:
        Expression representing Blank[] or Blank[head].

    Examples:
        >>> blank()                    # _ matches anything
        Blank[]
        >>> blank(Symbol("Integer"))   # _Integer matches integers
        Blank[Integer]
        >>> blank(Symbol("List"))      # _List matches lists
        Blank[List]

    Wolfram Equivalent:
        _ or Blank[]
        _h or Blank[h]
    """
    if head is None:
        return Expression(Blank)
    if not isinstance(head, Symbol):
        raise TypeError(f"Blank head constraint must be Symbol, got {type(head).__name__}")
    return Expression(Blank, head)


def blank_seq(head: Optional[Symbol] = None) -> Expression:
    """
    Create a BlankSequence pattern that matches one or more expressions.

    Args:
        head: Optional head constraint for each matched element.

    Returns:
        Expression representing BlankSequence[] or BlankSequence[head].

    Examples:
        >>> blank_seq()                # __ matches one or more of anything
        BlankSequence[]
        >>> blank_seq(Symbol("Integer"))  # __Integer matches one or more integers
        BlankSequence[Integer]

    Wolfram Equivalent:
        __ or BlankSequence[]
        __h or BlankSequence[h]
    """
    if head is None:
        return Expression(BlankSequence)
    if not isinstance(head, Symbol):
        raise TypeError(f"BlankSequence head constraint must be Symbol, got {type(head).__name__}")
    return Expression(BlankSequence, head)


def blank_null_seq(head: Optional[Symbol] = None) -> Expression:
    """
    Create a BlankNullSequence pattern that matches zero or more expressions.

    Args:
        head: Optional head constraint for each matched element.

    Returns:
        Expression representing BlankNullSequence[] or BlankNullSequence[head].

    Examples:
        >>> blank_null_seq()              # ___ matches zero or more of anything
        BlankNullSequence[]
        >>> blank_null_seq(Symbol("Integer"))  # ___Integer
        BlankNullSequence[Integer]

    Wolfram Equivalent:
        ___ or BlankNullSequence[]
        ___h or BlankNullSequence[h]
    """
    if head is None:
        return Expression(BlankNullSequence)
    if not isinstance(head, Symbol):
        raise TypeError(f"BlankNullSequence head constraint must be Symbol, got {type(head).__name__}")
    return Expression(BlankNullSequence, head)


# ═══════════════════════════════════════════════════════════════════════════════
# TYPE PREDICATES
# ═══════════════════════════════════════════════════════════════════════════════

def is_blank(obj: object) -> bool:
    """
    Check if object is a Blank pattern.

    Args:
        obj: The object to check.

    Returns:
        True if obj is Blank[] or Blank[head].

    Examples:
        >>> is_blank(blank())
        True
        >>> is_blank(blank(Symbol("Integer")))
        True
        >>> is_blank(blank_seq())
        False
    """
    return is_expr(obj) and obj.head == Blank


def is_blank_sequence(obj: object) -> bool:
    """
    Check if object is a BlankSequence pattern.

    Args:
        obj: The object to check.

    Returns:
        True if obj is BlankSequence[] or BlankSequence[head].
    """
    return is_expr(obj) and obj.head == BlankSequence


def is_blank_null_sequence(obj: object) -> bool:
    """
    Check if object is a BlankNullSequence pattern.

    Args:
        obj: The object to check.

    Returns:
        True if obj is BlankNullSequence[] or BlankNullSequence[head].
    """
    return is_expr(obj) and obj.head == BlankNullSequence


def is_any_blank(obj: object) -> bool:
    """
    Check if object is any type of blank pattern.

    Args:
        obj: The object to check.

    Returns:
        True if obj is Blank, BlankSequence, or BlankNullSequence.

    Examples:
        >>> is_any_blank(blank())
        True
        >>> is_any_blank(blank_seq())
        True
        >>> is_any_blank(blank_null_seq())
        True
        >>> is_any_blank(Symbol("x"))
        False
    """
    if not is_expr(obj):
        return False
    return obj.head in (Blank, BlankSequence, BlankNullSequence)


def is_sequence_blank(obj: object) -> bool:
    """
    Check if object is a sequence-matching blank (__ or ___).

    Sequence blanks can match multiple elements in an argument list,
    unlike regular Blank which matches exactly one element.

    Args:
        obj: The object to check.

    Returns:
        True if obj is BlankSequence or BlankNullSequence.
    """
    if not is_expr(obj):
        return False
    return obj.head in (BlankSequence, BlankNullSequence)


# ═══════════════════════════════════════════════════════════════════════════════
# BLANK UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def blank_head_constraint(blank_expr: Expression) -> Optional[Symbol]:
    """
    Get the head constraint of a blank pattern.

    Args:
        blank_expr: A blank expression (Blank, BlankSequence, or BlankNullSequence).

    Returns:
        The head constraint Symbol, or None if unconstrained.

    Raises:
        TypeError: If blank_expr is not a blank pattern.

    Examples:
        >>> blank_head_constraint(blank())
        None
        >>> blank_head_constraint(blank(Symbol("Integer")))
        Symbol("Integer")
    """
    if not is_any_blank(blank_expr):
        raise TypeError(f"Expected blank pattern, got {type(blank_expr).__name__}")

    if len(blank_expr) == 0:
        return None
    return blank_expr[0]


def blank_matches_head(blank_expr: Expression, elem: "Element") -> bool:
    """
    Check if an element's head satisfies a blank's head constraint.

    Args:
        blank_expr: A blank pattern (Blank, BlankSequence, or BlankNullSequence).
        elem: The element to check.

    Returns:
        True if the element's head matches the constraint (or no constraint).

    Examples:
        >>> blank_matches_head(blank(), 42)
        True
        >>> blank_matches_head(blank(Symbol("Integer")), 42)
        True
        >>> blank_matches_head(blank(Symbol("Integer")), 3.14)
        False
    """
    constraint = blank_head_constraint(blank_expr)
    if constraint is None:
        return True  # No constraint, matches anything

    elem_head = head_of(elem)
    return elem_head == constraint


def blank_min_length(blank_expr: Expression) -> int:
    """
    Get the minimum number of elements a blank pattern can match.

    Args:
        blank_expr: A blank pattern.

    Returns:
        0 for BlankNullSequence, 1 for Blank and BlankSequence.

    Raises:
        TypeError: If blank_expr is not a blank pattern.
    """
    if not is_any_blank(blank_expr):
        raise TypeError(f"Expected blank pattern, got {type(blank_expr).__name__}")

    if blank_expr.head == BlankNullSequence:
        return 0
    return 1  # Blank and BlankSequence both require at least 1


def blank_max_length(blank_expr: Expression) -> Union[int, float]:
    """
    Get the maximum number of elements a blank pattern can match.

    Args:
        blank_expr: A blank pattern.

    Returns:
        1 for Blank, infinity (float('inf')) for sequence blanks.

    Raises:
        TypeError: If blank_expr is not a blank pattern.
    """
    if not is_any_blank(blank_expr):
        raise TypeError(f"Expected blank pattern, got {type(blank_expr).__name__}")

    if blank_expr.head == Blank:
        return 1
    return float('inf')  # BlankSequence and BlankNullSequence


def blank_can_match_empty(blank_expr: Expression) -> bool:
    """
    Check if a blank pattern can match zero elements.

    Args:
        blank_expr: A blank pattern.

    Returns:
        True only for BlankNullSequence.
    """
    return is_blank_null_sequence(blank_expr)


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE CONSTRUCTORS
# ═══════════════════════════════════════════════════════════════════════════════

# Pre-built unconstrained blanks for common use
_BLANK = blank()
_BLANK_SEQ = blank_seq()
_BLANK_NULL_SEQ = blank_null_seq()


def get_blank() -> Expression:
    """Get a cached unconstrained Blank[] pattern."""
    return _BLANK


def get_blank_seq() -> Expression:
    """Get a cached unconstrained BlankSequence[] pattern."""
    return _BLANK_SEQ


def get_blank_null_seq() -> Expression:
    """Get a cached unconstrained BlankNullSequence[] pattern."""
    return _BLANK_NULL_SEQ
