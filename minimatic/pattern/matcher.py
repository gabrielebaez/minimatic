"""
Matcher - Pattern matching engine.

This module provides the core pattern matching functionality:
    - match(): Match a pattern against an expression
    - matches(): Check if pattern matches (boolean)
    - find_matches(): Find all matches in an expression
    - replace_with_bindings(): Substitute bound values

The matcher handles:
    - Blank patterns (_, __, ___)
    - Named patterns (Pattern[x, _])
    - Conditional patterns (Condition[pat, test])
    - Alternatives (Alternatives[a, b])
    - Structural matching (head + arguments)
    - Flat/Orderless attributes
    - Sequence patterns

Usage:
    from minimatic.pattern import match, matches, Bindings

    result = match(pattern, expression)
    if result is not NO_MATCH:
        print(result[Symbol("x")])  # Access bound value

    if matches(pattern, expression):
        print("Pattern matches!")
"""

from __future__ import annotations
from typing import (
    Optional,
    Union,
    List,
    Tuple,
    Iterator,
    Callable,
    TYPE_CHECKING,
)
from itertools import permutations, combinations
from dataclasses import dataclass

if TYPE_CHECKING:
    from minimatic.core.atoms import Element

from minimatic.core.symbol import Symbol, is_symbol
from minimatic.core.expression import Expression, is_expr, head_of
from minimatic.core.atoms import is_atom
from minimatic.core.attributes import Flat, Orderless

from .bindings import Bindings, empty_bindings, BindingConflict
from .blanks import (
    Blank,
    BlankSequence,
    BlankNullSequence,
    is_blank,
    is_blank_sequence,
    is_blank_null_sequence,
    is_any_blank,
    is_sequence_blank,
    blank_head_constraint,
    blank_matches_head,
)
from .structural import (
    Pattern,
    Condition,
    Alternatives,
    PatternTest,
    Optional as OptionalPattern,
    Repeated,
    RepeatedNull,
    Except,
    Verbatim,
    HoldPattern,
    is_pattern,
    is_condition,
    is_alternatives,
    is_pattern_test,
    is_optional,
    is_repeated,
    is_repeated_null,
    is_except,
    is_verbatim,
    is_hold_pattern,
    pattern_name,
    pattern_blank,
    get_condition_test,
    get_condition_pattern,
    unwrap_hold_pattern,
)


# ═══════════════════════════════════════════════════════════════════════════════
# MATCH RESULT TYPE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class MatchResult:
    """
    Result of a pattern match attempt.

    Attributes:
        success: Whether the match succeeded.
        bindings: The variable bindings if successful.
    """
    success: bool
    bindings: Bindings

    def __bool__(self) -> bool:
        """Allow using MatchResult in boolean context."""
        return self.success

    def __getitem__(self, key: Symbol) -> "Element":
        """Access bindings directly."""
        return self.bindings[key]

    def get(self, key: Symbol, default: "Element" = None) -> "Element":
        """Get binding with default."""
        return self.bindings.get(key, default)


# Sentinel for failed matches
NO_MATCH = MatchResult(success=False, bindings=empty_bindings())


def success(bindings: Optional[Bindings] = None) -> MatchResult:
    """Create a successful match result."""
    if bindings is None:
        bindings = empty_bindings()
    return MatchResult(success=True, bindings=bindings)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN MATCHING FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def match(
    pattern: "Element",
    expr: "Element",
    bindings: Optional[Bindings] = None,
    evaluator: Optional[Callable[["Element"], "Element"]] = None,
) -> MatchResult:
    """
    Match a pattern against an expression.

    This is the main entry point for pattern matching. It attempts to
    match the pattern against the expression, returning bindings if
    successful or NO_MATCH if unsuccessful.

    Args:
        pattern: The pattern to match.
        expr: The expression to match against.
        bindings: Optional initial bindings (for nested matching).
        evaluator: Optional evaluator for Condition tests.

    Returns:
        MatchResult with success=True and bindings if matched,
        or NO_MATCH (success=False) if not matched.

    Examples:
        >>> x = Symbol("x")
        >>> from minimatic.pattern import pattern, blank, match
        >>> pat = pattern(x)  # x_
        >>> result = match(pat, 42)
        >>> result.success
        True
        >>> result[x]
        42
    """
    if bindings is None:
        bindings = empty_bindings()

    return _match_impl(pattern, expr, bindings, evaluator)


def matches(
    pattern: "Element",
    expr: "Element",
    evaluator: Optional[Callable[["Element"], "Element"]] = None,
) -> bool:
    """
    Check if a pattern matches an expression.

    Convenience function that returns just True/False.

    Args:
        pattern: The pattern to match.
        expr: The expression to match against.
        evaluator: Optional evaluator for Condition tests.

    Returns:
        True if pattern matches, False otherwise.
    """
    return match(pattern, expr, evaluator=evaluator).success


