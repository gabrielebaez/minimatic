"""Tests for Rules module."""

from __future__ import annotations

from minimatic.core.expression import Expression, is_expr
from minimatic.core.symbol import Symbol
from minimatic.eval.rules import (
    RuleDelayed,
    RuleImmediate,
    apply_rule,
    apply_rules_repeatedly,
    is_rule,
    is_rule_delayed,
    is_rule_immediate,
    try_rules,
)
from minimatic.pattern.structural import pattern

Plus = Symbol("Plus")
x = Symbol("x")
y = Symbol("y")


class TestRuleCreation:
    def test_immediate_rule(self):
        r = RuleImmediate(x, 42)
        assert r.lhs == x
        assert r.rhs == 42
        assert r.is_immediate()
        assert not r.is_delayed()

    def test_delayed_rule(self):
        r = RuleDelayed(x, 42)
        assert r.is_delayed()
        assert not r.is_immediate()

    def test_rule_with_condition(self):
        cond = Symbol("True")
        r = RuleImmediate(x, 42, condition=cond)
        assert r.condition == cond

    def test_rule_with_priority(self):
        r = RuleImmediate(x, 42, priority=10)
        assert r.priority == 10


class TestRuleTypeCheck:
    def test_is_rule(self):
        assert is_rule(RuleImmediate(x, 42))
        assert not is_rule(42)

    def test_is_rule_immediate(self):
        assert is_rule_immediate(RuleImmediate(x, 42))
        assert not is_rule_immediate(RuleDelayed(x, 42))

    def test_is_rule_delayed(self):
        assert is_rule_delayed(RuleDelayed(x, 42))
        assert not is_rule_delayed(RuleImmediate(x, 42))


class TestApplyRule:
    def test_apply_immediate(self):
        r = RuleImmediate(x, 42)
        result, success = apply_rule(r, x)
        assert success
        assert result == 42

    def test_apply_delayed(self):
        r = RuleDelayed(x, 42)
        result, success = apply_rule(r, x)
        assert success
        assert result == 42

    def test_apply_no_match(self):
        r = RuleImmediate(x, 42)
        result, success = apply_rule(r, y)
        assert not success
        assert result == y

    def test_apply_with_pattern(self):
        pat = pattern(x)
        r = RuleImmediate(pat, 42)
        result, success = apply_rule(r, 99)
        assert success
        assert result == 42

    def test_apply_callable_rhs(self):
        def my_func(bindings):
            val = bindings.get(x)
            if val is None:
                return 0
            return val * 2

        r = RuleImmediate(pattern(x), my_func)
        result, success = apply_rule(r, 5)
        assert success
        assert result == 10


class TestTryRules:
    def test_try_rules_first_match(self):
        rules = [
            RuleImmediate(x, 1),
            RuleImmediate(x, 2),
        ]
        result = try_rules(rules, x)
        assert result == 1

    def test_try_rules_no_match(self):
        rules = [RuleImmediate(x, 42)]
        result = try_rules(rules, y)
        assert result == y

    def test_try_rules_priority(self):
        rules = [
            RuleImmediate(x, 1, priority=0),
            RuleImmediate(x, 2, priority=10),
        ]
        result = try_rules(rules, x)
        assert result == 2


class TestApplyRulesRepeatedly:
    def test_repeated_until_fixed_point(self):
        rules = [RuleImmediate(x, x)]
        result = apply_rules_repeatedly(rules, x)
        assert result == x

    def test_repeated_changes(self):
        # This rule never stabilizes, should hit max iterations
        rules = [RuleImmediate(x, Expression(Plus, x, 1))]
        result = apply_rules_repeatedly(rules, x, max_iterations=3)
        assert result == x or is_expr(result)


class TestRuleRepr:
    def test_repr_immediate(self):
        r = RuleImmediate(x, 42)
        assert "->" in repr(r)

    def test_repr_delayed(self):
        r = RuleDelayed(x, 42)
        assert ":>" in repr(r)
