"""Tests for Comparison and Logic builtins module."""

from __future__ import annotations

# Force registration of builtins
import minimatic.builtins.comparison  # noqa: F401
from minimatic.core.expression import Expression
from minimatic.core.symbol import Symbol
from minimatic.eval.evaluator import evaluate

Less = Symbol("Less")
Greater = Symbol("Greater")
LessEqual = Symbol("LessEqual")
GreaterEqual = Symbol("GreaterEqual")
Equal = Symbol("Equal")
Unequal = Symbol("Unequal")
And = Symbol("And")
Or = Symbol("Or")
Not = Symbol("Not")
EvenQ = Symbol("EvenQ")
OddQ = Symbol("OddQ")


class TestLess:
    def test_less_true(self, ctx):
        assert evaluate(Expression(Less, 1, 2), ctx) is True

    def test_less_false(self, ctx):
        assert evaluate(Expression(Less, 2, 1), ctx) is False

    def test_less_equal(self, ctx):
        assert evaluate(Expression(Less, 1, 1), ctx) is False

    def test_less_float(self, ctx):
        assert evaluate(Expression(Less, 1.5, 2.0), ctx) is True

    def test_less_int_float(self, ctx):
        assert evaluate(Expression(Less, 1, 1.5), ctx) is True

    def test_less_negative(self, ctx):
        assert evaluate(Expression(Less, -1, 0), ctx) is True

    def test_less_one_arg(self, ctx):
        result = evaluate(Expression(Less, 1), ctx)
        assert result == Expression(Less, 1)

    def test_less_non_numeric(self, ctx):
        result = evaluate(Expression(Less, Symbol("a"), Symbol("b")), ctx)
        assert result == Expression(Less, Symbol("a"), Symbol("b"))


class TestGreater:
    def test_greater_true(self, ctx):
        assert evaluate(Expression(Greater, 2, 1), ctx) is True

    def test_greater_false(self, ctx):
        assert evaluate(Expression(Greater, 1, 2), ctx) is False

    def test_greater_equal(self, ctx):
        assert evaluate(Expression(Greater, 1, 1), ctx) is False

    def test_greater_float(self, ctx):
        assert evaluate(Expression(Greater, 2.0, 1.5), ctx) is True

    def test_greater_negative(self, ctx):
        assert evaluate(Expression(Greater, 0, -1), ctx) is True


class TestLessEqual:
    def test_lessequal_less(self, ctx):
        assert evaluate(Expression(LessEqual, 1, 2), ctx) is True

    def test_lessequal_equal(self, ctx):
        assert evaluate(Expression(LessEqual, 1, 1), ctx) is True

    def test_lessequal_false(self, ctx):
        assert evaluate(Expression(LessEqual, 2, 1), ctx) is False

    def test_lessequal_float(self, ctx):
        assert evaluate(Expression(LessEqual, 1.0, 1.0), ctx) is True


class TestGreaterEqual:
    def test_greaterequal_greater(self, ctx):
        assert evaluate(Expression(GreaterEqual, 2, 1), ctx) is True

    def test_greaterequal_equal(self, ctx):
        assert evaluate(Expression(GreaterEqual, 1, 1), ctx) is True

    def test_greaterequal_false(self, ctx):
        assert evaluate(Expression(GreaterEqual, 1, 2), ctx) is False

    def test_greaterequal_float(self, ctx):
        assert evaluate(Expression(GreaterEqual, 2.0, 1.0), ctx) is True


class TestEqual:
    def test_equal_int(self, ctx):
        assert evaluate(Expression(Equal, 1, 1), ctx) is True

    def test_equal_int_float(self, ctx):
        assert evaluate(Expression(Equal, 1, 1.0), ctx) is True

    def test_equal_false(self, ctx):
        assert evaluate(Expression(Equal, 1, 2), ctx) is False

    def test_equal_float(self, ctx):
        assert evaluate(Expression(Equal, 1.5, 1.5), ctx) is True

    def test_equal_non_numeric(self, ctx):
        result = evaluate(Expression(Equal, Symbol("a"), Symbol("a")), ctx)
        assert result == Expression(Equal, Symbol("a"), Symbol("a"))


class TestUnequal:
    def test_unequal_true(self, ctx):
        assert evaluate(Expression(Unequal, 1, 2), ctx) is True

    def test_unequal_false(self, ctx):
        assert evaluate(Expression(Unequal, 1, 1), ctx) is False

    def test_unequal_int_float(self, ctx):
        assert evaluate(Expression(Unequal, 1, 1.0), ctx) is False


