"""
Bindings - Match result management.

This module provides the Bindings class for managing pattern match results.
Bindings map pattern variable names (Symbols) to matched values.

Key Properties:
    - Immutable: Backed by frozenset, all operations return new Bindings
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

# from __future__ import annotations
from collections.abc import Iterator, Mapping
from typing import (
    TYPE_CHECKING,
    Any,
)

if TYPE_CHECKING:
    from src.core.atoms import Element

from src.core.symbol import Symbol

# ═══════════════════════════════════════════════════════════════════════════════
# BINDINGS CLASS
# ═══════════════════════════════════════════════════════════════════════════════


class Bindings(Mapping[Symbol, "Element"]):
    """
    Immutable mapping from pattern variable names to matched values.

    Bindings represent the result of a successful pattern match. They
    map Symbol names (from Pattern[name, _] constructs) to the actual
    expressions that matched.

    Backed by a frozenset of (key, value) pairs for true immutability.
    All modification operations return new Bindings objects, enabling
    safe backtracking during matching.

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
        _pairs: Frozen set of (Symbol, Element) tuples.
        _index: Dict for O(1) lookup (derived from _pairs).
    """

    __slots__ = ("_pairs", "_index", "_hash")

    def __init__(
        self,
        data: dict[Symbol, Element] | Bindings | None = None,
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
            self._pairs: frozenset[tuple[Symbol, Element]] = frozenset()
            self._index: dict[Symbol, Element] = {}
        elif isinstance(data, Bindings):
            self._pairs = data._pairs
            self._index = dict(data._index)
        elif isinstance(data, dict):
            for key in data:
                if not isinstance(key, Symbol):
                    raise TypeError(f"Bindings keys must be Symbols, got {type(key).__name__}")
            self._pairs = frozenset(data.items())
            self._index = dict(data)
        else:
            raise TypeError(f"Bindings data must be dict or Bindings, got {type(data).__name__}")
        self._hash: int | None = None

    @classmethod
    def _from_parts(cls, pairs: frozenset[tuple[Symbol, Element]]) -> Bindings:
        """Construct directly from frozenset (internal use)."""
        obj = object.__new__(cls)
        obj._pairs = pairs
        obj._index = dict(pairs)
        obj._hash = None
        return obj

    # ─────────────────────────────────────────────────────────────────────────
    # Mapping Protocol
    # ─────────────────────────────────────────────────────────────────────────

    def __getitem__(self, key: Symbol) -> Element:
        """Get the value bound to a symbol."""
        return self._index[key]

    def __len__(self) -> int:
        """Number of bindings."""
        return len(self._pairs)

    def __iter__(self) -> Iterator[Symbol]:
        """Iterate over bound symbols."""
        return iter(self._index)

    def __contains__(self, key: object) -> bool:
        """Check if a symbol is bound."""
        return key in self._index

    def get(self, key: Symbol, default: Any = None) -> Any:
        """Get value with optional default."""
        return self._index.get(key, default)

    def keys(self):
        """View of bound symbols."""
        return self._index.keys()

    def values(self):
        """View of bound values."""
        return self._index.values()

    def items(self):
        """View of (symbol, value) pairs."""
        return self._index.items()

    # ─────────────────────────────────────────────────────────────────────────
    # Immutable Modification Operations
    # ─────────────────────────────────────────────────────────────────────────

    def bind(self, name: Symbol, value: Element) -> Bindings:
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

        if name in self._index:
            existing = self._index[name]
            if existing == value:
                return self
            raise BindingConflict(name, existing, value)

        return Bindings._from_parts(self._pairs | frozenset({(name, value)}))

    def bind_all(self, bindings: Mapping[Symbol, Element]) -> Bindings:
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

    def unbind(self, name: Symbol) -> Bindings:
        """
        Create new Bindings without a specific binding.

        Args:
            name: The symbol to remove.

        Returns:
            New Bindings without the specified binding.
        """
        if name not in self._index:
            return self

        new_pairs = frozenset((k, v) for k, v in self._pairs if k != name)
        return Bindings._from_parts(new_pairs)

    def merge(self, other: Bindings) -> Bindings:
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
        return self._pairs == other._pairs

    def __hash__(self) -> int:
        """Hash for use in sets/dicts."""
        if self._hash is None:
            self._hash = hash(self._pairs)
        return self._hash

    # ─────────────────────────────────────────────────────────────────────────
    # String Representations
    # ─────────────────────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        """Detailed representation."""
        if not self._pairs:
            return "Bindings({})"
        items = ", ".join(f"{k}: {v!r}" for k, v in sorted(self._pairs, key=lambda p: str(p[0])))
        return f"Bindings({{{items}}})"

    def __str__(self) -> str:
        """Human-readable representation."""
        if not self._pairs:
            return "{}"
        items = ", ".join(f"{k} → {v}" for k, v in sorted(self._pairs, key=lambda p: str(p[0])))
        return f"{{{items}}}"

    # ─────────────────────────────────────────────────────────────────────────
    # Boolean
    # ─────────────────────────────────────────────────────────────────────────

    def __bool__(self) -> bool:
        """True if bindings is non-empty."""
        return bool(self._pairs)

    # ─────────────────────────────────────────────────────────────────────────
    # Utility Methods
    # ─────────────────────────────────────────────────────────────────────────

    def to_dict(self) -> dict[Symbol, Element]:
        """Convert to a regular dictionary (copy)."""
        return dict(self._index)

    def is_compatible_with(self, other: Bindings) -> bool:
        """
        Check if this bindings can be merged with another without conflict.

        Args:
            other: Another Bindings to check compatibility with.

        Returns:
            True if merge would succeed without BindingConflict.
        """
        for name, value in other.items():
            if name in self._index and self._index[name] != value:
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
        super().__init__(f"Cannot bind {name} to {new!r}: already bound to {existing!r}")


# ═══════════════════════════════════════════════════════════════════════════════
# FACTORY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

_EMPTY_BINDINGS: Bindings | None = None


def empty_bindings() -> Bindings:
    """
    Get an empty Bindings object.
    Returns a cached singleton for efficiency.
    """
    global _EMPTY_BINDINGS
    if _EMPTY_BINDINGS is None:
        _EMPTY_BINDINGS = Bindings()
    return _EMPTY_BINDINGS


def single_binding(name: Symbol, value: Element) -> Bindings:
    """
    Create Bindings with a single binding.
    """
    return Bindings({name: value})


# ═══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════


def merge_bindings(b1: Bindings, b2: Bindings) -> Bindings:
    """
    Merge two Bindings objects.
    """
    return b1.merge(b2)


def bindings_compatible(b1: Bindings, b2: Bindings) -> bool:
    """
    Check if two Bindings can be merged without conflict.
    """
    return b1.is_compatible_with(b2)


def bindings_from_pairs(*pairs: tuple[Symbol, Element]) -> Bindings:
    """
    Create Bindings from (symbol, value) pairs.
    """
    return Bindings(dict(pairs))
