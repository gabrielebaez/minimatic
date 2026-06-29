"""
Control flow built-in functions.

Implements conditional, looping, scoping, and evaluation control
following Wolfram Language semantics. All constructs use Hold attributes
to receive unevaluated expressions and selectively evaluate them.
"""

from typing import Any

from minimatic.core import (
    Expression,
    HoldAll,
    HoldFirst,
    Symbol,
    gensym,
    is_expr,
    is_integer,
    is_numeric,
    is_real,
    is_string,
    is_symbol,
)
from minimatic.eval.context import EvaluationContext, with_context
from minimatic.pattern import replace_with_bindings

from .registry import register_builtin

# ═══════════════════════════════════════════════════════════════════════════════
# ASSIGNMENT
# ═══════════════════════════════════════════════════════════════════════════════

Set = Symbol("Set")


@register_builtin(Set, attributes={HoldFirst}, auto_evaluate=False)
def set_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """
    Set[sym, value] (x = value). Assign value to sym, returning the value.
    """
    from minimatic.eval import evaluate

    args = expr.args
    if len(args) < 2:
        return expr

    sym = args[0]
    value = evaluate(args[1], context)

    # Set OwnValue on the symbol
    if is_symbol(sym):
        context.set_own_values(sym, [(sym, value, None)])
        return value

    return expr


SetDelayed = Symbol("SetDelayed")


@register_builtin(SetDelayed, attributes={HoldAll}, auto_evaluate=False)
def set_delayed_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """
    SetDelayed[sym, body] (x := body). Assign unevaluated body as DownValue.
    """
    args = expr.args
    if len(args) < 2:
        return expr

    sym = args[0]
    body = args[1]

    if is_symbol(sym):
        # Store as a DownValue with pattern sym (matches any call)
        existing = context.get_down_values(sym)
        existing.append((sym, body, None))
        context.set_down_values(sym, existing)
        return Symbol("Null")

    return expr


# ═══════════════════════════════════════════════════════════════════════════════
# CONDITIONALS
# ═══════════════════════════════════════════════════════════════════════════════

If = Symbol("If")


@register_builtin(If, attributes={HoldAll}, auto_evaluate=False)
def if_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """
    Conditional: If[condition, then] or If[condition, then, else].
    Returns Null if condition is not True and no else branch.
    """
    from minimatic.eval import evaluate

    args = expr.args
    if len(args) < 2:
        return expr

    condition = evaluate(args[0], context)

    if condition is True or condition is Symbol("True"):
        return evaluate(args[1], context)
    elif len(args) >= 3:
        return evaluate(args[2], context)
    else:
        return Symbol("Null")


Which = Symbol("Which")


@register_builtin(Which, attributes={HoldAll}, auto_evaluate=False)
def which_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """
    Which[test1, val1, test2, val2, ...].
    Evaluates tests in order, returns the value for the first True test.
    """
    from minimatic.eval import evaluate

    args = expr.args
    if len(args) < 2:
        return expr

    for i in range(0, len(args) - 1, 2):
        condition = evaluate(args[i], context)
        if condition is True or condition is Symbol("True"):
            return evaluate(args[i + 1], context)

    return Symbol("Null")


Switch = Symbol("Switch")


@register_builtin(Switch, attributes={HoldFirst}, auto_evaluate=False)
def switch_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """
    Switch[expr, pat1, val1, pat2, val2, ..., default].
    Evaluates expr, then matches against patterns.
    """
    from minimatic.eval import evaluate
    from minimatic.pattern import match

    args = expr.args
    if len(args) < 2:
        return expr

    evaluated = evaluate(args[0], context)

    for i in range(1, len(args) - 1, 2):
        pattern = args[i]
        result = match(pattern, evaluated)
        if result.success:
            return evaluate(args[i + 1], context)

    # If odd number of args after expr, last one is default
    if len(args) % 2 == 0:
        return evaluate(args[-1], context)

    return Symbol("Null")


# ═══════════════════════════════════════════════════════════════════════════════
# EVALUATION CONTROL
# ═══════════════════════════════════════════════════════════════════════════════

CompoundExpression = Symbol("CompoundExpression")


