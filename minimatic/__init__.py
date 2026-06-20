"""
Minimatic - A minimal Wolfram Language-style symbolic computation engine.

Usage:
    from minimatic import Symbol, Expression, evaluate, GlobalContext
    from minimatic import Plus, Times, Power, Request

    ctx = GlobalContext
    Plus = Symbol("Plus")
    evaluate(Expression(Plus, 1, 2, 3), ctx)  # 6
"""

from .core import (
    Expression,
    Symbol,
    gensym,
    is_expr,
    is_symbol,
    symbol,
)
from .eval import (
    EvaluationContext,
    GlobalContext,
    evaluate,
    try_evaluate,
)

__all__ = [
    # Core
    "Symbol",
    "Expression",
    "symbol",
    "gensym",
    "is_symbol",
    "is_expr",
    # Eval
    "evaluate",
    "try_evaluate",
    "EvaluationContext",
    "GlobalContext",
]
