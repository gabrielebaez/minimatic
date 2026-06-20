"""
Built-in function implementations for Minimatic.

Provides native implementations of core Wolfram Language functions
including arithmetic, list manipulation, and system functions.
"""

from .arithmetic import (
    Abs,
    Divide,
    Exp,
    Log,
    Minus,
    Plus,
    Power,
    Product,
    Sqrt,
    Subtract,
    Sum,
    Times,
)
from .registry import (
    BuiltinFunction,
    BuiltinRegistry,
    builtin_attributes,
    clear_registry,
    get_builtin,
    has_builtin,
    register_builtin,
)
from .io import Request

__all__ = [
    # Registry
    "register_builtin",
    "get_builtin",
    "has_builtin",
    "builtin_attributes",
    "BuiltinFunction",
    "BuiltinRegistry",
    "clear_registry",
    # Arithmetic (exported for direct access)
    "Plus",
    "Times",
    "Power",
    "Minus",
    "Divide",
    "Subtract",
    "Abs",
    "Sqrt",
    "Exp",
    "Log",
    "Sum",
    "Product",
    # Web
    "Request",
]
