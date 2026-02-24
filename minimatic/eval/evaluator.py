"""
Main evaluation loop implementing the Wolfram Language
standard evaluation procedure.
"""

from __future__ import annotations

import sys
from typing import Any, Optional, Callable

from minimatic.core import (
    Symbol, Expression, 
    is_symbol, is_expr, is_atom,
    HoldAll, HoldAllComplete, HoldFirst, HoldRest,
    Flat, Orderless, Listable, SequenceHold
)
from minimatic.core.attributes import has_attribute
from minimatic.pattern import match, replace_with_bindings, NO_MATCH, Bindings

from .context import get_current_context, EvaluationContext
from .values import get_value, OwnValues, DownValues, UpValues, SubValues, NValues
from .rules import Rule, try_rules, apply_rule
from .transforms import (
    flatten_sequences, apply_flat, 
    apply_orderless, apply_listable
)


# System constants
DEFAULT_RECURSION_LIMIT = 256
DEFAULT_ITERATION_LIMIT = 1000


class RecursionLimitError(Exception):
    """Raised when $RecursionLimit is exceeded."""
    pass


class IterationLimitError(Exception):
    """Raised when $IterationLimit is exceeded."""
    pass


# Thread-local evaluation state
class EvalState:
    def __init__(self):
        self.recursion_depth = 0
        self.iteration_count = 0
        self.recursion_limit = DEFAULT_RECURSION_LIMIT
        self.iteration_limit = DEFAULT_ITERATION_LIMIT
        self.trace_enabled = False


_eval_state = EvalState()


def evaluate(expr: Any, context: Optional[EvaluationContext] = None) -> Any:
    """
    Main evaluation loop following the Wolfram Language standard evaluation procedure.

    Algorithm (from evaluation.txt):
    0. Check limits (recursion depth)
    1. Dispatch by expression type (Atom, Symbol, Expression)
    2. Evaluate head (unless HoldAllComplete)
    3. Resolve attributes
    4. Evaluate arguments (respecting Hold attributes)
    5. Flatten Sequences
    6. Apply structural attributes (Flat, Orderless)
    7. Apply Listable attribute
    8. Try rules (UpValues, DownValues, SubValues, NValues, Built-in)
    9. If changed, re-evaluate (check iteration limit)
    10. Return stable expression
    """
    if context is None:
        context = get_current_context()

    # Step 0: Check recursion limit
    _eval_state.recursion_depth += 1
    if _eval_state.recursion_depth > _eval_state.recursion_limit:
        _eval_state.recursion_depth -= 1
        raise RecursionLimitError(f"Recursion depth of {_eval_state.recursion_limit} exceeded")

    try:
        # Step 1: Dispatch by expression type
        if is_atom(expr):
            # Atoms evaluate to themselves
            return expr

        if is_symbol(expr):
            # Apply OwnValues to symbols
            return _evaluate_symbol(expr, context)

        # Expression evaluation
        if not is_expr(expr):
            # Unknown type, return as-is
            return expr

        return _evaluate_expression(expr, context)

    finally:
        _eval_state.recursion_depth -= 1


def _evaluate_symbol(sym: Symbol, context: EvaluationContext) -> Any:
    """Evaluate a symbol by applying its OwnValues."""
    own_values = context.get_own_values(sym)

    if not own_values:
        return sym  # No definitions

    # Try each OwnValue rule
    for pattern_expr, replacement, condition in own_values:
        result, success = _try_definition(pattern_expr, replacement, condition, sym, context)
        if success:
            return evaluate(result, context)  # Re-evaluate result

    return sym