@register_builtin(CompoundExpression, attributes={HoldAll}, auto_evaluate=False)
def compound_expression_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """
    CompoundExpression[a, b, ..., c]. Evaluate all, return last.
    """
    from minimatic.eval import evaluate

    if not expr.args:
        return Symbol("Null")

    result = Symbol("Null")
    for arg in expr.args:
        result = evaluate(arg, context)
    return result


Evaluate = Symbol("Evaluate")


@register_builtin(Evaluate, attributes={HoldAll}, auto_evaluate=False)
def evaluate_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """
    Evaluate[expr]. Force evaluation of a held expression.
    """
    from minimatic.eval import evaluate

    if not expr.args:
        return expr
    return evaluate(expr.args[0], context)


ReleaseHold = Symbol("ReleaseHold")


@register_builtin(ReleaseHold, attributes={HoldAll}, auto_evaluate=False)
def release_hold_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """
    ReleaseHold[expr]. Unwrap a held expression and evaluate it.
    If expr is Hold[inner], evaluates inner directly.
    """
    from minimatic.eval import evaluate

    if not expr.args:
        return expr
    inner = expr.args[0]
    # If it's Hold[...], unwrap and evaluate the inner expression
    if is_expr(inner) and is_symbol(inner.head) and inner.head.name == "Hold" and inner.args:
        return evaluate(inner.args[0], context)
    return evaluate(inner, context)


Hold = Symbol("Hold")


@register_builtin(Hold, attributes={HoldAll}, auto_evaluate=False)
def hold_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """
    Hold[expr]. Prevent evaluation (identity for held expressions).
    """
    return expr


HoldForm = Symbol("HoldForm")


@register_builtin(HoldForm, attributes={HoldAll}, auto_evaluate=False)
def hold_form_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """
    HoldForm[expr]. Prevent evaluation (display-oriented).
    """
    return expr


# ═══════════════════════════════════════════════════════════════════════════════
# LOOPING
# ═══════════════════════════════════════════════════════════════════════════════

Do = Symbol("Do")


@register_builtin(Do, attributes={HoldAll}, auto_evaluate=False)
def do_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """
    Do[body, {i, imin, imax}] or Do[body, {i, imin, imax, step}] or Do[body, {i, list}].
    Iterate for side effects, return Null.
    """
    from minimatic.eval import evaluate

    args = expr.args
    if len(args) < 2:
        return expr

    body = args[0]
    iter_spec = args[1]

    if not is_expr(iter_spec) or len(iter_spec.args) < 2:
        return expr

    var = iter_spec.args[0]
    iter_args = iter_spec.args[1:]

    if len(iter_args) == 1:
        # {i, list} form - iterate over list
        lst = evaluate(iter_args[0], context)
        if is_expr(lst) and is_symbol(lst.head) and lst.head.name == "List":
            for item in lst.args:
                substituted = replace_with_bindings(body, {var: item})
                evaluate(substituted, context)
        return Symbol("Null")

    elif len(iter_args) >= 2:
        # {i, imin, imax} or {i, imin, imax, step}
        imin = evaluate(iter_args[0], context)
        imax = evaluate(iter_args[1], context)
        step = evaluate(iter_args[2], context) if len(iter_args) > 2 else 1

        if is_integer(imin) and is_integer(imax) and is_integer(step) and step != 0:
            i = imin
            while (step > 0 and i <= imax) or (step < 0 and i >= imax):
                substituted = replace_with_bindings(body, {var: i})
                evaluate(substituted, context)
                i += step
        return Symbol("Null")

    return expr


While = Symbol("While")


@register_builtin(While, attributes={HoldAll}, auto_evaluate=False)
def while_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """
    While[test, body]. Loop while test is True, return Null.
    """
    from minimatic.eval import evaluate

    args = expr.args
    if len(args) < 2:
        return expr

    while True:
        condition = evaluate(args[0], context)
        if condition is not True and condition is not Symbol("True"):
            break
        evaluate(args[1], context)
    return Symbol("Null")


For = Symbol("For")


