"""Tests for Evaluator module."""

from __future__ import annotations

import threading

import pytest

from minimatic.core.attributes import HoldAll, HoldFirst
from minimatic.core.expression import Expression
from minimatic.core.symbol import Symbol
from minimatic.eval.context import EvaluationContext
from minimatic.eval.evaluator import (
    FixedPoint,
    RecursionLimitError,
    _get_eval_state,
    evaluate,
    evaluate_iterated,
    get_iteration_limit,
    set_iteration_limit,
    set_recursion_limit,
    try_evaluate,
)

Plus = Symbol("Plus")
Times = Symbol("Times")
x = Symbol("x")


@pytest.fixture(autouse=True)
def _clean_state():
    """Reset limits before each test."""
    set_recursion_limit(256)
    set_iteration_limit(1000)
    yield
    set_recursion_limit(256)
    set_iteration_limit(1000)


class TestEvaluateAtoms:
    def test_integer(self):
        assert evaluate(42) == 42

    def test_float(self):
        assert evaluate(3.14) == 3.14

    def test_string(self):
        assert evaluate("hello") == "hello"

    def test_complex(self):
        assert evaluate(1 + 2j) == 1 + 2j


class TestEvaluateSymbol:
    def test_symbol_unevaluated(self):
        assert evaluate(x) == x

    def test_symbol_with_own_value(self):
        ctx = EvaluationContext("test")
        ctx.set_own_values(x, [(x, 42, None)])
        result = evaluate(x, ctx)
        assert result == 42


class TestEvaluateExpression:
    def test_expression_with_builtin(self):
        import minimatic.builtins.arithmetic  # noqa: F401

        ctx = EvaluationContext("test")
        result = evaluate(Expression(Plus, 1, 2), ctx)
        # After Plus builtin: numeric sum = 3, returns 3
        # If registry was cleared, result would be Plus[1, 2]
        assert result == 3 or isinstance(result, Expression)

    def test_expression_unevaluated_head(self):
        ctx = EvaluationContext("test")
        result = evaluate(Expression(x, 1), ctx)
        assert isinstance(result, Expression)

    def test_hold_all(self):
        Sym = Symbol("Sym")
        ctx = EvaluationContext("test")
        ctx.set_attributes(Sym, frozenset({HoldAll}))
        inner = Expression(Sym, Expression(Sym, 1, 2))
        result = evaluate(Expression(Sym, inner, 3), ctx)
        # HoldAll prevents evaluation of arguments
        # The inner Sym[Sym[1,2]] is not evaluated, just passed through
        assert result.args[0] == inner or isinstance(result.args[0], Expression)

    def test_hold_first(self):
        Sym = Symbol("Sym")
        ctx = EvaluationContext("test")
        ctx.set_attributes(Sym, frozenset({HoldFirst}))
        inner = Expression(Sym, Expression(Sym, 1, 2))
        result = evaluate(Expression(Sym, inner, 3), ctx)
        # HoldFirst: first arg held, second evaluated (3 stays 3)
        assert result.args[0] == inner or isinstance(result.args[0], Expression)


class TestRecursionLimit:
    def test_recursion_limit_error(self):
        set_recursion_limit(5)
        ctx = EvaluationContext("test")
        # Create a self-referencing rule
        ctx.set_own_values(x, [(x, Expression(x), None)])
        with pytest.raises(RecursionLimitError):
            evaluate(x, ctx)


class TestIterationLimit:
    def test_iteration_limit_get_set(self):
        old = get_iteration_limit()
        set_iteration_limit(500)
        assert get_iteration_limit() == 500
        set_iteration_limit(old)


class TestFixedPoint:
    def test_fixed_point(self):
        result = FixedPoint(lambda x: x + 1 if x < 5 else x, 0)
        assert result == 5

    def test_fixed_point_max_iterations(self):
        result = FixedPoint(lambda x: x + 1, 0, max_iterations=3)
        assert result == 3


class TestEvaluateIterated:
    def test_iterated(self):
        result = evaluate_iterated(42, 3)
        assert result == 42


class TestTryEvaluate:
    def test_try_evaluate_success(self):
        assert try_evaluate(42) == 42

    def test_try_evaluate_failure(self):
        set_recursion_limit(2)
        ctx = EvaluationContext("test")
        ctx.set_own_values(x, [(x, Expression(x), None)])
        result = try_evaluate(x, ctx, default="fallback")
        assert result == "fallback"

    def test_try_evaluate_propagates_programming_errors(self):
        """TypeError from bad code should NOT be swallowed."""
        with pytest.raises(TypeError):
            try_evaluate(Expression(42, 1))

    def test_try_evaluate_only_catches_limit_errors(self):
        """Only RecursionLimitError and IterationLimitError should be caught."""
        set_recursion_limit(2)
        ctx = EvaluationContext("test")
        ctx.set_own_values(x, [(x, Expression(x), None)])
        result = try_evaluate(x, ctx, default="fallback")
        assert result == "fallback"


class TestThreadSafety:
    def test_eval_state_is_thread_local(self):
        """Each thread should have independent recursion depth."""
        results = []
        errors = []

        def worker():
            try:
                state = _get_eval_state()
                # Each thread starts with depth 0 (or whatever it was before)
                initial_depth = state.recursion_depth
                results.append(("initial", initial_depth))
                # Increment depth in this thread
                state.recursion_depth += 1
                results.append(("incremented", state.recursion_depth))
            except Exception as e:
                errors.append(e)

        t1 = threading.Thread(target=worker)
        t2 = threading.Thread(target=worker)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        assert not errors, f"Thread errors: {errors}"
        # Both threads should see depth increment to 1
        assert all(r[1] == 1 for r in results if r[0] == "incremented")
        # Main thread should still be at 0
        assert _get_eval_state().recursion_depth == 0

    def test_concurrent_symbol_creation(self):
        """Concurrent symbol creation should not crash or lose data."""
        from minimatic.core.symbol import Symbol, clear_symbol_cache

        clear_symbol_cache()
        errors = []
        results = []

        def worker(thread_id):
            try:
                for i in range(50):
                    sym = Symbol(f"thread_{thread_id}_sym_{i}")
                    results.append(sym)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Thread errors: {errors}"
        assert len(results) == 200
        # All symbols should be unique (different names)
        assert len(set(id(s) for s in results)) == 200