def _evaluate_expression(expr: Expression, context: EvaluationContext) -> Any:
    """Evaluate a compound expression."""
    original_expr = expr

    # Step 2: Evaluate head (unless HoldAllComplete)
    head = expr.head

    # Check for HoldAllComplete on the head symbol
    if is_symbol(head) and has_attribute(context, head, HoldAllComplete):
        # Don't evaluate head or anything else
        pass
    else:
        # Evaluate head
        if is_symbol(head):
            # Check OwnValues for head
            head = _evaluate_symbol_head(head, context)
        elif is_expr(head):
            head = evaluate(head, context)

        # If head changed, create new expression
        if head != expr.head:
            expr = Expression(head, *expr.args, attributes=expr.attributes)

    # Step 3: Resolve attributes
    # Merge: head_attrs ∪ expr_attrs (expr_attrs take precedence)
    head_attrs = frozenset()
    if is_symbol(expr.head):
        head_attrs = context.get_attributes(expr.head)

    # Combine attributes (expression attributes override head attributes)
    # But expression attributes are additional constraints, so we union them
    effective_attrs = head_attrs | expr.attributes

    # Check for HoldAllComplete on effective attributes
    has_hold_all_complete = HoldAllComplete in effective_attrs

    # Step 4: Evaluate arguments (respecting Hold attributes)
    has_hold_all = HoldAll in effective_attrs
    has_hold_first = HoldFirst in effective_attrs
    has_hold_rest = HoldRest in effective_attrs

    if has_hold_all_complete or has_hold_all:
        # Hold all arguments
        evaluated_args = list(expr.args)
    elif has_hold_first:
        # Hold first, evaluate rest
        evaluated_args = [expr.args[0]] if expr.args else []
        evaluated_args.extend(evaluate(arg, context) for arg in expr.args[1:])
    elif has_hold_rest:
        # Evaluate first, hold rest
        if expr.args:
            evaluated_args = [evaluate(expr.args[0], context)]
            evaluated_args.extend(expr.args[1:])
        else:
            evaluated_args = []
    else:
        # Evaluate all arguments
        evaluated_args = [evaluate(arg, context) for arg in expr.args]

    # Check if any argument changed
    args_changed = tuple(evaluated_args) != expr.args

    if args_changed:
        expr = Expression(expr.head, *evaluated_args, attributes=expr.attributes)

    # Step 5: Flatten Sequences (unless SequenceHold or HoldAllComplete)
    has_sequence_hold = SequenceHold in effective_attrs

    if not has_hold_all_complete and not has_sequence_hold:
        expr = flatten_sequences(expr, hold_sequence=False)

    # Step 6: Apply structural attributes
    has_flat = Flat in effective_attrs
    has_orderless = Orderless in effective_attrs

    if has_flat:
        expr = apply_flat(expr, is_flat=True)

    if has_orderless:
        expr = apply_orderless(expr, is_orderless=True)

    # Step 7: Apply Listable attribute
    has_listable = Listable in effective_attrs

    if has_listable:
        threaded = apply_listable(expr, is_listable=True)
        if threaded != expr:
            # If threading occurred, evaluate the result and return
            return evaluate(threaded, context)

    # Step 8: Try rules in priority order
    new_expr = _apply_rules(expr, context)

    # Step 9: Check if changed and re-evaluate
    if new_expr != expr:
        _eval_state.iteration_count += 1
        if _eval_state.iteration_count > _eval_state.iteration_limit:
            raise IterationLimitError(f"Iteration limit of {_eval_state.iteration_limit} exceeded")

        # Re-evaluate from top (Step 0)
        return evaluate(new_expr, context)

    # Step 10: Return stable expression
    return expr


def _evaluate_symbol_head(head: Symbol, context: EvaluationContext) -> Any:
    """Evaluate a symbol that appears as a head."""
    own_values = context.get_own_values(head)

    if not own_values:
        return head

    for pattern_expr, replacement, condition in own_values:
        result, success = _try_definition(pattern_expr, replacement, condition, head, context)
        if success:
            return evaluate(result, context)

    return head


