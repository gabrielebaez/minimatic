"""
Built-in function implementations for Minimatic.

Provides native implementations of core Wolfram Language functions
including arithmetic, list manipulation, and system functions.
"""

from .registry import (
    register_builtin,
    get_builtin,
    has_builtin,
    builtin_attributes,
    BuiltinFunction,
    BuiltinRegistry,
    clear_registry
)

from .arithmetic import (
    Plus,
    Times,
    Power,
    Minus,
    Divide,
    Subtract,
    Abs,
    Sqrt,
    Exp,
    Log,
    Sum,
    Product
)

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
]
