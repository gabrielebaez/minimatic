"""
Comparison and logic built-in functions.

Implements ordering, equality, logical connectives, and parity predicates
following Wolfram Language semantics.
"""

from typing import Any

from minimatic.core import (
    Expression,
    HoldAll,
    Symbol,
    is_integer,
    is_numeric,
)
from minimatic.eval.context import EvaluationContext

from .registry import register_builtin

# ═══════════════════════════════════════════════════════════════════════════════
# COMPARISON
# ═══════════════════════════════════════════════════════════════════════════════

Less = Symbol("Less")


@register_builtin(Less, auto_evaluate=True)
def less_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """Less[a, b]. Returns True if a < b."""
    from minimatic.eval import evaluate

    args = expr.args
    if len(args) < 2:
        return expr
    a = evaluate(args[0], context)
    b = evaluate(args[1], context)
    if is_numeric(a) and is_numeric(b) and not isinstance(a, bool) and not isinstance(b, bool):
        return a < b
    return expr


Greater = Symbol("Greater")


@register_builtin(Greater, auto_evaluate=True)
def greater_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """Greater[a, b]. Returns True if a > b."""
    from minimatic.eval import evaluate

    args = expr.args
    if len(args) < 2:
        return expr
    a = evaluate(args[0], context)
    b = evaluate(args[1], context)
    if is_numeric(a) and is_numeric(b) and not isinstance(a, bool) and not isinstance(b, bool):
        return a > b
    return expr


LessEqual = Symbol("LessEqual")


@register_builtin(LessEqual, auto_evaluate=True)
def lessequal_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """LessEqual[a, b]. Returns True if a <= b."""
    from minimatic.eval import evaluate

    args = expr.args
    if len(args) < 2:
        return expr
    a = evaluate(args[0], context)
    b = evaluate(args[1], context)
    if is_numeric(a) and is_numeric(b) and not isinstance(a, bool) and not isinstance(b, bool):
        return a <= b
    return expr


GreaterEqual = Symbol("GreaterEqual")


@register_builtin(GreaterEqual, auto_evaluate=True)
def greaterequal_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """GreaterEqual[a, b]. Returns True if a >= b."""
    from minimatic.eval import evaluate

    args = expr.args
    if len(args) < 2:
        return expr
    a = evaluate(args[0], context)
    b = evaluate(args[1], context)
    if is_numeric(a) and is_numeric(b) and not isinstance(a, bool) and not isinstance(b, bool):
        return a >= b
    return expr


Equal = Symbol("Equal")


@register_builtin(Equal, auto_evaluate=True)
def equal_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """Equal[a, b]. Mathematical equality. Equal[1, 1.0] → True."""
    from minimatic.eval import evaluate

    args = expr.args
    if len(args) < 2:
        return expr
    a = evaluate(args[0], context)
    b = evaluate(args[1], context)
    if is_numeric(a) and is_numeric(b) and not isinstance(a, bool) and not isinstance(b, bool):
        return a == b
    return expr


Unequal = Symbol("Unequal")


@register_builtin(Unequal, auto_evaluate=True)
def unequal_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """Unequal[a, b]. Returns True if a ≠ b."""
    from minimatic.eval import evaluate

    args = expr.args
    if len(args) < 2:
        return expr
    a = evaluate(args[0], context)
    b = evaluate(args[1], context)
    if is_numeric(a) and is_numeric(b) and not isinstance(a, bool) and not isinstance(b, bool):
        return a != b
    return expr


# ═══════════════════════════════════════════════════════════════════════════════
# LOGIC
# ═══════════════════════════════════════════════════════════════════════════════

And = Symbol("And")


@register_builtin(And, attributes={HoldAll}, auto_evaluate=False)
def and_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """And[a, b, ...]. Short-circuit AND. Returns False on first False."""
    from minimatic.eval import evaluate

    args = expr.args
    if len(args) == 0:
        return True

    for arg in args:
        val = evaluate(arg, context)
        if val is False or val is Symbol("False"):
            return False
        if val is not True and val is not Symbol("True"):
            return expr
    return True


Or = Symbol("Or")


@register_builtin(Or, attributes={HoldAll}, auto_evaluate=False)
def or_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """Or[a, b, ...]. Short-circuit OR. Returns True on first True."""
    from minimatic.eval import evaluate

    args = expr.args
    if len(args) == 0:
        return False

    for arg in args:
        val = evaluate(arg, context)
        if val is True or val is Symbol("True"):
            return True
        if val is not False and val is not Symbol("False"):
            return expr
    return False


Not = Symbol("Not")


@register_builtin(Not, auto_evaluate=True)
def not_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """Not[expr]. Logical negation."""
    from minimatic.eval import evaluate

    args = expr.args
    if len(args) < 1:
        return expr
    val = evaluate(args[0], context)
    if val is True or val is Symbol("True"):
        return False
    if val is False or val is Symbol("False"):
        return True
    return expr


# ═══════════════════════════════════════════════════════════════════════════════
# PARITY PREDICATES
# ═══════════════════════════════════════════════════════════════════════════════

EvenQ = Symbol("EvenQ")


@register_builtin(EvenQ, auto_evaluate=True)
def evenq_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """EvenQ[n]. Returns True if n is an even integer."""
    from minimatic.eval import evaluate

    args = expr.args
    if len(args) < 1:
        return False
    result = evaluate(args[0], context)
    if is_integer(result):
        return result % 2 == 0
    return False


OddQ = Symbol("OddQ")


@register_builtin(OddQ, auto_evaluate=True)
def oddq_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """OddQ[n]. Returns True if n is an odd integer."""
    from minimatic.eval import evaluate

    args = expr.args
    if len(args) < 1:
        return False
    result = evaluate(args[0], context)
    if is_integer(result):
        return result % 2 != 0
    return False