def _apply_rules(expr: Expression, context: EvaluationContext) -> Any:
    """
    Apply rules in priority order:
    a. UpValues - check arguments left-to-right; first wins
    b. DownValues - check head's rewrite rules
    c. SubValues - if head is Expression[sym, ...], check sym
    d. NValues - for numeric approximation (N[...])
    e. Built-in - native implementation of head
    """

    # a. UpValues: check arguments left-to-right
    for arg in expr.args:
        if is_symbol(arg):
            up_values = context.get_up_values(arg)
            if up_values:
                result = _try_value_rules(up_values, expr, context)
                if result != expr:
                    return result
        elif is_expr(arg) and is_symbol(arg.head):
            up_values = context.get_up_values(arg.head)
            if up_values:
                result = _try_value_rules(up_values, expr, context)
                if result != expr:
                    return result

    # b. DownValues: check head's definitions
    if is_symbol(expr.head):
        down_values = context.get_down_values(expr.head)
        if down_values:
            result = _try_value_rules(down_values, expr, context)
            if result != expr:
                return result

    # c. SubValues: for f[a][b] patterns
    if is_expr(expr.head):
        sub_sym = expr.head.head if is_symbol(expr.head.head) else None
        if sub_sym is not None:
            sub_values = context.get_sub_values(sub_sym)
            if sub_values:
                result = _try_value_rules(sub_values, expr, context)
                if result != expr:
                    return result

    # d. NValues: for N[expr] numeric approximation
    # Check if this is inside N[]
    # For now, handled via DownValues on N

    # e. Built-in: native implementation
    # This would dispatch to registered built-in functions
    result = _try_builtin(expr, context)

    return result


def _try_value_rules(rules_list: list, expr: Expression, context: EvaluationContext) -> Any:
    """Try a list of value entries (pattern, replacement, condition) against expr."""
    for pattern_expr, replacement, condition in rules_list:
        result, success = _try_definition(pattern_expr, replacement, condition, expr, context)
        if success:
            return result
    return expr


def _try_definition(pattern_expr: Any, replacement: Any, condition: Optional[Any], 
                    expr: Any, context: EvaluationContext) -> tuple[Any, bool]:
    """Try a single definition against an expression."""
    # Match pattern
    match_result = match(pattern_expr, expr)

    if not match_result:
        return expr, False

    # Check condition if present
    if condition is not None:
        cond_substituted = replace_with_bindings(condition, match_result.bindings)
        cond_result = evaluate(cond_substituted, context)

        # Must be True to proceed
        if cond_result is not True and cond_result != Symbol("True"):
            return expr, False

    # Apply replacement
    result = replace_with_bindings(replacement, match_result.bindings)

    return result, True


def _try_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """Try to apply built-in function implementation."""
    # This would integrate with the builtins module
    # For now, return unchanged
    return expr


def try_evaluate(expr: Any, context: Optional[EvaluationContext] = None, 
                 default: Any = None) -> Any:
    """
    Evaluate expression, returning default if evaluation fails.
    """
    try:
        return evaluate(expr, context)
    except (RecursionLimitError, IterationLimitError, Exception):
        return default


def FixedPoint(func: Callable[[Any], Any], expr: Any, 
               max_iterations: int = 100, same_test: Optional[Callable] = None) -> Any:
    """
    Apply func repeatedly until the result no longer changes.

    Args:
        func: Function to apply
        expr: Starting expression
        max_iterations: Maximum number of iterations
        same_test: Optional equality test function

    Returns:
        Fixed point of func starting from expr
    """
    if same_test is None:
        same_test = lambda a, b: a == b

    for _ in range(max_iterations):
        new_expr = func(expr)
        if same_test(new_expr, expr):
            return expr
        expr = new_expr

    return expr


def evaluate_iterated(expr: Any, n: int, context: Optional[EvaluationContext] = None) -> Any:
    """
    Evaluate expression n times.
    """
    for _ in range(n):
        expr = evaluate(expr, context)
    return expr


def set_recursion_limit(limit: int) -> int:
    """Set $RecursionLimit and return old value."""
    old = _eval_state.recursion_limit
    _eval_state.recursion_limit = limit
    return old


def set_iteration_limit(limit: int) -> int:
    """Set $IterationLimit and return old value."""
    old = _eval_state.iteration_limit
    _eval_state.iteration_limit = limit
    return old


def get_recursion_limit() -> int:
    """Get current $RecursionLimit."""
    return _eval_state.recursion_limit


def get_iteration_limit() -> int:
    """Get current $IterationLimit."""
    return _eval_state.iteration_limit
