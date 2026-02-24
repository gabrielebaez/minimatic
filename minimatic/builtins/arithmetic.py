"""
Arithmetic built-in functions.

Implements Plus, Times, Power, and related operations following
Wolfram Language semantics with proper attribute handling.
"""

from __future__ import annotations

import math
from typing import Any, List

from minimatic.core import Symbol, Expression, is_expr
from minimatic.core.attributes import Flat, Orderless, Listable, NumericFunction, HoldRest
from minimatic.eval.context import EvaluationContext

from .registry import register_builtin


# Numeric type checking
def is_number(x: Any) -> bool:
    """Check if x is a numeric type (int, float, complex)."""
    return isinstance(x, (int, float, complex))


def is_real(x: Any) -> bool:
    """Check if x is a real number."""
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def is_integer(x: Any) -> bool:
    """Check if x is an integer."""
    return isinstance(x, int) and not isinstance(x, bool)


def is_complex(x: Any) -> bool:
    """Check if x is complex."""
    return isinstance(x, complex)


def flatten_associative(args: List[Any], identity: Any) -> List[Any]:
    """Flatten nested associative operations (for Flat attribute)."""
    result = []
    for arg in args:
        if arg == identity:
            continue
        result.append(arg)
    return result


def numeric_plus(args: List[Any]) -> Any:
    """Compute numeric sum of arguments."""
    total = 0
    symbolic = []

    for arg in args:
        if is_number(arg):
            total += arg
        else:
            symbolic.append(arg)

    if total != 0 or not symbolic:
        symbolic.insert(0, total)

    return symbolic if len(symbolic) > 1 else (symbolic[0] if symbolic else 0)


def numeric_times(args: List[Any]) -> Any:
    """Compute numeric product of arguments."""
    prod = 1
    symbolic = []

    for arg in args:
        if is_number(arg):
            prod *= arg
        else:
            symbolic.append(arg)

    # Handle special cases
    if prod == 0:
        return 0
    if prod == 1 and symbolic:
        return symbolic if len(symbolic) > 1 else symbolic[0]
    if not symbolic:
        return prod

    symbolic.insert(0, prod)
    return symbolic if len(symbolic) > 1 else symbolic[0]


# ----- Plus (+) -----

Plus = Symbol("Plus")

@register_builtin(
    Plus,
    attributes={Flat, Orderless, Listable, NumericFunction},
    auto_evaluate=True
)
def plus_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """
    Implement Plus with Wolfram Language semantics.

    Attributes: Flat (associative), Orderless (commutative), Listable
    """
    args = list(expr.args)

    # Handle single argument
    if len(args) == 0:
        return 0
    if len(args) == 1:
        return args[0]

    # Flatten nested Plus (Flat attribute)
    flat_args = []
    for arg in args:
        if is_expr(arg) and arg.head == Plus:
            flat_args.extend(arg.args)
        else:
            flat_args.append(arg)

    # Separate numeric and symbolic parts
    numeric_sum = 0
    symbolic_terms = []

    for arg in flat_args:
        if is_number(arg):
            numeric_sum += arg
        elif is_expr(arg) and arg.head == Times:
            # Check for numeric coefficient in Times
            coeff, rest = extract_numeric_coefficient(arg)
            if coeff is not None:
                if coeff != 1 or not rest:
                    if rest:
                        term = (Times, coeff, rest)
                    else:
                        term = coeff
                    # Combine like terms would go here
                    symbolic_terms.append(arg)  # Simplified
                else:
                    symbolic_terms.append(rest)
            else:
                symbolic_terms.append(arg)
        else:
            symbolic_terms.append(arg)

    # Simplify: if no symbolic terms, return numeric sum
    if not symbolic_terms:
        return numeric_sum

    # Build result
    result_args = []
    if numeric_sum != 0:
        result_args.append(numeric_sum)

    # Sort for canonical order (Orderless)
    # Simplified: just keep as-is for now
    result_args.extend(symbolic_terms)

    if len(result_args) == 1:
        return result_args[0]

    return Expression(Plus, *result_args)


def extract_numeric_coefficient(expr: Expression) -> tuple:
    """
    Extract numeric coefficient from Times expression.
    Returns (coefficient, rest) or (None, None) if no numeric part.
    """
    if not (is_expr(expr) and expr.head == Symbol("Times")):
        return (None, None)

    numeric_parts = []
    symbolic_parts = []

    for arg in expr.args:
        if is_number(arg):
            numeric_parts.append(arg)
        else:
            symbolic_parts.append(arg)

    if not numeric_parts:
        return (None, None)

    coeff = 1
    for n in numeric_parts:
        coeff *= n

    if not symbolic_parts:
        return (coeff, None)

    if len(symbolic_parts) == 1:
        return (coeff, symbolic_parts[0])

    rest = Expression(Symbol("Times"), *symbolic_parts)
    return (coeff, rest)


