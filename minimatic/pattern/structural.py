"""
Structural Patterns - Pattern combinators and named patterns.

This module provides higher-level pattern constructs:
    - Pattern: Named patterns (x_)
    - Condition: Conditional patterns (/;)
    - Alternatives: Alternative patterns (|)
    - PatternTest: Test patterns (?)
    - Optional: Optional patterns with defaults
    - Repeated: Repeated patterns (..)
    - Except: Exclusion patterns
    - Verbatim: Literal matching
    - HoldPattern: Hold pattern during evaluation

These constructs combine with blanks to form complex patterns.

Examples:
    x_                  Pattern[x, Blank[]]
    x_Integer           Pattern[x, Blank[Integer]]
    x_ /; x > 0         Condition[Pattern[x, Blank[]], Greater[x, 0]]
    a | b               Alternatives[a, b]
    x_?NumberQ          PatternTest[Pattern[x, Blank[]], NumberQ]
    x_: 0               Optional[Pattern[x, Blank[]], 0]
"""

from __future__ import annotations
from typing import Optional, Union, Any, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from core.atoms import Element

from minimatic.core.symbol import Symbol
from minimatic.core.expression import Expression, is_expr

from .blanks import (
    Blank,
    BlankSequence,
    BlankNullSequence,
    blank,
    is_any_blank,
)


# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN HEAD SYMBOLS
# ═══════════════════════════════════════════════════════════════════════════════

Pattern = Symbol("Pattern")
"""Head for named patterns: Pattern[name, blank]."""

Condition = Symbol("Condition")
"""Head for conditional patterns: Condition[pattern, test]."""

Alternatives = Symbol("Alternatives")
"""Head for alternative patterns: Alternatives[p1, p2, ...]."""

PatternTest = Symbol("PatternTest")
"""Head for test patterns: PatternTest[pattern, testFunc]."""

Optional = Symbol("Optional")
"""Head for optional patterns: Optional[pattern, default]."""

Repeated = Symbol("Repeated")
"""Head for one-or-more repetition: Repeated[pattern]."""

RepeatedNull = Symbol("RepeatedNull")
"""Head for zero-or-more repetition: RepeatedNull[pattern]."""

Except = Symbol("Except")
"""Head for exclusion patterns: Except[pattern] or Except[pattern, alternative]."""

Verbatim = Symbol("Verbatim")
"""Head for literal matching: Verbatim[expr]."""

HoldPattern = Symbol("HoldPattern")
"""Head to hold pattern during evaluation: HoldPattern[pattern]."""


# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN CONSTRUCTORS
# ═══════════════════════════════════════════════════════════════════════════════

def pattern(name: Symbol, pat: Optional[Expression] = None) -> Expression:
    """
    Create a named pattern.

    A named pattern binds the matched expression to a symbol name,
    allowing it to be referenced in the replacement or condition.

    Args:
        name: The symbol to bind the match to.
        pat: The pattern to match. Defaults to Blank[] if not provided.

    Returns:
        Expression representing Pattern[name, pat].

    Examples:
        >>> x = Symbol("x")
        >>> pattern(x)                    # x_ 
        Pattern[x, Blank[]]
        >>> pattern(x, blank(Symbol("Integer")))  # x_Integer
        Pattern[x, Blank[Integer]]

    Wolfram Equivalent:
        x_ or Pattern[x, Blank[]]
        x_h or Pattern[x, Blank[h]]
    """
    if not isinstance(name, Symbol):
        raise TypeError(f"Pattern name must be Symbol, got {type(name).__name__}")

    if pat is None:
        pat = blank()

    return Expression(Pattern, name, pat)


def condition(pat: Expression, test: Expression) -> Expression:
    """
    Create a conditional pattern.

    A conditional pattern only matches if both the pattern matches
    AND the test expression evaluates to True.

    Args:
        pat: The pattern that must match.
        test: The condition that must be True (can reference bound names).

    Returns:
        Expression representing Condition[pat, test].

    Examples:
        >>> x = Symbol("x")
        >>> Greater = Symbol("Greater")
        >>> # x_ /; x > 0
        >>> condition(pattern(x), Expression(Greater, x, 0))
        Condition[Pattern[x, Blank[]], Greater[x, 0]]

    Wolfram Equivalent:
        pattern /; test or Condition[pattern, test]
    """
    return Expression(Condition, pat, test)


def alternatives(*patterns: Expression) -> Expression:
    """
    Create an alternatives pattern.

    Matches if any of the given patterns matches. Patterns are tried
    in order; the first successful match is used.

    Args:
        *patterns: Two or more patterns to try.

    Returns:
        Expression representing Alternatives[p1, p2, ...].

    Raises:
        ValueError: If fewer than 2 patterns provided.

    Examples:
        >>> a, b = Symbol("a"), Symbol("b")
        >>> alternatives(a, b)   # a | b
        Alternatives[a, b]

    Wolfram Equivalent:
        a | b | c or Alternatives[a, b, c]
    """
    if len(patterns) < 2:
        raise ValueError("Alternatives requires at least 2 patterns")
    return Expression(Alternatives, *patterns)


