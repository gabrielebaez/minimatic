
from typing import (Any, Callable, 
                    Optional, Tuple, 
                    FrozenSet, Hashable)


class Expression:
    """
    Immutable symbolic expression node.

    head  : operator/name
    tail  : child expressions
    rule  : optional evaluation semantics
    value : cached evaluated result
    t     : node type flag: 'atom', 'symbol', 'compound', etc.
    attrs : frozen set of user attributes
    """

    __slots__ = ("_head", "_tail", "_rule", "_value", "_t", "_attrs", "_hash")

    def __init__(
        self,
        head: Any,
        *tail: "Expression",
        rule: Optional[Callable[..., Any]] = None,
        value: Optional[Any] = None,
        t: str = "atom",
        attributes: Tuple[Any, ...] = (),
    ) -> None:
        self._head = head
        self._tail: Tuple["Expression", ...] = tail
        self._rule = rule
        self._value = value
        self._t = t
        self._attrs: FrozenSet[Any] = frozenset(attributes)
        self._hash: Optional[int] = None

    # --------------------------------------------------
    # structural equality & hashing
    # --------------------------------------------------
    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Expression)
            and self._t == other._t
            and self._head == other._head
            and self._tail == other._tail
        )

    def __hash__(self) -> int:
        if self._hash is None:
            self._hash = hash((self._t, self._head, self._tail))
        return self._hash

    # --------------------------------------------------
    # repr / str
    # --------------------------------------------------
    def __repr__(self) -> str:
        if not self._tail:
            return f"Expression({self._head!r}, t={self._t!r})"
        return f"Expression({self._head!r}, {', '.join(map(repr, self._tail))})"

    def __str__(self) -> str:
        if self._t == "atom":
            return str(self._head)
        return f"{self._head}({', '.join(map(str, self._tail))})"

    # --------------------------------------------------
    # evaluation
    # --------------------------------------------------
    def evaluate(self) -> Any:
        if self._rule is None:
            # return self
            return self._value
        try:
            # allow keyword arguments via a dict stored in tail[0] if needed
            return self._rule(*(child.evaluate() for child in self._tail))
        except TypeError as exc:
            raise TypeError(
                f"Rule {self._rule.__name__} incompatible with tail {self._tail}"
            ) from exc

    # --------------------------------------------------
    # immutability helpers
    # --------------------------------------------------
    def replace(self, **kwargs: Any) -> "Expression":
        """Return a new Expression with specified fields updated."""
        return Expression(
            head=kwargs.get("head", self._head),
            *kwargs.get("tail", self._tail),
            rule=kwargs.get("rule", self._rule),
            value=kwargs.get("value", self._value),
            t=kwargs.get("t", self._t),
            attributes=kwargs.get("attributes", tuple(self._attrs)),
        )

    def copy(self) -> "Expression":
        return self.replace()