@register_builtin(For, attributes={HoldAll}, auto_evaluate=False)
def for_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """
    For[start, test, incr, body]. C-style for loop, return Null.
    """
    from minimatic.eval import evaluate

    args = expr.args
    if len(args) < 4:
        return expr

    start, test, incr, body = args[0], args[1], args[2], args[3]

    # Evaluate start
    evaluate(start, context)

    while True:
        # Check test
        condition = evaluate(test, context)
        if condition is not True and condition is not Symbol("True"):
            break

        # Execute body
        evaluate(body, context)

        # Execute increment
        evaluate(incr, context)

    return Symbol("Null")


Table = Symbol("Table")


@register_builtin(Table, attributes={HoldAll}, auto_evaluate=False)
def table_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """
    Table[expr, {i, imin, imax}] or Table[expr, {i, list}].
    Collect results into a List.
    """
    from minimatic.eval import evaluate

    args = expr.args
    if len(args) < 2:
        return expr

    body = args[0]
    iter_spec = args[1]

    if not is_expr(iter_spec) or len(iter_spec.args) < 2:
        return expr

    var = iter_spec.args[0]
    iter_args = iter_spec.args[1:]
    results = []

    if len(iter_args) == 1:
        # {i, list} form
        lst = evaluate(iter_args[0], context)
        if is_expr(lst) and is_symbol(lst.head) and lst.head.name == "List":
            for item in lst.args:
                substituted = replace_with_bindings(body, {var: item})
                results.append(evaluate(substituted, context))

    elif len(iter_args) >= 2:
        # {i, imin, imax} or {i, imin, imax, step}
        imin = evaluate(iter_args[0], context)
        imax = evaluate(iter_args[1], context)
        step = evaluate(iter_args[2], context) if len(iter_args) > 2 else 1

        if is_integer(imin) and is_integer(imax) and is_integer(step) and step != 0:
            i = imin
            while (step > 0 and i <= imax) or (step < 0 and i >= imax):
                substituted = replace_with_bindings(body, {var: i})
                results.append(evaluate(substituted, context))
                i += step

    return Expression(Symbol("List"), *results)


Nest = Symbol("Nest")


@register_builtin(Nest, attributes={HoldAll}, auto_evaluate=False)
def nest_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """
    Nest[f, expr, n]. Apply f to expr n times.
    """
    from minimatic.eval import evaluate

    args = expr.args
    if len(args) < 3:
        return expr

    f, x, n = args[0], args[1], args[2]
    n_val = evaluate(n, context)

    if not is_integer(n_val) or n_val < 0:
        return expr

    result = evaluate(x, context)
    for _ in range(n_val):
        result = evaluate(Expression(f, result), context)
    return result


NestList = Symbol("NestList")


@register_builtin(NestList, attributes={HoldAll}, auto_evaluate=False)
def nest_list_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """
    NestList[f, expr, n]. Apply f to expr n times, collecting intermediate results.
    """
    from minimatic.eval import evaluate

    args = expr.args
    if len(args) < 3:
        return expr

    f, x, n = args[0], args[1], args[2]
    n_val = evaluate(n, context)

    if not is_integer(n_val) or n_val < 0:
        return expr

    results = [evaluate(x, context)]
    result = results[0]
    for _ in range(n_val):
        result = evaluate(Expression(f, result), context)
        results.append(result)

    return Expression(Symbol("List"), *results)


Fold = Symbol("Fold")


@register_builtin(Fold, attributes={HoldAll}, auto_evaluate=False)
def fold_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """
    Fold[f, expr, list]. Left fold: f[f[f[expr, x1], x2], x3]...
    """
    from minimatic.eval import evaluate

    args = expr.args
    if len(args) < 3:
        return expr

    f, init, lst = args[0], args[1], args[2]
    result = evaluate(init, context)
    lst_val = evaluate(lst, context)

    if is_expr(lst_val) and is_symbol(lst_val.head) and lst_val.head.name == "List":
        for item in lst_val.args:
            result = evaluate(Expression(f, result, item), context)

    return result


Map = Symbol("Map")


@register_builtin(Map, attributes={HoldFirst}, auto_evaluate=False)
def map_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """
    Map[f, expr]. Apply f to each element of expr (must have List head).
    """
    from minimatic.eval import evaluate

    args = expr.args
    if len(args) < 2:
        return expr

    f, lst = args[0], args[1]
    lst_val = evaluate(lst, context)

    if is_expr(lst_val) and is_symbol(lst_val.head) and lst_val.head.name == "List":
        results = [evaluate(Expression(f, item), context) for item in lst_val.args]
        return Expression(Symbol("List"), *results)

    return expr


