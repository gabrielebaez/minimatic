"""
Evaluation engine

Provides expression evaluation, rule application, value storage,
and evaluation contexts following Wolfram Language semantics.
"""

from .context import (
    ContextChain,
    EvaluationContext,
    GlobalContext,
    context_stack,
    get_current_context,
    with_context,
)
from .evaluator import FixedPoint, evaluate, evaluate_iterated, try_evaluate
from .rules import Rule, RuleDelayed, RuleType, apply_rule, is_rule, is_rule_delayed, try_rules
from .transforms import (
    apply_flat,
    apply_listable,
    apply_orderless,
    canonical_sort,
    flatten_sequences,
)
from .values import (
    DefaultValues,
    DownValues,
    FormatValues,
    NValues,
    OwnValues,
    SubValues,
    UpValues,
    Values,
    ValueStore,
    clear_value,
    get_value,
    set_value,
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
