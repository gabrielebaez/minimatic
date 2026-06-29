"""Tests for Arithmetic builtins module."""

from __future__ import annotations

# Force registration of builtins
import minimatic.builtins.arithmetic  # noqa: F401
from minimatic.core.expression import Expression, is_expr
from minimatic.core.symbol import Symbol
from minimatic.eval.evaluator import evaluate

Plus = Symbol("Plus")
Times = Symbol("Times")
Power = Symbol("Power")
Minus = Symbol("Minus")
Divide = Symbol("Divide")
Subtract = Symbol("Subtract")
Abs = Symbol("Abs")
Sqrt = Symbol("Sqrt")
Exp = Symbol("Exp")
Log = Symbol("Log")
Sum = Symbol("Sum")
Product = Symbol("Product")


class TestPlus:
    def test_plus_numeric(self, ctx):
        assert evaluate(Expression(Plus, 1, 2, 3), ctx) == 6

    def test_plus_single(self, ctx):
        assert evaluate(Expression(Plus, 5), ctx) == 5

    def test_plus_zero(self, ctx):
        assert evaluate(Expression(Plus), ctx) == 0

    def test_plus_mixed(self, ctx):
        result = evaluate(Expression(Plus, 1, Symbol("x"), 2), ctx)
        assert is_expr(result)
        assert result.head == Plus
        assert 3 in result.args

    def test_plus_float(self, ctx):
        assert evaluate(Expression(Plus, 1.5, 2.5), ctx) == 4.0


class TestTimes:
    def test_times_numeric(self, ctx):
        assert evaluate(Expression(Times, 2, 3, 4), ctx) == 24

    def test_times_single(self, ctx):
        assert evaluate(Expression(Times, 5), ctx) == 5

    def test_times_one(self, ctx):
        assert evaluate(Expression(Times), ctx) == 1

    def test_times_zero(self, ctx):
        assert evaluate(Expression(Times, 0, Symbol("x")), ctx) == 0

    def test_times_mixed(self, ctx):
        result = evaluate(Expression(Times, 2, Symbol("x")), ctx)
        assert is_expr(result)
        assert result.head == Times


class TestPower:
    def test_power_numeric(self, ctx):
        assert evaluate(Expression(Power, 2, 3), ctx) == 8

    def test_power_zero(self, ctx):
        assert evaluate(Expression(Power, Symbol("x"), 0), ctx) == 1

    def test_power_one(self, ctx):
        x = Symbol("x")
        assert evaluate(Expression(Power, x, 1), ctx) == x

    def test_power_single(self, ctx):
        assert evaluate(Expression(Power, 5), ctx) == 5


class TestMinus:
    def test_minus(self, ctx):
        result = evaluate(Expression(Minus, 5), ctx)
        assert result == -5


class TestDivide:
    def test_divide_numeric(self, ctx):
        result = evaluate(Expression(Divide, 6, 2), ctx)
        assert result == 3.0


class TestSubtract:
    def test_subtract(self, ctx):
        result = evaluate(Expression(Subtract, 5, 3), ctx)
        assert result == 2


class TestAbs:
    def test_abs_positive(self, ctx):
        result = evaluate(Expression(Abs, 5), ctx)
        assert result == 5

    def test_abs_negative(self, ctx):
        result = evaluate(Expression(Abs, -5), ctx)
        assert result == 5


class TestSqrt:
    def test_sqrt_perfect(self, ctx):
        result = evaluate(Expression(Sqrt, 9), ctx)
        assert result == 3

    def test_sqrt_non_perfect(self, ctx):
        result = evaluate(Expression(Sqrt, 2), ctx)
        assert abs(result - 1.4142135623730951) < 1e-10

    def test_sqrt_negative(self, ctx):
        result = evaluate(Expression(Sqrt, -1), ctx)
        assert isinstance(result, complex)


class TestExp:
    def test_exp_numeric(self, ctx):
        import math

        result = evaluate(Expression(Exp, 1), ctx)
        assert abs(result - math.e) < 1e-10

    def test_exp_zero(self, ctx):
        result = evaluate(Expression(Exp, 0), ctx)
        assert result == 1


class TestLog:
    def test_log_one(self, ctx):
        result = evaluate(Expression(Log, 1), ctx)
        assert result == 0

    def test_log_e(self, ctx):
        import math

        result = evaluate(Expression(Log, math.e), ctx)
        assert abs(result - 1) < 1e-10

    def test_log_negative(self, ctx):
        import cmath

        result = evaluate(Expression(Log, -1), ctx)
        # Log(-1) = i*pi in complex
        assert isinstance(result, complex)
        assert abs(result - 1j * cmath.pi) < 1e-10

    def test_log_complex(self, ctx):
        result = evaluate(Expression(Log, 1 + 1j), ctx)
        assert isinstance(result, complex)


class TestPowerBugFix:
    def test_power_overflow(self, ctx):
        # This should not crash - returns unevaluated expression
        result = evaluate(Expression(Power, 10, 1000), ctx)
        # Python handles big integers, so this should work
        assert result == 10**1000

    def test_power_zero_division(self, ctx):
        # 0^(-1) should not crash
        result = evaluate(Expression(Power, 0, -1), ctx)
        # Returns unevaluated
        assert is_expr(result)
        assert result.head == Power


class TestArithmeticIntegration:
    def test_nested_plus_times(self, ctx):
        expr = Expression(Plus, Expression(Times, 2, 3), 4)
        assert evaluate(expr, ctx) == 10

    def test_nested_power_plus(self, ctx):
        expr = Expression(Power, Expression(Plus, 2, 3), 2)
        assert evaluate(expr, ctx) == 25


class TestSumExtended:
    def test_sum_with_range(self, ctx):
        # Sum[i, {i, 1, 10}] = 55
        i = Symbol("i")
        result = evaluate(
            Expression(Sum, i, Expression(Symbol("List"), i, 1, 10)), ctx
        )
        assert result == 55

    def test_sum_with_range_from_5(self, ctx):
        # Sum[i, {i, 5, 8}] = 5+6+7+8 = 26
        i = Symbol("i")
        result = evaluate(
            Expression(Sum, i, Expression(Symbol("List"), i, 5, 8)), ctx
        )
        assert result == 26

    def test_sum_with_step(self, ctx):
        # Sum[i, {i, 0, 10, 2}] = 0+2+4+6+8+10 = 30
        i = Symbol("i")
        result = evaluate(
            Expression(Sum, i, Expression(Symbol("List"), i, 0, 10, 2)), ctx
        )
        assert result == 30

    def test_product_with_range(self, ctx):
        # Product[i, {i, 1, 5}] = 120
        i = Symbol("i")
        result = evaluate(
            Expression(Product, i, Expression(Symbol("List"), i, 1, 5)), ctx
        )
        assert result == 120

    def test_product_with_range_from_2(self, ctx):
        # Product[i, {i, 2, 4}] = 2*3*4 = 24
        i = Symbol("i")
        result = evaluate(
            Expression(Product, i, Expression(Symbol("List"), i, 2, 4)), ctx
        )
        assert result == 24