# ═══════════════════════════════════════════════════════════════════════════════
# SCOPING
# ═══════════════════════════════════════════════════════════════════════════════

Module = Symbol("Module")


@register_builtin(Module, attributes={HoldAll}, auto_evaluate=False)
def module_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """
    Module[{x=1, y=2}, body]. Lexical scoping with unique local variables.
    Each variable gets a gensym'd name, values are substituted into body.
    """
    from minimatic.eval import evaluate

    args = expr.args
    if len(args) < 2:
        return expr

    locals_spec = args[0]
    body = args[1]

    # Parse local variable specifications
    bindings = {}
    if is_expr(locals_spec) and is_symbol(locals_spec.head) and locals_spec.head.name == "List":
        for item in locals_spec.args:
            if is_symbol(item):
                # {x} form - local with no initial value
                local_sym = gensym(item.name)
                bindings[item] = local_sym
            elif is_expr(item) and is_symbol(item.head) and item.head.name == "Set" and len(item.args) == 2:
                # {x = val} form
                local_sym = gensym(item.args[0].name)
                val = evaluate(item.args[1], context)
                context.set_own_values(local_sym, [(local_sym, val, None)])
                bindings[item.args[0]] = local_sym
            elif is_expr(item) and is_symbol(item.head) and item.head.name == "Rule" and len(item.args) == 2:
                # {x -> val} form
                local_sym = gensym(item.args[0].name)
                val = evaluate(item.args[1], context)
                context.set_own_values(local_sym, [(local_sym, val, None)])
                bindings[item.args[0]] = local_sym

    # Substitute and evaluate body
    substituted = replace_with_bindings(body, bindings)
    return evaluate(substituted, context)


Block = Symbol("Block")


@register_builtin(Block, attributes={HoldAll}, auto_evaluate=False)
def block_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """
    Block[{x=1, y=2}, body]. Dynamic scoping.
    Temporarily sets OwnValues, evaluates body, then restores.
    """
    from minimatic.eval import evaluate

    args = expr.args
    if len(args) < 2:
        return expr

    locals_spec = args[0]
    body = args[1]

    # Parse and save current values
    saved = {}
    new_ctx = EvaluationContext("Block", parent=context)

    if is_expr(locals_spec) and is_symbol(locals_spec.head) and locals_spec.head.name == "List":
        for item in locals_spec.args:
            if is_symbol(item):
                # {x} form - reset to unevaluated symbol
                saved[item] = context.get_own_values(item)
                new_ctx.set_own_values(item, [])
            elif is_expr(item) and is_symbol(item.head) and item.head.name == "Set" and len(item.args) == 2:
                # {x = val} form
                var = item.args[0]
                val = evaluate(item.args[1], context)
                saved[var] = context.get_own_values(var)
                new_ctx.set_own_values(var, [(var, val, None)])
            elif is_expr(item) and is_symbol(item.head) and item.head.name == "Rule" and len(item.args) == 2:
                # {x -> val} form
                var = item.args[0]
                val = evaluate(item.args[1], context)
                saved[var] = context.get_own_values(var)
                new_ctx.set_own_values(var, [(var, val, None)])

    # Evaluate body in new context
    with with_context(new_ctx):
        result = evaluate(body, new_ctx)

    # Restore original values
    for sym, values in saved.items():
        context.set_own_values(sym, values)

    return result


With = Symbol("With")


@register_builtin(With, attributes={HoldAll}, auto_evaluate=False)
def with_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """
    With[{x=val}, body]. Constant substitution (like Module but values are pre-evaluated).
    """
    from minimatic.eval import evaluate

    args = expr.args
    if len(args) < 2:
        return expr

    locals_spec = args[0]
    body = args[1]

    # Parse and evaluate all values first
    bindings = {}
    if is_expr(locals_spec) and is_symbol(locals_spec.head) and locals_spec.head.name == "List":
        for item in locals_spec.args:
            if is_expr(item) and is_symbol(item.head) and item.head.name == "Set" and len(item.args) == 2:
                # {x = val} form
                bindings[item.args[0]] = evaluate(item.args[1], context)
            elif is_expr(item) and is_symbol(item.head) and item.head.name == "Rule" and len(item.args) == 2:
                # {x -> val} form
                bindings[item.args[0]] = evaluate(item.args[1], context)

    # Substitute into body and evaluate
    substituted = replace_with_bindings(body, bindings)
    return evaluate(substituted, context)


