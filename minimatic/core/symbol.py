"""
Symbol - Immutable symbolic identifiers.

Symbols are the atomic named elements of the language. They represent
variables, function names, constants, and attributes.

Implementation:
    Symbols are implemented as a tuple subclass for immutability and hashability.
    An interning cache ensures that symbols with the same name share identity.

Structure:
    Symbol = (name: str,)

    Note: Symbol attributes (like Protected, Locked) are stored externally
    in the evaluation Context, not on the Symbol itself. This keeps Symbols
    lightweight and allows attributes to change during evaluation.
"""

from typing import Dict
from threading import Lock
import itertools


class Symbol(tuple):
    """
    Immutable symbolic identifier.

    Symbols are interned: two symbols with the same name are the same object.
    This enables fast identity comparison and reduces memory usage.

    Structure: (name: str,)

    Examples:
        >>> x = Symbol("x")
        >>> y = Symbol("y")
        >>> x2 = Symbol("x")
        >>> x is x2  # Same object due to interning
        True
        >>> x == y
        False

    Attributes:
        name (str): The symbol's identifier string.

    Note:
        Use the `symbol()` factory function for convenient creation with
        automatic interning. Direct `Symbol()` calls also intern.
    """

    __slots__ = ()

    def __new__(cls, name: str) -> Symbol:
        """
        Create or retrieve an interned Symbol.

        Args:
            name: The symbol name. Must be a non-empty string.

        Returns:
            The interned Symbol instance.

        Raises:
            TypeError: If name is not a string
            ValueError: If name is empty.
        """
        if not isinstance(name, str):
            raise TypeError(f"Symbol name must be str, got {type(name).__name__}")
        if not name:
            raise ValueError("Symbol name cannot be empty")

        # Check cache first (fast path)
        cached = _symbol_cache.get(name)
        if cached is not None:
            return cached

        # Create new symbol (slow path with lock)
        with _cache_lock:
            # Double-check after acquiring lock
            cached = _symbol_cache.get(name)
            if cached is not None:
                return cached

            # Create and cache
            instance = super().__new__(cls, (name,))
            _symbol_cache[name] = instance
            return instance

    # Properties
    @property
    def name(self) -> str:
        """The symbol's name string."""
        return self[0]

    # String Representations
    def __repr__(self) -> str:
        """Unambiguous representation: Symbol("name")"""
        return f'Symbol("{self.name}")'

    def __str__(self) -> str:
        """Human-readable representation: just the name."""
        return self.name

    # Comparison & Hashing
    def __hash__(self) -> int:
        """Hash based on the symbol name."""
        return hash(("Symbol", self.name))

    def __eq__(self, other: object) -> bool:
        """
        Equality comparison.

        Due to interning, symbol equality can use identity comparison
        for other Symbols, falling back to name comparison otherwise.
        """
        if self is other:
            return True
        if isinstance(other, Symbol):
            return self.name == other.name
        return False

    def __lt__(self, other: object) -> bool:
        """Ordering for Orderless attribute (alphabetical by name)."""
        if isinstance(other, Symbol):
            return self.name < other.name
        return NotImplemented

    def __le__(self, other: object) -> bool:
        if isinstance(other, Symbol):
            return self.name <= other.name
        return NotImplemented

    def __gt__(self, other: object) -> bool:
        if isinstance(other, Symbol):
            return self.name > other.name
        return NotImplemented

    def __ge__(self, other: object) -> bool:
        if isinstance(other, Symbol):
            return self.name >= other.name
        return NotImplemented


# SYMBOL INTERNING CACHE
_symbol_cache: Dict[str, Symbol] = {}
_cache_lock = Lock()
_gensym_counter = itertools.count(1)


def clear_symbol_cache() -> None:
    """Clear the symbol interning cache. Primarily for testing."""
    global _symbol_cache, _gensym_counter
    with _cache_lock:
        _symbol_cache.clear()
        _gensym_counter = itertools.count(1)

# FACTORY FUNCTIONS

def symbol(name: str) -> Symbol:
    """
    Create or retrieve an interned Symbol.

    This is the preferred way to create symbols.

    Args:
        name: The symbol name.

    Returns:
        The interned Symbol instance.

    Examples:
        >>> x = symbol("x")
        >>> plus = symbol("Plus")
    """
    return Symbol(name)


def gensym(prefix: str = "G") -> Symbol:
    """
    Generate a unique symbol with an auto-incrementing suffix.

    Useful for creating temporary or internal symbols that won't
    conflict with user-defined names.

    Args:
        prefix: The prefix for the generated name (default: "G").

    Returns:
        A new unique Symbol.

    Examples:
        >>> gensym()
        Symbol("G1")
        >>> gensym()
        Symbol("G2")
        >>> gensym("tmp")
        Symbol("tmp3")
    """
    n = next(_gensym_counter)
    return Symbol(f"{prefix}{n}")

# TYPE PREDICATES

def is_symbol(obj: object) -> bool:
    """
    Check if an object is a Symbol.

    Args:
        obj: The object to check.

    Returns:
        True if obj is a Symbol, False otherwise.
    """
    return isinstance(obj, Symbol)


# MODULE INITIALIZATION

# Pre-intern commonly used system symbols
_SYSTEM_SYMBOLS = [
    "Symbol", "Integer", "Real", "Rational", "Complex", "String",
    "List", "Rule", "RuleDelayed", "Set", "SetDelayed",
    "Pattern", "Blank", "BlankSequence", "BlankNullSequence",
    "Condition", "Alternatives", "Sequence",
    "True", "False", "Null", "Nothing",
]

for _name in _SYSTEM_SYMBOLS:
    Symbol(_name)