def match_sequence(
    patterns: Tuple["Element", ...],
    exprs: Tuple["Element", ...],
    bindings: Optional[Bindings] = None,
    evaluator: Optional[Callable[["Element"], "Element"]] = None,
    flat: bool = False,
    orderless: bool = False,
) -> Iterator[Bindings]:
    """
    Match a sequence of patterns against a sequence of expressions.

    This handles sequence patterns (__, ___) which can match multiple
    elements. It yields all possible ways to match.

    Args:
        patterns: Tuple of patterns.
        exprs: Tuple of expressions to match.
        bindings: Initial bindings.
        evaluator: Optional evaluator for conditions.
        flat: If True, handle Flat attribute (associative).
        orderless: If True, handle Orderless attribute (commutative).

    Yields:
        Bindings for each successful match.
    """
    if bindings is None:
        bindings = empty_bindings()

    yield from _match_sequence_impl(
        patterns, exprs, bindings, evaluator, flat, orderless
    )


# ═══════════════════════════════════════════════════════════════════════════════
# INTERNAL MATCHING IMPLEMENTATION
# ═══════════════════════════════════════════════════════════════════════════════

def _match_impl(
    pattern: "Element",
    expr: "Element",
    bindings: Bindings,
    evaluator: Optional[Callable[["Element"], "Element"]],
) -> MatchResult:
    """Internal implementation of pattern matching."""

    # ─────────────────────────────────────────────────────────────────────────
    # Handle HoldPattern - unwrap and continue
    # ─────────────────────────────────────────────────────────────────────────
    if is_hold_pattern(pattern):
        pattern = unwrap_hold_pattern(pattern)

    # ─────────────────────────────────────────────────────────────────────────
    # Handle Verbatim - literal matching
    # ─────────────────────────────────────────────────────────────────────────
    if is_verbatim(pattern):
        if len(pattern) >= 1:
            return success(bindings) if pattern[0] == expr else NO_MATCH
        return NO_MATCH

    # ─────────────────────────────────────────────────────────────────────────
    # Handle Blank patterns (_, _h)
    # ─────────────────────────────────────────────────────────────────────────
    if is_blank(pattern):
        if blank_matches_head(pattern, expr):
            return success(bindings)
        return NO_MATCH

    # ─────────────────────────────────────────────────────────────────────────
    # Handle Named patterns (Pattern[name, blank])
    # ─────────────────────────────────────────────────────────────────────────
    if is_pattern(pattern):
        name = pattern_name(pattern)
        inner = pattern_blank(pattern)

        # First check if inner pattern matches
        if inner is not None:
            inner_result = _match_impl(inner, expr, bindings, evaluator)
            if not inner_result.success:
                return NO_MATCH
            bindings = inner_result.bindings

        # Then try to bind the name
        if name is not None:
            try:
                bindings = bindings.bind(name, expr)
            except BindingConflict:
                return NO_MATCH

        return success(bindings)

    # ─────────────────────────────────────────────────────────────────────────
    # Handle Condition patterns (pat /; test)
    # ─────────────────────────────────────────────────────────────────────────
    if is_condition(pattern):
        inner_pat = get_condition_pattern(pattern)
        test = get_condition_test(pattern)

        if inner_pat is None:
            return NO_MATCH

        # First match the inner pattern
        inner_result = _match_impl(inner_pat, expr, bindings, evaluator)
        if not inner_result.success:
            return NO_MATCH

        # Then evaluate the condition
        if test is not None and evaluator is not None:
            # Substitute bindings into test
            substituted = replace_with_bindings(test, inner_result.bindings)
            # Evaluate the test
            result = evaluator(substituted)
            # Check if result is True
            if result != Symbol("True") and result is not True:
                return NO_MATCH

        return success(inner_result.bindings)

    # ─────────────────────────────────────────────────────────────────────────
    # Handle Alternatives (a | b | c)
    # ─────────────────────────────────────────────────────────────────────────
    if is_alternatives(pattern):
        for alt in pattern.args:
            result = _match_impl(alt, expr, bindings, evaluator)
            if result.success:
                return result
        return NO_MATCH

    # ─────────────────────────────────────────────────────────────────────────
    # Handle PatternTest (pat?test)
    # ─────────────────────────────────────────────────────────────────────────
    if is_pattern_test(pattern):
        if len(pattern) < 2:
            return NO_MATCH

        inner_pat = pattern[0]
        test_func = pattern[1]

        # First match the inner pattern
        inner_result = _match_impl(inner_pat, expr, bindings, evaluator)
        if not inner_result.success:
            return NO_MATCH

        # Then apply the test function
        if evaluator is not None:
            test_expr = Expression(test_func, expr)
            result = evaluator(test_expr)
            if result != Symbol("True") and result is not True:
                return NO_MATCH

        return success(inner_result.bindings)

    # ─────────────────────────────────────────────────────────────────────────
    # Handle Except (Except[c] or Except[c, pat])
    # ─────────────────────────────────────────────────────────────────────────
    if is_except(pattern):
        if len(pattern) < 1:
            return NO_MATCH

        excluded = pattern[0]

        # Check if excluded pattern matches
        excluded_result = _match_impl(excluded, expr, bindings, evaluator)
        if excluded_result.success:
            return NO_MATCH  # Excluded pattern matched, so fail

        # If there's an alternative pattern, it must match
        if len(pattern) >= 2:
            alternative = pattern[1]
            return _match_impl(alternative, expr, bindings, evaluator)

        # No alternative, just check that excluded didn't match
        return success(bindings)

    # ─────────────────────────────────────────────────────────────────────────
    # Handle atoms - must be equal
    # ─────────────────────────────────────────────────────────────────────────
    if is_atom(pattern):
        return success(bindings) if pattern == expr else NO_MATCH

    # ─────────────────────────────────────────────────────────────────────────
    # Handle symbols - must be equal
    # ─────────────────────────────────────────────────────────────────────────
    if is_symbol(pattern):
        return success(bindings) if pattern == expr else NO_MATCH

    # ─────────────────────────────────────────────────────────────────────────
    # Handle expressions - match head and arguments
    # ─────────────────────────────────────────────────────────────────────────
    if is_expr(pattern) and is_expr(expr):
        # Match heads
        head_result = _match_impl(pattern.head, expr.head, bindings, evaluator)
        if not head_result.success:
            return NO_MATCH

        # Check for Flat/Orderless attributes
        flat = expr.has_attr(Flat) if hasattr(expr, 'has_attr') else False
        orderless = expr.has_attr(Orderless) if hasattr(expr, 'has_attr') else False

        # Match arguments
        for matched_bindings in _match_sequence_impl(
            pattern.args, expr.args, head_result.bindings, evaluator, flat, orderless
        ):
            return success(matched_bindings)

        return NO_MATCH

    # ─────────────────────────────────────────────────────────────────────────
    # Default: no match
    # ─────────────────────────────────────────────────────────────────────────
    return NO_MATCH


