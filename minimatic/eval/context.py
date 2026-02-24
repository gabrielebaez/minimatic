"""
Evaluation context/environment management.

Provides symbol tables, attribute storage, and value storage
with support for nested scopes and context chaining.
"""

from __future__ import annotations

import threading
from collections.abc import Mapping
from typing import Any, Optional

from minimatic.core import Symbol, Expression #, Attritube
# from minimatic.core.attributes import get_attributes as get_base_attributes


class EvaluationContext:
    """
    An evaluation context (namespace) containing:
    - Symbol table (symbol name -> Symbol object)
    - Attribute storage (Symbol -> frozenset of Attributes)
    - Value storage (all value types: OwnValues, DownValues, etc.)

    Contexts can be chained for nested scopes (local variables).
    """

    def __init__(self, name: str = "Global", parent: Optional[EvaluationContext] = None):
        self.name = name
        self.parent = parent

        # Symbol name -> Symbol object mapping
        self._symbols: dict[str, Symbol] = {}

        # Symbol -> frozenset[Attribute]
        self._attributes: dict[Symbol, frozenset[Symbol]] = {}

        # Value storage by type
        self._own_values: dict[Symbol, list] = {}
        self._down_values: dict[Symbol, list] = {}
        self._up_values: dict[Symbol, list] = {}
        self._sub_values: dict[Symbol, list] = {}
        self._n_values: dict[Symbol, list] = {}
        self._default_values: dict[Symbol, Any] = {}
        self._format_values: dict[Symbol, list] = {}

    def get_symbol(self, name: str) -> Optional[Symbol]:
        """Get symbol by name, checking parent contexts if not found."""
        if name in self._symbols:
            return self._symbols[name]
        if self.parent is not None:
            return self.parent.get_symbol(name)
        return None

    def intern_symbol(self, name: str, sym: Symbol) -> Symbol:
        """Intern a symbol in this context."""
        self._symbols[name] = sym
        return sym

    def get_attributes(self, sym: Symbol) -> frozenset[Symbol]:
        """Get attributes for a symbol."""
        if sym in self._attributes:
            return self._attributes[sym]
        if self.parent is not None:
            return self.parent.get_attributes(sym)
        return frozenset()

    def set_attributes(self, sym: Symbol, attrs: frozenset[Symbol]) -> None:
        """Set attributes for a symbol."""
        self._attributes[sym] = frozenset(attrs)

    def clear_attributes(self, sym: Symbol) -> None:
        """Clear all attributes for a symbol."""
        if sym in self._attributes:
            del self._attributes[sym]

    def has_attribute(self, sym: Symbol, attr: Symbol) -> bool:
        """Check if symbol has a specific attribute."""
        return attr in self.get_attributes(sym)

    # Value storage accessors

    def get_own_values(self, sym: Symbol) -> list:
        return self._own_values.get(sym, [])

    def set_own_values(self, sym: Symbol, values: list) -> None:
        self._own_values[sym] = values

    def get_down_values(self, sym: Symbol) -> list:
        return self._down_values.get(sym, [])

    def set_down_values(self, sym: Symbol, values: list) -> None:
        self._down_values[sym] = values

    def get_up_values(self, sym: Symbol) -> list:
        return self._up_values.get(sym, [])

    def set_up_values(self, sym: Symbol, values: list) -> None:
        self._up_values[sym] = values

    def get_sub_values(self, sym: Symbol) -> list:
        return self._sub_values.get(sym, [])

    def set_sub_values(self, sym: Symbol, values: list) -> None:
        self._sub_values[sym] = values

    def get_n_values(self, sym: Symbol) -> list:
        return self._n_values.get(sym, [])

    def set_n_values(self, sym: Symbol, values: list) -> None:
        self._n_values[sym] = values

    def get_default_value(self, sym: Symbol) -> Any:
        return self._default_values.get(sym, None)

    def set_default_value(self, sym: Symbol, value: Any) -> None:
        self._default_values[sym] = value

    def get_format_values(self, sym: Symbol) -> list:
        return self._format_values.get(sym, [])

    def set_format_values(self, sym: Symbol, values: list) -> None:
        self._format_values[sym] = values

    def clear_all_values(self, sym: Symbol) -> None:
        """Clear all values for a symbol."""
        for store in [self._own_values, self._down_values, self._up_values,
                      self._sub_values, self._n_values, self._default_values,
                      self._format_values]:
            if sym in store:
                del store[sym]

    def __repr__(self) -> str:
        return f"EvaluationContext({self.name!r})"


# Global context singleton
GlobalContext = EvaluationContext("Global")


# Thread-local storage for current context stack
_thread_local = threading.local()


def context_stack() -> list[EvaluationContext]:
    """Get the current thread's context stack."""
    if not hasattr(_thread_local, "stack"):
        _thread_local.stack = [GlobalContext]
    return _thread_local.stack


def get_current_context() -> EvaluationContext:
    """Get the innermost active evaluation context."""
    return context_stack()[-1]


class with_context:
    """
    Context manager for temporary context scoping.

    Usage:
        with with_context(EvaluationContext("Local")):
            result = evaluate(expr)
    """

    def __init__(self, ctx: EvaluationContext):
        self.ctx = ctx
        self.stack = context_stack()

    def __enter__(self):
        self.stack.append(self.ctx)
        return self.ctx

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stack.pop()
        return False


class ContextChain(Mapping):
    """
    A chained view of multiple evaluation contexts.
    Reads traverse the chain; writes go to the first context.
    """

    def __init__(self, *contexts: EvaluationContext):
        self.contexts = list(contexts)

    def __getitem__(self, key: Symbol) -> Any:
        for ctx in self.contexts:
            result = ctx.get_symbol(key.name if isinstance(key, Symbol) else key)
            if result is not None:
                return result
        raise KeyError(key)

    def __iter__(self):
        seen = set()
        for ctx in self.contexts:
            for sym in ctx._symbols.values():
                if sym not in seen:
                    seen.add(sym)
                    yield sym

    def __len__(self):
        return len(set(self.__iter__()))
