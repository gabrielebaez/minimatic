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
    - PatternTest (pat?test)
    - Optional patterns (x_:default)
    - Repeated patterns (x_..)
    - Except patterns
    - Verbatim (literal matching)
    - HoldPattern
    - Structural matching (head + arguments)
    - Flat (associative) matching
    - Orderless (commutative) matching
    - Sequence patterns (__, ___)

Usage:
    from minimatic.pattern import match, matches, Bindings

    result = match(pattern, expression)
    if result:
        print(result[Symbol("x")])

    if matches(pattern, expression):
        print("Pattern matches!")
"""

# from __future__ import annotations
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from minimatic.core.atoms import Element

from minimatic.core.atoms import is_atom
from minimatic.core.attributes import Flat, Orderless
from minimatic.core.expression import Expression, is_expr
from minimatic.core.symbol import Symbol, is_symbol

from .bindings import BindingConflict, Bindings, empty_bindings
from .blanks import (
    blank_matches_head,
    is_blank,
    is_blank_null_sequence,
    is_sequence_blank,
)
from .structural import (
    get_condition_pattern,
    get_condition_test,
    get_default_value,
    is_alternatives,
    is_condition,
    is_except,
    is_hold_pattern,
    is_optional,
    is_pattern,
    is_pattern_test,
    is_repeated,
    is_repeated_null,
    is_verbatim,
    pattern_blank,
    pattern_name,
    unwrap_hold_pattern,
)

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT_MAX_DEPTH = 128
"""Maximum recursion depth for pattern matching."""


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

    def __getitem__(self, key: Symbol) -> Element:
        """Access bindings directly."""
        return self.bindings[key]

    def get(self, key: Symbol, default: Element = None) -> Element:
        """Get binding with default."""
        return self.bindings.get(key, default)


# Sentinel for failed matches
NO_MATCH = MatchResult(success=False, bindings=empty_bindings())


def success(bindings: Bindings | None = None) -> MatchResult:
    """Create a successful match result."""
    if bindings is None:
        bindings = empty_bindings()
    return MatchResult(success=True, bindings=bindings)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN MATCHING FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════


def match(
    pattern: Element,
    expr: Element,
    bindings: Bindings | None = None,
    evaluator: Callable[[Element], Element] | None = None,
    max_depth: int = DEFAULT_MAX_DEPTH,
    expr_attrs: frozenset | None = None,
) -> MatchResult:
    """
    Match a pattern against an expression.

    Args:
        pattern: The pattern to match.
        expr: The expression to match against.
        bindings: Optional initial bindings (for nested matching).
        evaluator: Optional evaluator for Condition/PatternTest evaluation.
                   If None, Condition/PatternTest fail safely (no match).
        max_depth: Maximum recursion depth.
        expr_attrs: Optional resolved attributes for the expression's head.
                    Used for Flat/Orderless matching when the expression
                    itself doesn't carry attributes (e.g., head attrs from context).

    Returns:
        MatchResult with success=True and bindings if matched,
        or NO_MATCH (success=False) if not matched.
    """
    if bindings is None:
        bindings = empty_bindings()

    return _match_impl(pattern, expr, bindings, evaluator, max_depth, 0, expr_attrs)


def matches(
    pattern: Element,
    expr: Element,
    evaluator: Callable[[Element], Element] | None = None,
) -> bool:
    """
    Check if a pattern matches an expression.
    """
    return match(pattern, expr, evaluator=evaluator).success


def match_sequence(
    patterns: tuple[Element, ...],
    exprs: tuple[Element, ...],
    bindings: Bindings | None = None,
    evaluator: Callable[[Element], Element] | None = None,
    flat: bool = False,
    orderless: bool = False,
) -> Iterator[Bindings]:
    """
    Match a sequence of patterns against a sequence of expressions.

    Yields all possible ways to match.
    """
    if bindings is None:
        bindings = empty_bindings()

    yield from _match_sequence_impl(
        patterns,
        exprs,
        bindings,
        evaluator,
        flat,
        orderless,
        DEFAULT_MAX_DEPTH,
        0,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# INTERNAL MATCHING IMPLEMENTATION
# ═══════════════════════════════════════════════════════════════════════════════


def _match_impl(
    pattern: Element,
    expr: Element,
    bindings: Bindings,
    evaluator: Callable[[Element], Element] | None,
    max_depth: int,
    depth: int,
    expr_attrs: frozenset | None = None,
) -> MatchResult:
    """Internal implementation of pattern matching."""

    if depth > max_depth:
        return NO_MATCH

    # ─────────────────────────────────────────────────────────────────────────
    # Handle HoldPattern - unwrap and continue
    # ─────────────────────────────────────────────────────────────────────────
    if is_hold_pattern(pattern):
        pattern = unwrap_hold_pattern(pattern)

    # ─────────────────────────────────────────────────────────────────────────
    # Handle Verbatim - literal matching
    # ─────────────────────────────────────────────────────────────────────────
    if is_verbatim(pattern):
        if len(pattern.args) >= 1:
            return success(bindings) if pattern.args[0] == expr else NO_MATCH
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
            inner_result = _match_impl(inner, expr, bindings, evaluator, max_depth, depth + 1)
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
    # Fail-safe: if no evaluator, pattern does NOT match
    # ─────────────────────────────────────────────────────────────────────────
    if is_condition(pattern):
        inner_pat = get_condition_pattern(pattern)
        test = get_condition_test(pattern)

        if inner_pat is None:
            return NO_MATCH

        # First match the inner pattern
        inner_result = _match_impl(
            inner_pat, expr, bindings, evaluator, max_depth, depth + 1, expr_attrs
        )
        if not inner_result.success:
            return NO_MATCH

        # Then evaluate the condition
        if test is not None:
            if evaluator is None:
                # Fail-safe: no evaluator means we can't check the condition
                return NO_MATCH
            substituted = replace_with_bindings(test, inner_result.bindings)
            result = evaluator(substituted)
            if result != Symbol("True") and result is not True:
                return NO_MATCH

        return success(inner_result.bindings)

    # ─────────────────────────────────────────────────────────────────────────
    # Handle Alternatives (a | b | c)
    # ─────────────────────────────────────────────────────────────────────────
    if is_alternatives(pattern):
        for alt in pattern.args:
            result = _match_impl(alt, expr, bindings, evaluator, max_depth, depth + 1)
            if result.success:
                return result
        return NO_MATCH

    # ─────────────────────────────────────────────────────────────────────────
    # Handle PatternTest (pat?test)
    # Fail-safe: if no evaluator, pattern does NOT match
    # ─────────────────────────────────────────────────────────────────────────
    if is_pattern_test(pattern):
        if len(pattern.args) < 2:
            return NO_MATCH

        inner_pat = pattern.args[0]
        test_func = pattern.args[1]

        # First match the inner pattern
        inner_result = _match_impl(
            inner_pat, expr, bindings, evaluator, max_depth, depth + 1, expr_attrs
        )
        if not inner_result.success:
            return NO_MATCH

        # Then apply the test function
        if evaluator is None:
            # Fail-safe: no evaluator means we can't run the test
            return NO_MATCH
        test_expr = Expression(test_func, expr)
        result = evaluator(test_expr)
        if result != Symbol("True") and result is not True:
            return NO_MATCH

        return success(inner_result.bindings)

    # ─────────────────────────────────────────────────────────────────────────
    # Handle Except (Except[c] or Except[c, pat])
    # ─────────────────────────────────────────────────────────────────────────
    if is_except(pattern):
        if len(pattern.args) < 1:
            return NO_MATCH

        excluded = pattern.args[0]

        # Check if excluded pattern matches
        excluded_result = _match_impl(
            excluded, expr, bindings, evaluator, max_depth, depth + 1, expr_attrs
        )
        if excluded_result.success:
            return NO_MATCH  # Excluded matched → fail

        # If there's an alternative pattern, it must match
        if len(pattern.args) >= 2:
            alternative = pattern.args[1]
            return _match_impl(
                alternative, expr, bindings, evaluator, max_depth, depth + 1, expr_attrs
            )

        # No alternative, just check that excluded didn't match
        return success(bindings)

    # ─────────────────────────────────────────────────────────────────────────
    # Handle Repeated (pat..) - one or more
    # ─────────────────────────────────────────────────────────────────────────
    if is_repeated(pattern):
        inner_pat = pattern.args[0] if len(pattern.args) >= 1 else None
        if inner_pat is None:
            return NO_MATCH
        return _match_impl(inner_pat, expr, bindings, evaluator, max_depth, depth + 1, expr_attrs)

    # ─────────────────────────────────────────────────────────────────────────
    # Handle RepeatedNull (pat...) - zero or more
    # ─────────────────────────────────────────────────────────────────────────
    if is_repeated_null(pattern):
        inner_pat = pattern.args[0] if len(pattern.args) >= 1 else None
        if inner_pat is None:
            return NO_MATCH
        result = _match_impl(inner_pat, expr, bindings, evaluator, max_depth, depth + 1, expr_attrs)
        if result.success:
            return result
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
        head_result = _match_impl(
            pattern.head, expr.head, bindings, evaluator, max_depth, depth + 1, expr_attrs
        )
        if not head_result.success:
            return NO_MATCH

        # Check for Flat/Orderless attributes
        # Priority: expr_attrs param > expression's own attributes
        if expr_attrs is not None:
            flat = Flat in expr_attrs
            orderless = Orderless in expr_attrs
        elif hasattr(expr, "has_attr"):
            flat = expr.has_attr(Flat)
            orderless = expr.has_attr(Orderless)
        else:
            flat = False
            orderless = False

        # If Flat, flatten nested same-head expressions in both pattern and expr
        p_args = pattern.args
        e_args = expr.args
        if flat:
            p_args = _flatten_args(p_args, pattern.head)
            e_args = _flatten_args(e_args, expr.head)

        # Match arguments
        for matched_bindings in _match_sequence_impl(
            p_args,
            e_args,
            head_result.bindings,
            evaluator,
            flat,
            orderless,
            max_depth,
            depth + 1,
        ):
            return success(matched_bindings)

        return NO_MATCH

    # ─────────────────────────────────────────────────────────────────────────
    # Default: no match
    # ─────────────────────────────────────────────────────────────────────────
    return NO_MATCH


def _flatten_args(args: tuple, head: Element) -> tuple:
    """
    Flatten nested expressions with the same head.

    Used for Flat attribute: Plus[Plus[a, b], c] → (a, b, c)
    """
    result = []
    for arg in args:
        if is_expr(arg) and arg.head == head:
            result.extend(_flatten_args(arg.args, head))
        else:
            result.append(arg)
    return tuple(result)


# ═══════════════════════════════════════════════════════════════════════════════
# SEQUENCE MATCHING
# ═══════════════════════════════════════════════════════════════════════════════


def _match_sequence_impl(
    patterns: tuple[Element, ...],
    exprs: tuple[Element, ...],
    bindings: Bindings,
    evaluator: Callable[[Element], Element] | None,
    flat: bool,
    orderless: bool,
    max_depth: int,
    depth: int,
    expr_attrs: frozenset | None = None,
) -> Iterator[Bindings]:
    """
    Internal implementation of sequence matching.

    Handles:
    - Sequence patterns (__, ___)
    - Repeated/RepeatedNull patterns in sequence position
    - Optional patterns in sequence position
    - Flat (associative) matching
    - Orderless (commutative) matching
    """

    # Base case: no patterns left
    if not patterns:
        if not exprs:
            yield bindings
        return

    pat = patterns[0]
    rest_patterns = patterns[1:]

    # ─────────────────────────────────────────────────────────────────────────
    # Handle Optional in sequence position
    # Try matching the inner pattern; if fails, bind default and continue
    # ─────────────────────────────────────────────────────────────────────────
    if is_optional(pat):
        inner = pat.args[0] if len(pat.args) >= 1 else None
        default = get_default_value(pat)

        if inner is not None:
            # Try matching with the inner pattern
            yield from _match_sequence_impl(
                (inner,) + rest_patterns,
                exprs,
                bindings,
                evaluator,
                flat,
                orderless,
                max_depth,
                depth + 1,
                expr_attrs,
            )

        # Try matching as absent: bind default, continue with rest
        if default is not None and is_pattern(inner):
            name = pattern_name(inner)
            if name is not None:
                try:
                    new_bindings = bindings.bind(name, default)
                    yield from _match_sequence_impl(
                        rest_patterns,
                        exprs,
                        new_bindings,
                        evaluator,
                        flat,
                        orderless,
                        max_depth,
                        depth + 1,
                        expr_attrs,
                    )
                except BindingConflict:
                    pass
        elif default is not None and is_blank(inner):
            # Unnamed optional: just skip
            yield from _match_sequence_impl(
                rest_patterns,
                exprs,
                bindings,
                evaluator,
                flat,
                orderless,
                max_depth,
                depth + 1,
                expr_attrs,
            )
        return

    # ─────────────────────────────────────────────────────────────────────────
    # Handle sequence blanks (__, ___) and named sequence patterns
    # ─────────────────────────────────────────────────────────────────────────
    if is_sequence_blank(pat) or _is_named_sequence_pattern(pat):
        # Get the actual blank and optional name
        if is_pattern(pat):
            name = pattern_name(pat)
            blank_part = pattern_blank(pat)
        else:
            name = None
            blank_part = pat

        is_null = is_blank_null_sequence(blank_part) if blank_part is not None else False
        min_match = 0 if is_null else 1

        # Compute minimum expressions needed by remaining patterns.
        # BlankNullSequence needs 0, everything else needs at least 1.
        min_needed_rest = sum(
            1
            for p in rest_patterns
            if not (is_blank_null_sequence(p) or _is_named_null_sequence_pattern(p))
        )

        # Try matching different numbers of expressions
        for match_count in range(min_match, len(exprs) - min_needed_rest + 1):
            matched_exprs = exprs[:match_count]
            remaining_exprs = exprs[match_count:]

            # Check head constraints for each matched expression
            if blank_part is not None:
                all_match = all(blank_matches_head(blank_part, e) for e in matched_exprs)
                if not all_match:
                    continue

            # Try to bind the sequence
            new_bindings = bindings
            if name is not None:
                # Bind as List[...] (not Sequence[...])
                seq_value = Expression(Symbol("List"), *matched_exprs)
                try:
                    new_bindings = bindings.bind(name, seq_value)
                except BindingConflict:
                    continue

            # Continue matching rest of patterns
            yield from _match_sequence_impl(
                rest_patterns,
                remaining_exprs,
                new_bindings,
                evaluator,
                flat,
                orderless,
                max_depth,
                depth + 1,
                expr_attrs,
            )
        return

    # ─────────────────────────────────────────────────────────────────────────
    # Handle Repeated in sequence position (pat..)
    # ─────────────────────────────────────────────────────────────────────────
    if is_repeated(pat):
        inner = pat.args[0] if len(pat.args) >= 1 else None
        if inner is None:
            return

        min_needed_rest = _min_exprs_for_patterns(rest_patterns)

        # Try matching 1 to N expressions
        for match_count in range(1, len(exprs) - min_needed_rest + 1):
            matched_exprs = exprs[:match_count]
            remaining_exprs = exprs[match_count:]

            # Try to match all matched_exprs against inner pattern.
            # Each element must match; accumulate bindings.
            all_ok = True
            new_bindings = bindings
            for e in matched_exprs:
                result = _match_impl(
                    inner, e, new_bindings, evaluator, max_depth, depth + 1, expr_attrs
                )
                if not result.success:
                    all_ok = False
                    break
                new_bindings = result.bindings

            if all_ok:
                yield from _match_sequence_impl(
                    rest_patterns,
                    remaining_exprs,
                    new_bindings,
                    evaluator,
                    flat,
                    orderless,
                    max_depth,
                    depth + 1,
                    expr_attrs,
                )
        return

    # ─────────────────────────────────────────────────────────────────────────
    # Handle RepeatedNull in sequence position (pat...)
    # Zero or more repetitions
    # ─────────────────────────────────────────────────────────────────────────
    if is_repeated_null(pat):
        inner = pat.args[0] if len(pat.args) >= 1 else None
        if inner is None:
            return

        min_needed_rest = _min_exprs_for_patterns(rest_patterns)

        # Try matching 0 to N expressions
        for match_count in range(0, len(exprs) - min_needed_rest + 1):
            matched_exprs = exprs[:match_count]
            remaining_exprs = exprs[match_count:]

            all_ok = True
            new_bindings = bindings
            for e in matched_exprs:
                result = _match_impl(
                    inner, e, new_bindings, evaluator, max_depth, depth + 1, expr_attrs
                )
                if not result.success:
                    all_ok = False
                    break
                new_bindings = result.bindings

            if all_ok:
                yield from _match_sequence_impl(
                    rest_patterns,
                    remaining_exprs,
                    new_bindings,
                    evaluator,
                    flat,
                    orderless,
                    max_depth,
                    depth + 1,
                    expr_attrs,
                )
        return

    # ─────────────────────────────────────────────────────────────────────────
    # Handle Orderless (commutative) matching
    # Try each remaining expression for the current pattern position
    # ─────────────────────────────────────────────────────────────────────────
    if orderless and len(exprs) > 0:
        for i in range(len(exprs)):
            expr = exprs[i]
            result = _match_impl(pat, expr, bindings, evaluator, max_depth, depth + 1, expr_attrs)
            if result.success:
                remaining = exprs[:i] + exprs[i + 1 :]
                yield from _match_sequence_impl(
                    rest_patterns,
                    remaining,
                    result.bindings,
                    evaluator,
                    flat,
                    False,
                    max_depth,
                    depth + 1,
                    expr_attrs,
                )
        return

    # ─────────────────────────────────────────────────────────────────────────
    # Standard sequential matching
    # ─────────────────────────────────────────────────────────────────────────
    if not exprs:
        return  # No expressions left to match

    expr = exprs[0]
    rest_exprs = exprs[1:]

    result = _match_impl(pat, expr, bindings, evaluator, max_depth, depth + 1, expr_attrs)
    if result.success:
        yield from _match_sequence_impl(
            rest_patterns,
            rest_exprs,
            result.bindings,
            evaluator,
            flat,
            orderless,
            max_depth,
            depth + 1,
            expr_attrs,
        )


def _is_named_sequence_pattern(pattern: Element) -> bool:
    """Check if pattern is Pattern[name, BlankSequence|BlankNullSequence]."""
    if not is_pattern(pattern):
        return False
    inner = pattern_blank(pattern)
    return inner is not None and is_sequence_blank(inner)


def _is_named_null_sequence_pattern(pattern: Element) -> bool:
    """Check if pattern is Pattern[name, BlankNullSequence]."""
    if not is_pattern(pattern):
        return False
    inner = pattern_blank(pattern)
    return inner is not None and is_blank_null_sequence(inner)


def _min_exprs_for_patterns(patterns: tuple) -> int:
    """Compute minimum number of expressions needed to match a pattern tuple."""
    count = 0
    for p in patterns:
        if is_blank_null_sequence(p):
            continue
        if _is_named_null_sequence_pattern(p):
            continue
        if is_repeated_null(p):
            continue
        count += 1
    return count


# ═══════════════════════════════════════════════════════════════════════════════
# SUBSTITUTION
# ═══════════════════════════════════════════════════════════════════════════════


def replace_with_bindings(
    expr: Element,
    bindings: Bindings,
) -> Element:
    """
    Substitute bound values into an expression.

    Replaces all occurrences of bound symbols with their values.
    Bound sequences (List[...]) are flattened into argument lists.
    """
    if not bindings:
        return expr

    return _replace_impl(expr, bindings)


def _replace_impl(expr: Element, bindings: Bindings) -> Element:
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

        # Flatten List-bound sequences in arguments
        flattened_args: list[Element] = []
        for arg in new_args:
            if is_expr(arg) and arg.head == Symbol("List"):
                # Flatten List[...] into argument list
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
    pattern: Element,
    expr: Element,
    evaluator: Callable[[Element], Element] | None = None,
) -> Iterator[tuple[Element, Bindings]]:
    """
    Find all subexpressions that match a pattern.

    Traverses the expression tree and yields each subexpression
    that matches the pattern along with its bindings.
    """
    result = match(pattern, expr, evaluator=evaluator)
    if result.success:
        yield (expr, result.bindings)

    if is_expr(expr):
        for arg in expr.args:
            yield from find_matches(pattern, arg, evaluator)


def find_all_matches(
    pattern: Element,
    expr: Element,
    evaluator: Callable[[Element], Element] | None = None,
) -> list[tuple[Element, Bindings]]:
    """
    Find all subexpressions that match a pattern (list version).
    """
    return list(find_matches(pattern, expr, evaluator))


def count_matches(
    pattern: Element,
    expr: Element,
    evaluator: Callable[[Element], Element] | None = None,
) -> int:
    """
    Count how many subexpressions match a pattern.
    """
    return sum(1 for _ in find_matches(pattern, expr, evaluator))
