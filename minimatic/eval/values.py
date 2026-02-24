"""
Value types management: OwnValues, DownValues, UpValues, SubValues,
NValues, DefaultValues, and FormatValues.

Implements the Wolfram Language value storage hierarchy.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Union

from minimatic.core import Symbol, Expression
from minimatic.pattern import Bindings, pattern


# Type aliases for value entries
ValueEntry = tuple  # (pattern, replacement, condition=None)


@dataclass(frozen=True)
class Values:
    """
    Container for all value types associated with a symbol.

    Mirrors Wolfram Language's value system:
    - OwnValues: f -> value (symbol replacement)
    - DownValues: f[args] -> value (function definition)
    - UpValues: expr f -> value (operator overloading)
    - SubValues: f[args1][args2] -> value (subscripted functions)
    - NValues: N[f[args]] -> value (numeric approximation)
    - DefaultValues: Default[f] -> value (pattern defaults)
    - FormatValues: Format[f[args]] -> value (output formatting)
    """

    own: list[ValueEntry] = None
    down: list[ValueEntry] = None
    up: list[ValueEntry] = None
    sub: list[ValueEntry] = None
    n: list[ValueEntry] = None
    default: Any = None
    format: list[ValueEntry] = None

    def __post_init__(self):
        # Initialize mutable defaults safely
        object.__setattr__(self, "own", self.own or [])
        object.__setattr__(self, "down", self.down or [])
        object.__setattr__(self, "up", self.up or [])
        object.__setattr__(self, "sub", self.sub or [])
        object.__setattr__(self, "n", self.n or [])
        object.__setattr__(self, "format", self.format or [])


class ValueStore:
    """
    Global value store mapping symbols to their Values.

    This is typically accessed through EvaluationContext,
    but this class provides the core storage mechanism.
    """

    def __init__(self):
        self._store: dict[Symbol, Values] = {}

    def get_values(self, sym: Symbol) -> Values:
        """Get or create Values container for a symbol."""
        if sym not in self._store:
            self._store[sym] = Values()
        return self._store[sym]

    def clear_symbol(self, sym: Symbol) -> None:
        """Remove all values for a symbol."""
        if sym in self._store:
            del self._store[sym]

    def add_own_value(self, sym: Symbol, pattern_expr: Any, replacement: Any, 
                      condition: Optional[Any] = None) -> None:
        """Add an OwnValue: sym -> replacement when pattern matches."""
        values = self.get_values(sym)
        values.own.append((pattern_expr, replacement, condition))

    def add_down_value(self, sym: Symbol, pattern_expr: Expression, replacement: Any,
                       condition: Optional[Any] = None) -> None:
        """Add a DownValue: sym[args] -> replacement."""
        values = self.get_values(sym)
        values.down.append((pattern_expr, replacement, condition))

    def add_up_value(self, sym: Symbol, pattern_expr: Expression, replacement: Any,
                     condition: Optional[Any] = None) -> None:
        """Add an UpValue: pattern containing sym -> replacement."""
        values = self.get_values(sym)
        values.up.append((pattern_expr, replacement, condition))

    def add_sub_value(self, sym: Symbol, pattern_expr: Expression, replacement: Any,
                      condition: Optional[Any] = None) -> None:
        """Add a SubValue: sym[args1][args2] -> replacement."""
        values = self.get_values(sym)
        values.sub.append((pattern_expr, replacement, condition))

    def add_n_value(self, sym: Symbol, pattern_expr: Expression, replacement: Any,
                    condition: Optional[Any] = None) -> None:
        """Add an NValue: N[sym[args]] -> replacement."""
        values = self.get_values(sym)
        values.n.append((pattern_expr, replacement, condition))

    def set_default_value(self, sym: Symbol, value: Any) -> None:
        """Set DefaultValue for a symbol."""
        values = self.get_values(sym)
        values.default = value

    def add_format_value(self, sym: Symbol, pattern_expr: Expression, replacement: Any,
                         condition: Optional[Any] = None) -> None:
        """Add a FormatValue: sym[args] -> format_spec."""
        values = self.get_values(sym)
        values.format.append((pattern_expr, replacement, condition))


# Convenience functions for context-based value access

def get_value(ctx, sym: Symbol, value_type: str) -> list:
    """
    Get values of a specific type from context.

    value_type: one of 'own', 'down', 'up', 'sub', 'n', 'default', 'format'
    """
    if value_type == "own":
        return ctx.get_own_values(sym)
    elif value_type == "down":
        return ctx.get_down_values(sym)
    elif value_type == "up":
        return ctx.get_up_values(sym)
    elif value_type == "sub":
        return ctx.get_sub_values(sym)
    elif value_type == "n":
        return ctx.get_n_values(sym)
    elif value_type == "default":
        return ctx.get_default_value(sym)
    elif value_type == "format":
        return ctx.get_format_values(sym)
    else:
        raise ValueError(f"Unknown value type: {value_type}")


def set_value(ctx, sym: Symbol, value_type: str, values: Any) -> None:
    """Set values of a specific type in context."""
    if value_type == "own":
        ctx.set_own_values(sym, values)
    elif value_type == "down":
        ctx.set_down_values(sym, values)
    elif value_type == "up":
        ctx.set_up_values(sym, values)
    elif value_type == "sub":
        ctx.set_sub_values(sym, values)
    elif value_type == "n":
        ctx.set_n_values(sym, values)
    elif value_type == "default":
        ctx.set_default_value(sym, values)
    elif value_type == "format":
        ctx.set_format_values(sym, values)
    else:
        raise ValueError(f"Unknown value type: {value_type}")


def clear_value(ctx, sym: Symbol, value_type: Optional[str] = None) -> None:
    """Clear values. If value_type is None, clear all."""
    if value_type is None:
        ctx.clear_all_values(sym)
    else:
        set_value(ctx, sym, value_type, [] if value_type != "default" else None)


# Type constants for dispatch
OwnValues = "own"
DownValues = "down"
UpValues = "up"
SubValues = "sub"
NValues = "n"
DefaultValues = "default"
FormatValues = "format"

ALL_VALUE_TYPES = [OwnValues, DownValues, UpValues, SubValues, NValues, DefaultValues, FormatValues]
