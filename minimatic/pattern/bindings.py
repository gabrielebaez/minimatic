"""
Bindings - Match result management.

This module provides the Bindings class for managing pattern match results.
Bindings map pattern variable names (Symbols) to matched values.

Key Properties:
    - Immutable: All operations return new Bindings objects
    - Hashable: Can be used in sets or as dict keys
    - Conflict Detection: Detects when same name matches different values

Usage:
    # Create bindings
    b = empty_bindings()
    b = single_binding(x, 42)

    # Extend bindings
    b2 = b.bind(y, 3.14)

    # Merge bindings
    b3 = merge_bindings(b1, b2)

    # Access values
    value = b[x]
    value = b.get(x, default)
"""

from __future__ import annotations
from typing import (
    Dict, 
    Optional, 
    Iterator, 
    Mapping, 
    Any,
    Union,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from core.atoms import Element

from minimatic.core.symbol import Symbol


# ═══════════════════════════════════════════════════════════════════════════════
# BINDINGS CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class Bindings(Mapping[Symbol, "Element"]):
    """
    Immutable mapping from pattern variable names to matched values.

    Bindings represent the result of a successful pattern match. They
    map Symbol names (from Pattern[name, _] constructs) to the actual
    expressions that matched.

    Bindings are immutable — all modification operations return new
    Bindings objects. This enables safe backtracking during matching.

    Examples:
        >>> x, y = Symbol("x"), Symbol("y")
        >>> b = Bindings({x: 42, y: "hello"})
        >>> b[x]
        42
        >>> x in b
        True
        >>> len(b)
        2
        >>> b2 = b.bind(Symbol("z"), 3.14)  # Returns new Bindings
        >>> len(b)  # Original unchanged
        2

    Attributes:
        _data: Internal immutable mapping (frozenset of tuples).
    """

    __slots__ = ('_data', '_hash')

    def __init__(
        self, 
        data: Optional[Union[Dict[Symbol, "Element"], "Bindings"]] = None
    ) -> None:
        """
        Create a Bindings object.

        Args:
            data: Initial bindings as a dict or another Bindings object.
                  If None, creates empty bindings.

        Raises:
            TypeError: If keys are not Symbols.
        """
        if data is None:
            self._data: Dict[Symbol, "Element"] = {}
        elif isinstance(data, Bindings):
            self._data = dict(data._data)
        elif isinstance(data, dict):
            # Validate keys are Symbols
            for key in data:
                if not isinstance(key, Symbol):
                    raise TypeError(
                        f"Bindings keys must be Symbols, got {type(key).__name__}"
                    )
            self._data = dict(data)
        else:
            raise TypeError(
                f"Bindings data must be dict or Bindings, got {type(data).__name__}"
            )

        # Cache hash (computed lazily)
        self._hash: Optional[int] = None

    # ─────────────────────────────────────────────────────────────────────────
    # Mapping Protocol
    # ─────────────────────────────────────────────────────────────────────────

    def __getitem__(self, key: Symbol) -> "Element":
        """Get the value bound to a symbol."""
        return self._data[key]

    def __len__(self) -> int:
        """Number of bindings."""
        return len(self._data)

    def __iter__(self) -> Iterator[Symbol]:
        """Iterate over bound symbols."""
        return iter(self._data)

    def __contains__(self, key: object) -> bool:
        """Check if a symbol is bound."""
        return key in self._data

    def get(self, key: Symbol, default: Any = None) -> Any:
        """Get value with optional default."""
        return self._data.get(key, default)

    def keys(self):
        """View of bound symbols."""
        return self._data.keys()

    def values(self):
        """View of bound values."""
        return self._data.values()

    def items(self):
        """View of (symbol, value) pairs."""
        return self._data.items()

    # ─────────────────────────────────────────────────────────────────────────
    # Immutable Modification Operations
    # ─────────────────────────────────────────────────────────────────────────

    def bind(self, name: Symbol, value: "Element") -> "Bindings":
        """
        Create new Bindings with an additional binding.

        If the name is already bound to the same value, returns self.
        If bound to a different value, raises BindingConflict.

        Args:
            name: The symbol to bind.
            value: The value to bind to.

        Returns:
            New Bindings with the additional binding.

        Raises:
            BindingConflict: If name is bound to a different value.
        """
        if not isinstance(name, Symbol):
            raise TypeError(f"Binding name must be Symbol, got {type(name).__name__}")

        if name in self._data:
            existing = self._data[name]
            if existing == value:
                return self  # Same binding, no change needed
            raise BindingConflict(name, existing, value)

        new_data = dict(self._data)
        new_data[name] = value
        return Bindings(new_data)

    def bind_all(self, bindings: Mapping[Symbol, "Element"]) -> "Bindings":
        """
        Create new Bindings with multiple additional bindings.

        Args:
            bindings: Mapping of symbols to values to add.

        Returns:
            New Bindings with all additional bindings.

        Raises:
            BindingConflict: If any name conflicts with existing binding.
        """
        result = self
        for name, value in bindings.items():
            result = result.bind(name, value)
        return result

    def unbind(self, name: Symbol) -> "Bindings":
        """
        Create new Bindings without a specific binding.

        Args:
            name: The symbol to remove.

        Returns:
            New Bindings without the specified binding.
        """
        if name not in self._data:
            return self

        new_data = dict(self._data)
        del new_data[name]
        return Bindings(new_data)

    def merge(self, other: "Bindings") -> "Bindings":
        """
        Merge with another Bindings object.

        Args:
            other: Another Bindings to merge with.

        Returns:
            New Bindings containing all bindings from both.

        Raises:
            BindingConflict: If the same name is bound to different values.
        """
        if not other:
            return self
        if not self:
            return other

        return self.bind_all(other)

    # ─────────────────────────────────────────────────────────────────────────
    # Comparison & Hashing
    # ─────────────────────────────────────────────────────────────────────────

    def __eq__(self, other: object) -> bool:
        """Check equality with another Bindings."""
        if self is other:
            return True
        if not isinstance(other, Bindings):
            return False
        return self._data == other._data

    def __hash__(self) -> int:
        """Hash for use in sets/dicts."""
        if self._hash is None:
            # Create hashable representation
            self._hash = hash(frozenset(
                (k, self._make_hashable(v)) 
                for k, v in self._data.items()
            ))
        return self._hash

    @staticmethod
    def _make_hashable(value: Any) -> Any:
        """Make a value hashable for hashing purposes."""
        try:
            hash(value)
            return value
        except TypeError:
            # For unhashable types, use id as fallback
            return ("__unhashable__", id(value))

    # ─────────────────────────────────────────────────────────────────────────
    # String Representations
    # ─────────────────────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        """Detailed representation."""
        if not self._data:
            return "Bindings({})"

        items = ", ".join(
            f"{k}: {v!r}" for k, v in sorted(self._data.items(), key=lambda x: str(x[0]))
        )
        return f"Bindings({{{items}}})"

    def __str__(self) -> str:
        """Human-readable representation."""
        if not self._data:
            return "{}"

        items = ", ".join(
            f"{k} → {v}" for k, v in sorted(self._data.items(), key=lambda x: str(x[0]))
        )
        return f"{{{items}}}"

    # ─────────────────────────────────────────────────────────────────────────
    # Boolean
    # ─────────────────────────────────────────────────────────────────────────

    def __bool__(self) -> bool:
        """True if bindings is non-empty."""
        return bool(self._data)

    # ─────────────────────────────────────────────────────────────────────────
    # Utility Methods
    # ─────────────────────────────────────────────────────────────────────────

    def to_dict(self) -> Dict[Symbol, "Element"]:
        """Convert to a regular dictionary (copy)."""
        return dict(self._data)

    def is_compatible_with(self, other: "Bindings") -> bool:
        """
        Check if this bindings can be merged with another without conflict.

        Args:
            other: Another Bindings to check compatibility with.

        Returns:
            True if merge would succeed without BindingConflict.
        """
        for name, value in other.items():
            if name in self._data and self._data[name] != value:
                return False
        return True


# ═══════════════════════════════════════════════════════════════════════════════
# BINDING CONFLICT EXCEPTION
# ═══════════════════════════════════════════════════════════════════════════════

class BindingConflict(Exception):
    """
    Exception raised when attempting to bind a name to conflicting values.

    Attributes:
        name: The symbol with conflicting bindings.
        existing: The previously bound value.
        new: The new value that conflicts.
    """

    def __init__(self, name: Symbol, existing: Any, new: Any) -> None:
        self.name = name
        self.existing = existing
        self.new = new
        super().__init__(
            f"Cannot bind {name} to {new!r}: already bound to {existing!r}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# FACTORY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

# Cached empty bindings singleton
_EMPTY_BINDINGS: Optional[Bindings] = None


def empty_bindings() -> Bindings:
    """
    Get an empty Bindings object.

    Returns a cached singleton for efficiency.

    Returns:
        Empty Bindings object.
    """
    global _EMPTY_BINDINGS
    if _EMPTY_BINDINGS is None:
        _EMPTY_BINDINGS = Bindings()
    return _EMPTY_BINDINGS


def single_binding(name: Symbol, value: "Element") -> Bindings:
    """
    Create Bindings with a single binding.

    Args:
        name: The symbol to bind.
        value: The value to bind to.

    Returns:
        Bindings with just the one binding.
    """
    return Bindings({name: value})


# ═══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def merge_bindings(b1: Bindings, b2: Bindings) -> Bindings:
    """
    Merge two Bindings objects.

    Functional interface to Bindings.merge().

    Args:
        b1: First bindings.
        b2: Second bindings.

    Returns:
        Merged bindings containing all bindings from both.

    Raises:
        BindingConflict: If same name bound to different values.
    """
    return b1.merge(b2)


def bindings_compatible(b1: Bindings, b2: Bindings) -> bool:
    """
    Check if two Bindings can be merged without conflict.

    Args:
        b1: First bindings.
        b2: Second bindings.

    Returns:
        True if merge would succeed.
    """
    return b1.is_compatible_with(b2)


def bindings_from_pairs(*pairs: tuple[Symbol, "Element"]) -> Bindings:
    """
    Create Bindings from (symbol, value) pairs.

    Args:
        *pairs: (Symbol, value) tuples.

    Returns:
        Bindings with all the given bindings.

    Examples:
        >>> x, y = Symbol("x"), Symbol("y")
        >>> bindings_from_pairs((x, 1), (y, 2))
        Bindings({x: 1, y: 2})
    """
    return Bindings(dict(pairs))