# ----- Times (*) -----

Times = Symbol("Times")

@register_builtin(
    Times,
    attributes={Flat, Orderless, Listable, NumericFunction},
    auto_evaluate=True
)
def times_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """
    Implement Times with Wolfram Language semantics.

    Attributes: Flat (associative), Orderless (commutative), Listable
    """
    args = list(expr.args)

    # Handle special cases
    if len(args) == 0:
        return 1
    if len(args) == 1:
        return args[0]

    # Check for zero factor
    for arg in args:
        if arg == 0:
            return 0

    # Flatten nested Times (Flat attribute)
    flat_args = []
    for arg in args:
        if is_expr(arg) and arg.head == Times:
            flat_args.extend(arg.args)
        else:
            flat_args.append(arg)

    # Separate numeric and symbolic parts
    numeric_prod = 1
    symbolic_factors = []

    for arg in flat_args:
        if is_number(arg):
            numeric_prod *= arg
        else:
            symbolic_factors.append(arg)

    # Simplify
    if numeric_prod == 0:
        return 0
    if numeric_prod == 1 and not symbolic_factors:
        return 1
    if not symbolic_factors:
        return numeric_prod

    # Build result
    result_args = []
    if numeric_prod != 1:
        result_args.append(numeric_prod)

    result_args.extend(symbolic_factors)

    if len(result_args) == 1:
        return result_args[0]

    return Expression(Times, *result_args)


# ----- Power (^) -----

Power = Symbol("Power")

@register_builtin(
    Power,
    attributes={NumericFunction, Listable},  # NOT Flat or Orderless
    auto_evaluate=True
)
def power_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """
    Implement Power (exponentiation).

    Power[a, b] represents a^b.
    Attributes: NumericFunction, Listable (but NOT Flat or Orderless)
    """
    args = list(expr.args)

    if len(args) != 2:
        # Wolfram Language allows Power[a] -> a
        if len(args) == 1:
            return args[0]
        return expr  # Invalid arity

    base, exp = args

    # Numeric evaluation
    if is_number(base) and is_number(exp):
        try:
            # Handle special cases
            if base == 0:
                if exp > 0:
                    return 0
                # 0^0 or 0^negative is undefined or infinity
            if base == 1:
                return 1
            if exp == 0:
                return 1
            if exp == 1:
                return base

            result = base ** exp

            # Convert to int if it's a whole number
            if isinstance(result, float) and result.is_integer():
                return int(result)
            return result
        except (OverflowError, ZeroDivisionError):
            return Expression(Power, base, exp)

    # Symbolic simplifications
    if exp == 0:
        return 1
    if exp == 1:
        return base
    if base == 1:
        return 1

    # Sqrt[x] is Power[x, 1/2]
    # Keep as expression
    return Expression(Power, base, exp)


# ----- Minus -----

Minus = Symbol("Minus")

@register_builtin(
    Minus,
    attributes={Listable, NumericFunction},
    auto_evaluate=True
)
def minus_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """Unary minus: -x implemented as Times[-1, x]."""
    args = list(expr.args)

    if len(args) != 1:
        return expr

    arg = args[0]

    # Times[-1, arg]
    return Expression(Times, -1, arg)


# ----- Divide -----

Divide = Symbol("Divide")

@register_builtin(
    Divide,
    attributes={Listable, NumericFunction},
    auto_evaluate=True
)
def divide_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """Division: a / b implemented as Times[a, Power[b, -1]]."""
    args = list(expr.args)

    if len(args) != 2:
        return expr

    num, den = args

    # Times[num, Power[den, -1]]
    if is_number(den) and den != 0:
        return Expression(Times, num, 1 / den)

    return Expression(Times, num, Expression(Power, den, -1))


# ----- Subtract -----

Subtract = Symbol("Subtract")

@register_builtin(
    Subtract,
    attributes={Listable, NumericFunction},
    auto_evaluate=True
)
def subtract_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """Subtraction: a - b implemented as Plus[a, Times[-1, b]]."""
    args = list(expr.args)

    if len(args) != 2:
        return expr

    a, b = args

    # Plus[a, Times[-1, b]]
    return Expression(Plus, a, Expression(Times, -1, b))


# ----- Abs -----

Abs = Symbol("Abs")

@register_builtin(
    Abs,
    attributes={Listable, NumericFunction},
    auto_evaluate=True
)
def abs_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """Absolute value."""
    args = list(expr.args)

    if len(args) != 1:
        return expr

    arg = args[0]

    if is_number(arg):
        if is_complex(arg):
            return abs(arg)
        return abs(arg)

    # Symbolic: Abs[-x] -> Abs[x]
    if is_expr(arg) and arg.head == Times:
        # Extract sign
        first = arg.args[0]
        if is_number(first) and first < 0:
            rest = arg.args[1:] if len(arg.args) > 2 else arg.args[1]
            if len(arg.args) == 2:
                rest = arg.args[1]
            else:
                rest = Expression(Times, *arg.args[1:])
            return Expression(Abs, Expression(Times, -first, rest))

    return Expression(Abs, arg)


