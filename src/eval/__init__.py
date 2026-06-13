"""
Evaluation engine

Provides expression evaluation, rule application, value storage,
and evaluation contexts following Wolfram Language semantics.
"""

from .evaluator import evaluate, try_evaluate, FixedPoint, evaluate_iterated
from .rules import (
    Rule, RuleDelayed,
    RuleType, is_rule, is_rule_delayed,
    try_rules, apply_rule
)
from .values import (
    ValueStore, Values,
    OwnValues, DownValues, UpValues,
    SubValues, NValues, DefaultValues, FormatValues,
    get_value, set_value, clear_value
)
from .context import (
    EvaluationContext, GlobalContext, ContextChain,
    get_current_context, with_context, context_stack
)
from .transforms import (
    flatten_sequences,
    apply_flat, apply_orderless,
    apply_listable,
    canonical_sort
)

__all__ = [
    # Evaluator
    "evaluate",
    "try_evaluate",
    "FixedPoint",
    "evaluate_iterated",

    # Rules
    "Rule",
    "RuleDelayed",
    "RuleType",
    "is_rule",
    "is_rule_delayed",
    "try_rules",
    "apply_rule",

    # Values
    "ValueStore",
    "Values",
    "OwnValues",
    "DownValues",
    "UpValues",
    "SubValues",
    "NValues",
    "DefaultValues",
    "FormatValues",
    "get_value",
    "set_value",
    "clear_value",

    # Context
    "EvaluationContext",
    "GlobalContext",
    "ContextChain",
    "get_current_context",
    "with_context",
    "context_stack",

    # Transforms
    "flatten_sequences",
    "apply_flat",
    "apply_orderless",
    "apply_listable",
    "canonical_sort",
]