def pattern_test(pat: Expression, test: Symbol) -> Expression:
    """
    Create a pattern test.

    A pattern test matches if the pattern matches AND applying the
    test function to the matched value returns True.

    Args:
        pat: The pattern that must match.
        test: A symbol naming a test function (e.g., NumberQ, IntegerQ).

    Returns:
        Expression representing PatternTest[pat, test].

    Examples:
        >>> x = Symbol("x")
        >>> NumberQ = Symbol("NumberQ")
        >>> pattern_test(pattern(x), NumberQ)   # x_?NumberQ
        PatternTest[Pattern[x, Blank[]], NumberQ]

    Wolfram Equivalent:
        pattern?test or PatternTest[pattern, test]
    """
    return Expression(PatternTest, pat, test)


def optional(pat: Expression, default: "Element" = None) -> Expression:
    """
    Create an optional pattern with a default value.

    An optional pattern can match either the given pattern or nothing.
    If it matches nothing, the default value is used.

    Args:
        pat: The pattern that may or may not be present.
        default: The default value if pattern is absent.

    Returns:
        Expression representing Optional[pat] or Optional[pat, default].

    Examples:
        >>> x = Symbol("x")
        >>> optional(pattern(x), 0)   # x_: 0
        Optional[Pattern[x, Blank[]], 0]

    Wolfram Equivalent:
        pattern: default or Optional[pattern, default]
    """
    if default is None:
        return Expression(Optional, pat)
    return Expression(Optional, pat, default)


def repeated(pat: Expression, spec: Optional[Expression] = None) -> Expression:
    """
    Create a repeated pattern (one or more).

    Matches one or more occurrences of the given pattern.

    Args:
        pat: The pattern to repeat.
        spec: Optional repetition specification (e.g., {2}, {2, 5}).

    Returns:
        Expression representing Repeated[pat] or Repeated[pat, spec].

    Examples:
        >>> x = Symbol("x")
        >>> repeated(pattern(x))   # x_..
        Repeated[Pattern[x, Blank[]]]

    Wolfram Equivalent:
        pattern.. or Repeated[pattern]
    """
    if spec is None:
        return Expression(Repeated, pat)
    return Expression(Repeated, pat, spec)


def repeated_null(pat: Expression, spec: Optional[Expression] = None) -> Expression:
    """
    Create a repeated null pattern (zero or more).

    Matches zero or more occurrences of the given pattern.

    Args:
        pat: The pattern to repeat.
        spec: Optional repetition specification.

    Returns:
        Expression representing RepeatedNull[pat].

    Wolfram Equivalent:
        pattern... or RepeatedNull[pattern]
    """
    if spec is None:
        return Expression(RepeatedNull, pat)
    return Expression(RepeatedNull, pat, spec)


def except_pattern(
    excluded: Expression,
    alternative: Optional[Expression] = None
) -> Expression:
    """
    Create an exception pattern.

    Matches anything except what the excluded pattern matches.
    Optionally, can specify an alternative that must also match.

    Args:
        excluded: Pattern that must NOT match.
        alternative: If given, pattern that MUST match.

    Returns:
        Expression representing Except[excluded] or Except[excluded, alternative].

    Examples:
        >>> # Match anything except 0
        >>> except_pattern(0)
        Except[0]
        >>> # Match any integer except 0
        >>> Integer = Symbol("Integer")
        >>> except_pattern(0, blank(Integer))
        Except[0, Blank[Integer]]

    Wolfram Equivalent:
        Except[c] or Except[c, pattern]
    """
    if alternative is None:
        return Expression(Except, excluded)
    return Expression(Except, excluded, alternative)


def verbatim(expr: Expression) -> Expression:
    """
    Create a verbatim (literal) pattern.

    Matches the expression literally, without interpreting any
    pattern constructs within it.

    Args:
        expr: The expression to match literally.

    Returns:
        Expression representing Verbatim[expr].

    Examples:
        >>> # Match the literal pattern Blank[], not any expression
        >>> verbatim(blank())
        Verbatim[Blank[]]

    Wolfram Equivalent:
        Verbatim[expr]
    """
    return Expression(Verbatim, expr)


def hold_pattern(pat: Expression) -> Expression:
    """
    Create a held pattern.

    Prevents the pattern from being evaluated during rule application.
    The pattern inside is used for matching, but not evaluated first.

    Args:
        pat: The pattern to hold.

    Returns:
        Expression representing HoldPattern[pat].

    Examples:
        >>> Plus = Symbol("Plus")
        >>> x = Symbol("x")
        >>> # Match literal Plus[x, 1], not evaluated form
        >>> hold_pattern(Expression(Plus, x, 1))
        HoldPattern[Plus[x, 1]]

    Wolfram Equivalent:
        HoldPattern[pattern]
    """
    return Expression(HoldPattern, pat)


# ═══════════════════════════════════════════════════════════════════════════════
# TYPE PREDICATES
# ═══════════════════════════════════════════════════════════════════════════════

def is_pattern(obj: object) -> bool:
    """Check if object is a Pattern expression."""
    return is_expr(obj) and obj.head == Pattern


