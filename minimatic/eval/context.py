"""
Evaluation context/environment management.

Provides symbol tables, attribute storage, and value storage
with support for nested scopes and context chaining.
"""

import threading
from collections.abc import Mapping
from typing import Any

from minimatic.core import Symbol


class EvaluationContext:
    """
    An evaluation context (namespace) containing:
    - Symbol table (symbol name -> Symbol object)
    - Attribute storage (Symbol -> frozenset of Attributes)
    - Value storage (all value types: OwnValues, DownValues, etc.)

    Contexts can be chained for nested scopes (local variables).
    """

    def __init__(self, name: str = "Global", parent: EvaluationContext | None = None):
        self.name = name
        self.parent = parent

        # Symbol name -> Symbol object mapping
        self._symbols: dict[str, Symbol] = {}

        # Symbol -> frozenset[Attribute]
        self._attributes: dict[Symbol, frozenset[Symbol]] = {}

        # Consolidated value storage: Symbol -> {type_key: value}
        self._values: dict[Symbol, dict[str, Any]] = {}

    def get_symbol(self, name: str) -> Symbol | None:
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

    def _get_value_list(self, sym: Symbol, key: str) -> list:
        """Get a value list for a symbol and key, checking parent contexts."""
        sym_vals = self._values.get(sym)
        if sym_vals is not None and key in sym_vals:
            return sym_vals[key]
        if self.parent is not None:
            return self.parent._get_value_list(sym, key)
        return []

    def _get_value_scalar(self, sym: Symbol, key: str) -> Any:
        """Get a scalar value for a symbol and key, checking parent contexts."""
        sym_vals = self._values.get(sym)
        if sym_vals is not None and key in sym_vals:
            return sym_vals[key]
        if self.parent is not None:
            return self.parent._get_value_scalar(sym, key)
        return None

    def _set_value(self, sym: Symbol, key: str, value: Any) -> None:
        """Set a value for a symbol and key."""
        if sym not in self._values:
            self._values[sym] = {}
        self._values[sym][key] = value

    def get_own_values(self, sym: Symbol) -> list:
        return self._get_value_list(sym, "own")

    def set_own_values(self, sym: Symbol, values: list) -> None:
        self._set_value(sym, "own", values)

    def get_down_values(self, sym: Symbol) -> list:
        return self._get_value_list(sym, "down")

    def set_down_values(self, sym: Symbol, values: list) -> None:
        self._set_value(sym, "down", values)

    def get_up_values(self, sym: Symbol) -> list:
        return self._get_value_list(sym, "up")

    def set_up_values(self, sym: Symbol, values: list) -> None:
        self._set_value(sym, "up", values)

    def get_sub_values(self, sym: Symbol) -> list:
        return self._get_value_list(sym, "sub")

    def set_sub_values(self, sym: Symbol, values: list) -> None:
        self._set_value(sym, "sub", values)

    def get_n_values(self, sym: Symbol) -> list:
        return self._get_value_list(sym, "n")

    def set_n_values(self, sym: Symbol, values: list) -> None:
        self._set_value(sym, "n", values)

    def get_default_value(self, sym: Symbol) -> Any:
        return self._get_value_scalar(sym, "default")

    def set_default_value(self, sym: Symbol, value: Any) -> None:
        self._set_value(sym, "default", value)

    def get_format_values(self, sym: Symbol) -> list:
        return self._get_value_list(sym, "format")

    def set_format_values(self, sym: Symbol, values: list) -> None:
        self._set_value(sym, "format", values)

    def clear_all_values(self, sym: Symbol) -> None:
        """Clear all values for a symbol."""
        if sym in self._values:
            del self._values[sym]

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
