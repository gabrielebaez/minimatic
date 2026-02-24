"""
Rule representation and application.

Implements Rule (->) and RuleDelayed (:>) with priority-based
application order and condition checking.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Optional, Callable, Union

from minimatic.core import Expression, Symbol, is_expr
from minimatic.pattern import (
    match, replace_with_bindings, Bindings,
    MatchResult, NO_MATCH,
    pattern_name, is_pattern
)


class RuleType(Enum):
    """Types of rules."""
    IMMEDIATE = auto()   # -> (Rule)
    DELAYED = auto()     # :> (RuleDelayed)


@dataclass(frozen=True)
class Rule:
    """
    A rewrite rule: lhs -> rhs or lhs :> rhs.

    Attributes:
        lhs: Pattern expression to match against
        rhs: Replacement expression or callable
        rule_type: IMMEDIATE or DELAYED
        condition: Optional condition expression
        priority: Priority for rule ordering (higher = tried first)
    """

    lhs: Any
    rhs: Any
    rule_type: RuleType = RuleType.IMMEDIATE
    condition: Optional[Any] = None
    priority: int = 0

    def is_immediate(self) -> bool:
        """Check if this is an immediate rule (->)."""
        return self.rule_type == RuleType.IMMEDIATE

    def is_delayed(self) -> bool:
        """Check if this is a delayed rule (:>)."""
        return self.rule_type == RuleType.DELAYED

    def __repr__(self) -> str:
        arrow = "->" if self.is_immediate() else ":>"
        return f"Rule({self.lhs!r} {arrow} {self.rhs!r})"


# Convenience constructors

def RuleImmediate(lhs: Any, rhs: Any, condition: Optional[Any] = None, priority: int = 0) -> Rule:
    """Create an immediate rule: lhs -> rhs."""
    return Rule(lhs, rhs, RuleType.IMMEDIATE, condition, priority)


def RuleDelayed(lhs: Any, rhs: Any, condition: Optional[Any] = None, priority: int = 0) -> Rule:
    """Create a delayed rule: lhs :> rhs."""
    return Rule(lhs, rhs, RuleType.DELAYED, condition, priority)


# Type checking

def is_rule(obj: Any) -> bool:
    """Check if object is a Rule."""
    return isinstance(obj, Rule)


def is_rule_immediate(obj: Any) -> bool:
    """Check if object is an immediate Rule."""
    return isinstance(obj, Rule) and obj.is_immediate()


def is_rule_delayed(obj: Any) -> bool:
    """Check if object is a delayed Rule."""
    return isinstance(obj, Rule) and obj.is_delayed()


def apply_rule(rule: Rule, expr: Any, context: Any = None) -> tuple[Any, bool]:
    """
    Try to apply a single rule to an expression.

    Returns:
        (result, success): result is the transformed expression or original,
                          success indicates if rule matched
    """
    # Try to match lhs against expression
    match_result = match(rule.lhs, expr)

    if not match_result:
        return expr, False

    # Check condition if present
    if rule.condition is not None:
        # Evaluate condition with bindings substituted
        from .evaluator import evaluate  # Avoid circular import
        cond_expr = replace_with_bindings(rule.condition, match_result.bindings)
        cond_result = evaluate(cond_expr, context)

        # Condition must evaluate to True (or truthy)
        if not cond_result:
            return expr, False

    # Apply replacement
    if rule.is_immediate():
        # Evaluate rhs immediately
        if callable(rule.rhs):
            result = rule.rhs(match_result.bindings)
        else:
            replaced = replace_with_bindings(rule.rhs, match_result.bindings)
            from .evaluator import evaluate  # Avoid circular import
            result = evaluate(replaced, context)
    else:
        # Delayed: substitute but don't evaluate yet
        if callable(rule.rhs):
            result = rule.rhs(match_result.bindings)
        else:
            result = replace_with_bindings(rule.rhs, match_result.bindings)

    return result, True


def try_rules(rules: list[Rule], expr: Any, context: Any = None) -> Any:
    """
    Try to apply rules in order until one succeeds.

    Rules are tried in priority order (highest first), then by list order.

    Returns:
        Transformed expression if a rule matched, otherwise original expression.
    """
    # Sort by priority (highest first), maintaining stable order for equal priorities
    sorted_rules = sorted(rules, key=lambda r: -r.priority)

    for rule in sorted_rules:
        result, success = apply_rule(rule, expr, context)
        if success:
            return result

    return expr


def apply_rules_repeatedly(rules: list[Rule], expr: Any, context: Any = None, 
                         max_iterations: int = 1000) -> Any:
    """
    Apply rules repeatedly until fixed point or max iterations.
    """
    for _ in range(max_iterations):
        new_expr = try_rules(rules, expr, context)
        if new_expr == expr:
            return expr  # Fixed point
        expr = new_expr

    return expr  # Max iterations reached