# ═══════════════════════════════════════════════════════════════════════════════
# PREDICATES
# ═══════════════════════════════════════════════════════════════════════════════

TrueQ = Symbol("TrueQ")


@register_builtin(TrueQ, auto_evaluate=True)
def trueq_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """TrueQ[expr]. Returns True if expr is True, else False."""
    from minimatic.eval import evaluate

    args = expr.args
    if len(args) < 1:
        return False
    result = evaluate(args[0], context)
    return result is True or result is Symbol("True")


SameQ = Symbol("SameQ")


@register_builtin(SameQ, auto_evaluate=True)
def sameq_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """SameQ[a, b]. Structural equality (===)."""
    from minimatic.eval import evaluate

    args = expr.args
    if len(args) < 2:
        return expr
    a = evaluate(args[0], context)
    b = evaluate(args[1], context)
    return a == b


UnsameQ = Symbol("UnsameQ")


@register_builtin(UnsameQ, auto_evaluate=True)
def unsameq_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """UnsameQ[a, b]. Structural inequality."""
    from minimatic.eval import evaluate

    args = expr.args
    if len(args) < 2:
        return expr
    a = evaluate(args[0], context)
    b = evaluate(args[1], context)
    return a != b


NumericQ = Symbol("NumericQ")


@register_builtin(NumericQ, auto_evaluate=True)
def numericq_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """NumericQ[expr]. Returns True if expr is numeric."""
    from minimatic.eval import evaluate

    args = expr.args
    if len(args) < 1:
        return False
    result = evaluate(args[0], context)
    return is_numeric(result) and not isinstance(result, bool)


AtomQ = Symbol("AtomQ")


@register_builtin(AtomQ, auto_evaluate=True)
def atomq_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """AtomQ[expr]. Returns True if expr is atomic (not an Expression)."""
    from minimatic.eval import evaluate

    args = expr.args
    if len(args) < 1:
        return False
    result = evaluate(args[0], context)
    return not is_expr(result)


HeadQ = Symbol("HeadQ")


@register_builtin(HeadQ, auto_evaluate=True)
def headq_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """HeadQ[expr, head]. Returns True if head of expr is head."""
    from minimatic.eval import evaluate

    args = expr.args
    if len(args) < 2:
        return False
    obj = evaluate(args[0], context)
    head = evaluate(args[1], context)
    if is_expr(obj):
        return obj.head == head
    elif is_symbol(obj):
        return Symbol("Symbol") == head
    return False


ListQ = Symbol("ListQ")


@register_builtin(ListQ, auto_evaluate=True)
def listq_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """ListQ[expr]. Returns True if expr has List head."""
    from minimatic.eval import evaluate

    args = expr.args
    if len(args) < 1:
        return False
    result = evaluate(args[0], context)
    return is_expr(result) and is_symbol(result.head) and result.head.name == "List"


StringQ = Symbol("StringQ")


@register_builtin(StringQ, auto_evaluate=True)
def stringq_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """StringQ[expr]. Returns True if expr is a string."""
    from minimatic.eval import evaluate

    args = expr.args
    if len(args) < 1:
        return False
    result = evaluate(args[0], context)
    return is_string(result)


IntegerQ = Symbol("IntegerQ")


@register_builtin(IntegerQ, auto_evaluate=True)
def integerq_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """IntegerQ[expr]. Returns True if expr is an integer."""
    from minimatic.eval import evaluate

    args = expr.args
    if len(args) < 1:
        return False
    result = evaluate(args[0], context)
    return is_integer(result)


RealQ = Symbol("RealQ")


@register_builtin(RealQ, auto_evaluate=True)
def realq_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """RealQ[expr]. Returns True if expr is a real number."""
    from minimatic.eval import evaluate

    args = expr.args
    if len(args) < 1:
        return False
    result = evaluate(args[0], context)
    return is_real(result)
