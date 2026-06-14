"""
Main evaluation loop implementing the Wolfram Language
standard evaluation procedure.
"""

from collections.abc import Callable
from typing import Any

from src.core import (
    Expression,
    Flat,
    HoldAll,
    HoldAllComplete,
    HoldFirst,
    HoldRest,
    Listable,
    Orderless,
    SequenceHold,
    Symbol,
    is_atom,
    is_expr,
    is_symbol,
)
from src.pattern import match, replace_with_bindings

from .context import EvaluationContext, get_current_context
from .transforms import apply_flat, apply_listable, apply_orderless, flatten_sequences

# Lazy import to avoid circular dependency
_builtin_dispatch = None


def _get_builtin_dispatch():
    """Lazy import of built-in dispatch function."""
    global _builtin_dispatch
    if _builtin_dispatch is None:
        from src.builtins.registry import dispatch_builtin

        _builtin_dispatch = dispatch_builtin
    return _builtin_dispatch


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


def evaluate(expr: Any, context: EvaluationContext | None = None) -> Any:
    """
    Main evaluation loop following the Wolfram Language standard evaluation procedure.

    Algorithm:
    1. Dispatch by expression type (Atom, Symbol, Expression)
    2. For Atoms: return self
    3. For Symbols: apply OwnValues
    4. For Expressions:
       a. Evaluate head (unless HoldAllComplete)
       b. Resolve effective attributes
       c. Evaluate arguments (respecting Hold attributes)
       d. Flatten Sequences
       e. Apply Flat (associativity)
       f. Apply Orderless (commutativity)
       g. Apply Listable (threading)
       h. Try rules (UpValues, DownValues, SubValues, NValues, Built-in)
       i. If changed, re-evaluate (check iteration limit)
       j. Return stable expression
    """
    if context is None:
        context = get_current_context()

    # Step 1: Check recursion limit
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

    # Step 3a: Evaluate head (unless HoldAllComplete)
    head = expr.head
    effective_attrs = _resolve_attributes(expr, context)

    # Check for HoldAllComplete on effective attributes
    has_hold_all_complete = HoldAllComplete in effective_attrs

    if not has_hold_all_complete:
        # Evaluate head
        if is_symbol(head):
            # Check OwnValues for head
            head = _evaluate_symbol_head(head, context)
        elif is_expr(head):
            head = evaluate(head, context)

        # If head changed, create new expression
        if head != expr.head:
            expr = Expression(head, *expr.args, _attrs=expr.attributes)

    # Step 3b: Resolve attributes (already done above)
    # effective_attrs computed from head + expression attributes

    # Step 3c: Evaluate arguments (respecting Hold attributes)
    evaluated_args = _evaluate_arguments(expr, context, effective_attrs)

    # Check if any argument changed
    args_changed = tuple(evaluated_args) != expr.args

    if args_changed:
        expr = Expression(expr.head, *evaluated_args, _attrs=expr.attributes)

    # Step 3d: Flatten Sequences (unless SequenceHold or HoldAllComplete)
    has_sequence_hold = SequenceHold in effective_attrs

    if not has_hold_all_complete and not has_sequence_hold:
        expr = flatten_sequences(expr, hold_sequence=False)

    # Step 3e: Apply structural attributes
    has_flat = Flat in effective_attrs
    has_orderless = Orderless in effective_attrs

    if has_flat:
        expr = apply_flat(expr, is_flat=True)

    if has_orderless:
        expr = apply_orderless(expr, is_orderless=True)

    # Step 3f: Apply Listable attribute
    has_listable = Listable in effective_attrs

    if has_listable:
        threaded = apply_listable(expr, is_listable=True)
        if threaded != expr:
            # If threading occurred, evaluate the result and return
            return evaluate(threaded, context)

    # Step 3h: Try rules in priority order
    new_expr = _apply_rules(expr, context)

    # Step 3i: Check if changed and re-evaluate
    if new_expr != expr:
        _eval_state.iteration_count += 1
        if _eval_state.iteration_count > _eval_state.iteration_limit:
            raise IterationLimitError(f"Iteration limit of {_eval_state.iteration_limit} exceeded")

        # Re-evaluate from top (Step 1)
        return evaluate(new_expr, context)

    # Step 3j: Return stable expression
    return expr