def _match_sequence_impl(
    patterns: Tuple["Element", ...],
    exprs: Tuple["Element", ...],
    bindings: Bindings,
    evaluator: Optional[Callable[["Element"], "Element"]],
    flat: bool,
    orderless: bool,
) -> Iterator[Bindings]:
    """
    Internal implementation of sequence matching.

    This is the most complex part of pattern matching, handling:
    - Sequence patterns (__, ___)
    - Flat (associative) matching
    - Orderless (commutative) matching
    """

    # Base case: no patterns left
    if not patterns:
        if not exprs:
            yield bindings
        return

    pattern = patterns[0]
    rest_patterns = patterns[1:]

    # ─────────────────────────────────────────────────────────────────────────
    # Handle sequence patterns (__, ___)
    # ─────────────────────────────────────────────────────────────────────────
    if is_sequence_blank(pattern) or _is_named_sequence_pattern(pattern):
        # Get the actual blank and optional name
        if is_pattern(pattern):
            name = pattern_name(pattern)
            blank_part = pattern_blank(pattern)
        else:
            name = None
            blank_part = pattern

        is_null = is_blank_null_sequence(blank_part)
        min_match = 0 if is_null else 1

        # Try matching different numbers of expressions
        for match_count in range(min_match, len(exprs) - len(rest_patterns) + 1):
            matched_exprs = exprs[:match_count]
            remaining_exprs = exprs[match_count:]

            # Check head constraints for each matched expression
            if blank_part is not None:
                all_match = all(
                    blank_matches_head(blank_part, e) for e in matched_exprs
                )
                if not all_match:
                    continue

            # Try to bind the sequence
            new_bindings = bindings
            if name is not None:
                # Bind as Sequence[...]
                seq_value = Expression(Symbol("Sequence"), *matched_exprs)
                try:
                    new_bindings = bindings.bind(name, seq_value)
                except BindingConflict:
                    continue

            # Continue matching rest of patterns
            yield from _match_sequence_impl(
                rest_patterns, remaining_exprs, new_bindings, evaluator, flat, orderless
            )
        return

    # ─────────────────────────────────────────────────────────────────────────
    # Handle Orderless (commutative) matching
    # ─────────────────────────────────────────────────────────────────────────
    if orderless:
        # Try each expression for the first pattern
        for i, expr in enumerate(exprs):
            result = _match_impl(pattern, expr, bindings, evaluator)
            if result.success:
                remaining = exprs[:i] + exprs[i+1:]
                yield from _match_sequence_impl(
                    rest_patterns, remaining, result.bindings, evaluator, flat, orderless
                )
        return

    # ─────────────────────────────────────────────────────────────────────────
    # Standard sequential matching
    # ─────────────────────────────────────────────────────────────────────────
    if not exprs:
        return  # No expressions left to match

    expr = exprs[0]
    rest_exprs = exprs[1:]

    result = _match_impl(pattern, expr, bindings, evaluator)
    if result.success:
        yield from _match_sequence_impl(
            rest_patterns, rest_exprs, result.bindings, evaluator, flat, orderless
        )