class TestAnd:
    def test_and_both_true(self, ctx):
        assert evaluate(Expression(And, True, True), ctx) is True

    def test_and_first_false(self, ctx):
        assert evaluate(Expression(And, False, True), ctx) is False

    def test_and_second_false(self, ctx):
        assert evaluate(Expression(And, True, False), ctx) is False

    def test_and_both_false(self, ctx):
        assert evaluate(Expression(And, False, False), ctx) is False

    def test_and_short_circuit(self, ctx):
        # False short-circuits: second arg is never evaluated
        assert evaluate(Expression(And, False, Symbol("x")), ctx) is False

    def test_and_no_args(self, ctx):
        assert evaluate(Expression(And), ctx) is True

    def test_and_one_arg_true(self, ctx):
        assert evaluate(Expression(And, True), ctx) is True

    def test_and_one_arg_false(self, ctx):
        assert evaluate(Expression(And, False), ctx) is False

    def test_and_symbol_true(self, ctx):
        assert evaluate(Expression(And, Symbol("True"), Symbol("True")), ctx) is True

    def test_and_symbol_false(self, ctx):
        assert evaluate(Expression(And, Symbol("False"), Symbol("True")), ctx) is False

    def test_and_mixed_unevaluated(self, ctx):
        result = evaluate(Expression(And, True, Symbol("x")), ctx)
        assert result == Expression(And, True, Symbol("x"))


class TestOr:
    def test_or_both_true(self, ctx):
        assert evaluate(Expression(Or, True, True), ctx) is True

    def test_or_first_true(self, ctx):
        assert evaluate(Expression(Or, True, False), ctx) is True

    def test_or_second_true(self, ctx):
        assert evaluate(Expression(Or, False, True), ctx) is True

    def test_or_both_false(self, ctx):
        assert evaluate(Expression(Or, False, False), ctx) is False

    def test_or_short_circuit(self, ctx):
        # True short-circuits: second arg is never evaluated
        assert evaluate(Expression(Or, True, Symbol("x")), ctx) is True

    def test_or_no_args(self, ctx):
        assert evaluate(Expression(Or), ctx) is False

    def test_or_one_arg_true(self, ctx):
        assert evaluate(Expression(Or, True), ctx) is True

    def test_or_one_arg_false(self, ctx):
        assert evaluate(Expression(Or, False), ctx) is False

    def test_or_symbol_true(self, ctx):
        assert evaluate(Expression(Or, Symbol("True"), Symbol("False")), ctx) is True

    def test_or_mixed_unevaluated(self, ctx):
        result = evaluate(Expression(Or, False, Symbol("x")), ctx)
        assert result == Expression(Or, False, Symbol("x"))


class TestNot:
    def test_not_true(self, ctx):
        assert evaluate(Expression(Not, True), ctx) is False

    def test_not_false(self, ctx):
        assert evaluate(Expression(Not, False), ctx) is True

    def test_not_symbol_true(self, ctx):
        assert evaluate(Expression(Not, Symbol("True")), ctx) is False

    def test_not_symbol_false(self, ctx):
        assert evaluate(Expression(Not, Symbol("False")), ctx) is True

    def test_not_unevaluated(self, ctx):
        result = evaluate(Expression(Not, Symbol("x")), ctx)
        assert result == Expression(Not, Symbol("x"))

    def test_not_no_args(self, ctx):
        result = evaluate(Expression(Not), ctx)
        assert result == Expression(Not)


class TestEvenQ:
    def test_evenq_even(self, ctx):
        assert evaluate(Expression(EvenQ, 4), ctx) is True

    def test_evenq_odd(self, ctx):
        assert evaluate(Expression(EvenQ, 3), ctx) is False

    def test_evenq_zero(self, ctx):
        assert evaluate(Expression(EvenQ, 0), ctx) is True

    def test_evenq_negative(self, ctx):
        assert evaluate(Expression(EvenQ, -2), ctx) is True

    def test_evenq_negative_odd(self, ctx):
        assert evaluate(Expression(EvenQ, -3), ctx) is False

    def test_evenq_float(self, ctx):
        assert evaluate(Expression(EvenQ, 4.0), ctx) is False

    def test_evenq_string(self, ctx):
        assert evaluate(Expression(EvenQ, "hello"), ctx) is False

    def test_evenq_no_args(self, ctx):
        assert evaluate(Expression(EvenQ), ctx) is False


class TestOddQ:
    def test_oddq_odd(self, ctx):
        assert evaluate(Expression(OddQ, 3), ctx) is True

    def test_oddq_even(self, ctx):
        assert evaluate(Expression(OddQ, 4), ctx) is False

    def test_oddq_one(self, ctx):
        assert evaluate(Expression(OddQ, 1), ctx) is True

    def test_oddq_negative(self, ctx):
        assert evaluate(Expression(OddQ, -3), ctx) is True

    def test_oddq_negative_even(self, ctx):
        assert evaluate(Expression(OddQ, -4), ctx) is False

    def test_oddq_zero(self, ctx):
        assert evaluate(Expression(OddQ, 0), ctx) is False

    def test_oddq_float(self, ctx):
        assert evaluate(Expression(OddQ, 3.0), ctx) is False

    def test_oddq_string(self, ctx):
        assert evaluate(Expression(OddQ, "hello"), ctx) is False