def _resolve_attributes(expr: Expression, context: EvaluationContext) -> frozenset[Symbol]:
    """
    Step 3b: Resolve effective attributes.

    Attributes come from three sources (merged):
    - Head symbol's attributes from the context (user-defined)
    - Built-in function's registered attributes
    - Expression's own attributes (take precedence)
    """
    head_attrs = frozenset()
    if is_symbol(expr.head):
        head_attrs = context.get_attributes(expr.head)

    # Also check built-in registered attributes
    from src.builtins.registry import builtin_attributes

    builtin_attrs = builtin_attributes(expr.head) if is_symbol(expr.head) else frozenset()

    # Combine: head_ctx_attrs ∪ builtin_attrs ∪ expr_attrs
    # expr_attrs take precedence
    return head_attrs | builtin_attrs | expr.attributes


def _evaluate_arguments(
    expr: Expression,
    context: EvaluationContext,
    effective_attrs: frozenset[Symbol],
) -> list[Any]:
    """
    Step 3c: Evaluate arguments respecting Hold attributes.

    Hold attributes control which arguments are evaluated:
    - HoldAllComplete or HoldAll: none evaluated
    - HoldFirst: first held, rest evaluated
    - HoldRest: first evaluated, rest held
    - Default (no Hold): all evaluated
    """
    has_hold_all_complete = HoldAllComplete in effective_attrs
    has_hold_all = HoldAll in effective_attrs
    has_hold_first = HoldFirst in effective_attrs
    has_hold_rest = HoldRest in effective_attrs

    if has_hold_all_complete or has_hold_all:
        # Hold all arguments
        return list(expr.args)
    elif has_hold_first:
        # Hold first, evaluate rest
        evaluated_args = [expr.args[0]] if expr.args else []
        evaluated_args.extend(evaluate(arg, context) for arg in expr.args[1:])
        return evaluated_args
    elif has_hold_rest:
        # Evaluate first, hold rest
        if expr.args:
            evaluated_args = [evaluate(expr.args[0], context)]
            evaluated_args.extend(expr.args[1:])
            return evaluated_args
        return []
    else:
        # Evaluate all arguments
        return [evaluate(arg, context) for arg in expr.args]


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
    Step 3h: Apply rules in priority order:
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
    result = _try_builtin(expr, context)

    return result


def _try_value_rules(rules_list: list, expr: Expression, context: EvaluationContext) -> Any:
    """Try a list of value entries (pattern, replacement, condition) against expr."""
    for pattern_expr, replacement, condition in rules_list:
        result, success = _try_definition(pattern_expr, replacement, condition, expr, context)
        if success:
            return result
    return expr


def _try_definition(
    pattern_expr: Any,
    replacement: Any,
    condition: Any | None,
    expr: Any,
    context: EvaluationContext,
) -> tuple[Any, bool]:
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
    dispatch = _get_builtin_dispatch()
    return dispatch(expr, context)


def try_evaluate(
    expr: Any,
    context: EvaluationContext | None = None,
    default: Any = None,
) -> Any:
    """
    Evaluate expression, returning default if evaluation fails.
    """
    try:
        return evaluate(expr, context)
    except RecursionLimitError, IterationLimitError, Exception:
        return default


def FixedPoint(
    func: Callable[[Any], Any],
    expr: Any,
    max_iterations: int = 100,
    same_test: Callable | None = None,
) -> Any:
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

        def same_test(a: Any, b: Any) -> bool:
            return a == b

    for _ in range(max_iterations):
        new_expr = func(expr)
        if same_test(new_expr, expr):
            return expr
        expr = new_expr

    return expr


def evaluate_iterated(expr: Any, n: int, context: EvaluationContext | None = None) -> Any:
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