# ----- Sqrt -----

Sqrt = Symbol("Sqrt")

@register_builtin(
    Sqrt,
    attributes={Listable, NumericFunction},
    auto_evaluate=True
)
def sqrt_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """Square root: Sqrt[x] == Power[x, 1/2]."""
    args = list(expr.args)

    if len(args) != 1:
        return expr

    arg = args[0]

    if is_number(arg):
        if arg >= 0:
            result = math.sqrt(arg)
            # Return int if perfect square
            if result == int(result):
                return int(result)
            return result
        # Negative: complex result
        return complex(arg) ** 0.5

    return Expression(Power, arg, Symbol("Rational")(1, 2) if False else 0.5)


# ----- Exp -----

Exp = Symbol("Exp")

@register_builtin(
    Exp,
    attributes={Listable, NumericFunction},
    auto_evaluate=True
)
def exp_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """Exponential function: E^x."""
    args = list(expr.args)

    if len(args) != 1:
        return expr

    arg = args[0]

    if is_number(arg):
        return math.exp(arg) if is_real(arg) else complex(math.e) ** arg

    # E^0 = 1
    if arg == 0:
        return 1

    return Expression(Power, Symbol("E"), arg)


# ----- Log -----

Log = Symbol("Log")

@register_builtin(
    Log,
    attributes={Listable, NumericFunction},
    auto_evaluate=True
)
def log_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """
    Natural logarithm: Log[x] or Log[b, z] for base b.
    """
    args = list(expr.args)

    if len(args) == 1:
        # Natural log
        arg = args[0]
        if is_number(arg):
            if is_real(arg) and arg > 0:
                return math.log(arg)
            # Complex or negative
            return complex(arg).log() if hasattr(complex(arg), 'log') else math.log(abs(arg), math.e)
        return Expression(Log, arg)

    elif len(args) == 2:
        # Log base b of z
        base, arg = args
        if is_number(base) and is_number(arg):
            if is_real(base) and is_real(arg) and base > 0 and arg > 0:
                return math.log(arg, base)
        return Expression(Log, arg, base) / Expression(Log, base) if False else expr

    return expr


# ----- Sum -----

Sum = Symbol("Sum")

@register_builtin(
    Sum,
    attributes={HoldRest},  # Hold iterator specifications
    auto_evaluate=False
)
def sum_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """
    Summation: Sum[expr, {i, imin, imax}] or Sum[expr, {i, imax}].
    """
    from minimatic.eval import evaluate

    args = list(expr.args)
    if len(args) < 1:
        return expr

    summand = args[0]

    if len(args) == 1:
        return summand  # No iterators

    # Handle iterators - this is a simplified version
    iterators = args[1:]

    # Try to evaluate finite sums numerically
    result = 0
    for iter_spec in iterators:
        if not is_expr(iter_spec) or len(iter_spec.args) < 2:
            return expr  # Invalid iterator

        iter_args = iter_spec.args
        var = iter_args[0]

        if len(iter_args) == 2:
            # {i, imax} form - starts at 1
            imax = evaluate(iter_args[1], context)
            if is_integer(imax) and imax > 0:
                for i in range(1, imax + 1):
                    # Substitute and evaluate
                    from minimatic.pattern import replace_with_bindings
                    from minimatic.pattern import MatchResult, Bindings
                    substituted = replace_with_bindings(summand, {var: i})
                    result += evaluate(substituted, context)
                return result

    # Return unevaluated if we can't compute
    return Expression(Sum, summand, *iterators)


# ----- Product -----

Product = Symbol("Product")

@register_builtin(
    Product,
    attributes={HoldRest},
    auto_evaluate=False
)
def product_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """Product: Product[expr, {i, imin, imax}]."""
    from minimatic.eval import evaluate

    args = list(expr.args)
    if len(args) < 1:
        return expr

    factor = args[0]

    if len(args) == 1:
        return factor

    iterators = args[1:]

    # Try to evaluate finite products numerically
    result = 1
    for iter_spec in iterators:
        if not is_expr(iter_spec) or len(iter_spec.args) < 2:
            return expr

        iter_args = iter_spec.args
        var = iter_args[0]

        if len(iter_args) == 2:
            imax = evaluate(iter_args[1], context)
            if is_integer(imax) and imax > 0:
                for i in range(1, imax + 1):
                    from minimatic.pattern import replace_with_bindings
                    substituted = replace_with_bindings(factor, {var: i})
                    result *= evaluate(substituted, context)
                return result

    return Expression(Product, factor, *iterators)