def is_condition(obj: object) -> bool:
    """Check if object is a Condition expression."""
    return is_expr(obj) and obj.head == Condition


def is_alternatives(obj: object) -> bool:
    """Check if object is an Alternatives expression."""
    return is_expr(obj) and obj.head == Alternatives


def is_pattern_test(obj: object) -> bool:
    """Check if object is a PatternTest expression."""
    return is_expr(obj) and obj.head == PatternTest


def is_optional(obj: object) -> bool:
    """Check if object is an Optional expression."""
    return is_expr(obj) and obj.head == Optional


def is_repeated(obj: object) -> bool:
    """Check if object is a Repeated expression."""
    return is_expr(obj) and obj.head == Repeated


def is_repeated_null(obj: object) -> bool:
    """Check if object is a RepeatedNull expression."""
    return is_expr(obj) and obj.head == RepeatedNull


def is_except(obj: object) -> bool:
    """Check if object is an Except expression."""
    return is_expr(obj) and obj.head == Except


def is_verbatim(obj: object) -> bool:
    """Check if object is a Verbatim expression."""
    return is_expr(obj) and obj.head == Verbatim


def is_hold_pattern(obj: object) -> bool:
    """Check if object is a HoldPattern expression."""
    return is_expr(obj) and obj.head == HoldPattern


def is_pattern_construct(obj: object) -> bool:
    """
    Check if object is any pattern construct.

    Returns True for Pattern, Condition, Alternatives, PatternTest,
    Optional, Repeated, RepeatedNull, Except, Verbatim, HoldPattern,
    and all blank types.
    """
    if not is_expr(obj):
        return False
    return obj.head in (
        Pattern, Condition, Alternatives, PatternTest,
        Optional, Repeated, RepeatedNull, Except, Verbatim, HoldPattern,
        Blank, BlankSequence, BlankNullSequence,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def pattern_name(pat: Expression) -> Optional[Symbol]:
    """
    Extract the name from a Pattern expression.

    Args:
        pat: A Pattern expression.

    Returns:
        The bound symbol name, or None if not a Pattern.

    Examples:
        >>> x = Symbol("x")
        >>> pattern_name(pattern(x))
        Symbol("x")
        >>> pattern_name(blank())
        None
    """
    if is_pattern(pat) and len(pat) >= 1:
        return pat[0]
    return None


def pattern_blank(pat: Expression) -> Optional[Expression]:
    """
    Extract the blank/pattern from a Pattern expression.

    Args:
        pat: A Pattern expression.

    Returns:
        The blank portion, or None if not a Pattern.

    Examples:
        >>> x = Symbol("x")
        >>> pattern_blank(pattern(x, blank(Symbol("Integer"))))
        Blank[Integer]
    """
    if is_pattern(pat) and len(pat) >= 2:
        return pat[1]
    return None


def get_default_value(opt: Expression) -> Optional["Element"]:
    """
    Extract the default value from an Optional expression.

    Args:
        opt: An Optional expression.

    Returns:
        The default value, or None if not specified or not Optional.
    """
    if is_optional(opt) and len(opt) >= 2:
        return opt[1]
    return None


def get_condition_test(cond: Expression) -> Optional[Expression]:
    """
    Extract the test expression from a Condition.

    Args:
        cond: A Condition expression.

    Returns:
        The test expression, or None if not a Condition.
    """
    if is_condition(cond) and len(cond) >= 2:
        return cond[1]
    return None


def get_condition_pattern(cond: Expression) -> Optional[Expression]:
    """
    Extract the pattern from a Condition.

    Args:
        cond: A Condition expression.

    Returns:
        The pattern portion, or None if not a Condition.
    """
    if is_condition(cond) and len(cond) >= 1:
        return cond[0]
    return None


def unwrap_hold_pattern(pat: Expression) -> Expression:
    """
    Unwrap HoldPattern if present, otherwise return as-is.

    Args:
        pat: Any pattern expression.

    Returns:
        The inner pattern if HoldPattern, otherwise the input.
    """
    if is_hold_pattern(pat) and len(pat) >= 1:
        return pat[0]
    return pat


def collect_pattern_names(pat: "Element") -> set[Symbol]:
    """
    Collect all named pattern variables in a pattern.

    Recursively traverses the pattern to find all Pattern[name, _]
    constructs and returns the set of bound names.

    Args:
        pat: A pattern expression.

    Returns:
        Set of all Symbol names bound by Pattern constructs.

    Examples:
        >>> x, y = Symbol("x"), Symbol("y")
        >>> Plus = Symbol("Plus")
        >>> pat = Expression(Plus, pattern(x), pattern(y))
        >>> collect_pattern_names(pat)
        {Symbol("x"), Symbol("y")}
    """
    names: set[Symbol] = set()

    def collect(p: "Element") -> None:
        if is_pattern(p):
            name = pattern_name(p)
            if name is not None:
                names.add(name)
            # Also check nested pattern
            inner = pattern_blank(p)
            if inner is not None:
                collect(inner)
        elif is_expr(p):
            for arg in p.args:
                collect(arg)

    collect(pat)
    return names
