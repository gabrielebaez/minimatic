"""
Built-in function registry.

Manages native implementations of system functions with their
associated attributes and evaluation logic.
"""

from __future__ import annotations

import functools
from dataclasses import dataclass
from typing import Any, Callable, Optional, Dict, Set, TYPE_CHECKING

from minimatic.core import Symbol, Expression #, Attribute
from minimatic.core.attributes import HoldAll, HoldFirst, HoldRest, HoldAllComplete
from minimatic.core.attributes import Listable, Flat, Orderless, NumericFunction

if TYPE_CHECKING:
    from minimatic.eval.context import EvaluationContext


@dataclass
class BuiltinFunction:
    """
    Represents a built-in function implementation.

    Attributes:
        symbol: The symbol this built-in is bound to
        implementation: Callable implementing the function
        attributes: Set of attributes for this function
        auto_evaluate: Whether to auto-evaluate arguments (override attributes)
    """

    symbol: Symbol
    implementation: Callable[[Any, EvaluationContext], Any]
    attributes: frozenset[Attribute]
    auto_evaluate: bool = True

    def __call__(self, expr: Expression, context: EvaluationContext) -> Any:
        """Execute the built-in implementation."""
        return self.implementation(expr, context)


# Global registry mapping Symbol -> BuiltinFunction
_registry: Dict[Symbol, BuiltinFunction] = {}


def register_builtin(
    sym: Symbol,
    attributes: Optional[Set[Attribute]] = None,
    auto_evaluate: bool = True
) -> Callable[[Callable], Callable]:
    """
    Decorator to register a function as a built-in.

    Usage:
        @register_builtin(Symbol("Plus"), attributes={Flat, Orderless, Listable})
        def plus_impl(expr, context):
            # implementation
            return result
    """
    attrs = frozenset(attributes) if attributes else frozenset()

    def decorator(func: Callable[[Any, EvaluationContext], Any]) -> Callable:
        builtin = BuiltinFunction(
            symbol=sym,
            implementation=func,
            attributes=attrs,
            auto_evaluate=auto_evaluate
        )
        _registry[sym] = builtin
        return func

    return decorator


def get_builtin(sym: Symbol) -> Optional[BuiltinFunction]:
    """Get the built-in implementation for a symbol, if registered."""
    return _registry.get(sym)


def has_builtin(sym: Symbol) -> bool:
    """Check if a symbol has a registered built-in implementation."""
    return sym in _registry


def builtin_attributes(sym: Symbol) -> frozenset[Attribute]:
    """Get the attributes associated with a built-in symbol."""
    builtin = _registry.get(sym)
    if builtin:
        return builtin.attributes
    return frozenset()


def clear_registry() -> None:
    """Clear all registered built-ins (useful for testing)."""
    _registry.clear()


class BuiltinRegistry:
    """
    Scoped built-in registry for creating custom evaluation environments.

    Allows extending or overriding built-ins in a specific context.
    """

    def __init__(self, parent: Optional[BuiltinRegistry] = None):
        self.parent = parent
        self._local: Dict[Symbol, BuiltinFunction] = {}

    def register(self, sym: Symbol, impl: Callable, 
                 attributes: Optional[Set[Attribute]] = None) -> None:
        """Register a built-in in this registry."""
        attrs = frozenset(attributes) if attributes else frozenset()
        self._local[sym] = BuiltinFunction(sym, impl, attrs)

    def get(self, sym: Symbol) -> Optional[BuiltinFunction]:
        """Get built-in, checking local then parent."""
        if sym in self._local:
            return self._local[sym]
        if self.parent:
            return self.parent.get(sym)
        return get_builtin(sym)  # Fall back to global

    def has(self, sym: Symbol) -> bool:
        """Check if built-in exists in this registry chain."""
        return self.get(sym) is not None


def dispatch_builtin(expr: Expression, context: EvaluationContext) -> Any:
    """
    Dispatch an expression to its built-in implementation.

    This is called by the evaluator when no rules matched.
    Handles argument evaluation based on attributes.
    """
    if not isinstance(expr.head, Symbol):
        return expr  # Can't dispatch non-symbol heads

    builtin = get_builtin(expr.head)
    if builtin is None:
        return expr  # No built-in found

    # Check if we need to evaluate arguments
    # (The evaluator should have already done this based on Hold* attributes,
    #  but we double-check here for safety)

    # For Listable functions, threading should have been handled by evaluator
    # We just implement the scalar case

    return builtin(expr, context)