def _is_named_sequence_pattern(pattern: "Element") -> bool:
    """Check if pattern is Pattern[name, BlankSequence|BlankNullSequence]."""
    if not is_pattern(pattern):
        return False
    inner = pattern_blank(pattern)
    return inner is not None and is_sequence_blank(inner)


# ═══════════════════════════════════════════════════════════════════════════════
# SUBSTITUTION
# ═══════════════════════════════════════════════════════════════════════════════

def replace_with_bindings(
    expr: "Element",
    bindings: Bindings,
) -> "Element":
    """
    Substitute bound values into an expression.

    Replaces all occurrences of bound symbols with their values.

    Args:
        expr: The expression to perform substitution on.
        bindings: The bindings to apply.

    Returns:
        New expression with substitutions applied.

    Examples:
        >>> x = Symbol("x")
        >>> bindings = Bindings({x: 42})
        >>> Plus = Symbol("Plus")
        >>> replace_with_bindings(Expression(Plus, x, 1), bindings)
        Plus[42, 1]
    """
    if not bindings:
        return expr

    return _replace_impl(expr, bindings)


def _replace_impl(expr: "Element", bindings: Bindings) -> "Element":
    """Internal implementation of substitution."""

    # Check if this is a bound symbol
    if is_symbol(expr) and expr in bindings:
        return bindings[expr]

    # Atoms stay as-is
    if is_atom(expr) or is_symbol(expr):
        return expr

    # Recursively process expressions
    if is_expr(expr):
        new_head = _replace_impl(expr.head, bindings)
        new_args = tuple(_replace_impl(arg, bindings) for arg in expr.args)

        # Flatten Sequence in arguments
        flattened_args: List["Element"] = []
        for arg in new_args:
            if is_expr(arg) and arg.head == Symbol("Sequence"):
                flattened_args.extend(arg.args)
            else:
                flattened_args.append(arg)

        # Only create new expression if something changed
        if new_head == expr.head and tuple(flattened_args) == expr.args:
            return expr

        return Expression(new_head, *flattened_args, _attrs=expr.attributes)

    return expr


# ═══════════════════════════════════════════════════════════════════════════════
# FINDING MATCHES
# ═══════════════════════════════════════════════════════════════════════════════

def find_matches(
    pattern: "Element",
    expr: "Element",
    evaluator: Optional[Callable[["Element"], "Element"]] = None,
) -> Iterator[Tuple["Element", Bindings]]:
    """
    Find all subexpressions that match a pattern.

    Traverses the expression tree and yields each subexpression
    that matches the pattern along with its bindings.

    Args:
        pattern: The pattern to search for.
        expr: The expression to search in.
        evaluator: Optional evaluator for conditions.

    Yields:
        (matched_subexpression, bindings) tuples.
    """
    # Try matching at current level
    result = match(pattern, expr, evaluator=evaluator)
    if result.success:
        yield (expr, result.bindings)

    # Recurse into subexpressions
    if is_expr(expr):
        for arg in expr.args:
            yield from find_matches(pattern, arg, evaluator)


def find_all_matches(
    pattern: "Element",
    expr: "Element",
    evaluator: Optional[Callable[["Element"], "Element"]] = None,
) -> List[Tuple["Element", Bindings]]:
    """
    Find all subexpressions that match a pattern (list version).

    Like find_matches but returns a list instead of an iterator.

    Args:
        pattern: The pattern to search for.
        expr: The expression to search in.
        evaluator: Optional evaluator for conditions.

    Returns:
        List of (matched_subexpression, bindings) tuples.
    """
    return list(find_matches(pattern, expr, evaluator))


def count_matches(
    pattern: "Element",
    expr: "Element",
    evaluator: Optional[Callable[["Element"], "Element"]] = None,
) -> int:
    """
    Count how many subexpressions match a pattern.

    Args:
        pattern: The pattern to search for.
        expr: The expression to search in.
        evaluator: Optional evaluator for conditions.

    Returns:
        Number of matching subexpressions.
    """
    return sum(1 for _ in find_matches(pattern, expr, evaluator))
