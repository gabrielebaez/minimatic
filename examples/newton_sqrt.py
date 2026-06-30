"""
Newton's Method for Square Roots
================================
Demonstrates iterative numerical computation in minimatic.
Uses: Module, While, Set, arithmetic, comparison.
"""

from minimatic import Expression, GlobalContext, Symbol, evaluate
from minimatic.builtins import arithmetic, comparison, control  # noqa: F401

ctx = GlobalContext

# --- Symbol declarations ---
Plus = Symbol("Plus")
Times = Symbol("Times")
Divide = Symbol("Divide")
Power = Symbol("Power")
Subtract = Symbol("Subtract")
Abs = Symbol("Abs")
Greater = Symbol("Greater")
Set = Symbol("Set")
While = Symbol("While")
Module = Symbol("Module")
List = Symbol("List")
CompoundExpression = Symbol("CompoundExpression")

n = Symbol("n")
guess = Symbol("guess")
tol = Symbol("tol")
iters = Symbol("iters")


# --- Expression helpers ---
def plus(*args):
    return Expression(Plus, *args)


def times(*args):
    return Expression(Times, *args)


def divide(a, b):
    return Expression(Divide, a, b)


def power(a, b):
    return Expression(Power, a, b)


def subtract(a, b):
    return Expression(Subtract, a, b)


def abs_val(x):
    return Expression(Abs, x)


def greater(a, b):
    return Expression(Greater, a, b)


# --- Newton's method ---
def newton_sqrt(n_val):
    """
    Compute sqrt(n_val) via Newton's iteration:
        guess <- (guess + n/guess) / 2
    Returns List[approximation, iteration_count].
    """
    return evaluate(
        Expression(
            Module,
            # {guess = n/2, tol = 1e-10, iters = 0}
            Expression(
                List,
                Expression(Set, guess, divide(n_val, 2)),
                Expression(Set, tol, 1e-10),
                Expression(Set, iters, 0),
            ),
            # CompoundExpression[While[...], List[guess, iters]]
            Expression(
                CompoundExpression,
                # While[|guess^2 - n| > tol, ...]
                Expression(
                    While,
                    greater(abs_val(subtract(power(guess, 2), n_val)), tol),
                    Expression(
                        CompoundExpression,
                        # guess = (guess + n/guess) / 2
                        Expression(
                            Set,
                            guess,
                            divide(plus(guess, divide(n_val, guess)), 2),
                        ),
                        # iters = iters + 1
                        Expression(Set, iters, plus(iters, 1)),
                    ),
                ),
                # return {guess, iters}
                Expression(List, guess, iters),
            ),
        ),
        ctx,
    )


# --- Run ---
if __name__ == "__main__":
    print("Newton's Method for Square Roots")
    print("=" * 45)

    test_cases = [2, 4, 9, 25, 100, 0.5]

    for val in test_cases:
        result = newton_sqrt(val)
        approx = result.args[0]
        steps = result.args[1]
        print(f"sqrt({val}) = {approx:.10f}  ({steps} iterations)")
