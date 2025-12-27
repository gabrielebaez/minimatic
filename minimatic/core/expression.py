from typing import Any, Iterator, Optional, Sequence, Tuple, Callable
from abc import ABC


class BaseElement(ABC):

    def head(self) -> str:
        raise NotImplementedError("Subclasses should implement this method.")
    
    def tail(self) -> Sequence[Any]:
        raise NotImplementedError("Subclasses should implement this method.")

    def attributes(self) -> dict:
        raise NotImplementedError("Subclasses should implement this method.")

    def evaluate(self) -> Any:
        raise NotImplementedError("Subclasses should implement this method.")


class Expression(BaseElement):
    """
    Immutable n-ary symbolic expression.
    head(...) with optional attributes and shared sub-expressions.
    """

    __slots__ = ("_head", "_tail", "_attributes", "_hash")

    def __init__(self, 
                 head: BaseElement, 
                 tail: tuple[BaseElement],
                 attributes: tuple[str]=()):
        self._head = head
        self._tail = tail
        self._attributes = attributes
        self._hash: Optional[int] = None  # cached hash
        # validation
        if "Executable" in self._attributes and not callable(self._head):
            raise TypeError("Executable expressions require a callable head.")
    
    def __repr__(self):
        return f"{self._head}({self._tail})"

    # sequence protocol
    def __iter__(self) -> Iterator[BaseElement]:
        return iter(self._tail)

    def __len__(self) -> int:
        return len(self._tail)

    def __getitem__(self, idx: int) -> BaseElement:
        return self._tail[idx]

    # immutability helpers
    def __hash__(self) -> int:
        if self._hash is None:
            self._hash = hash(
                (self._head, self._tail, self._attributes)
            )
        return self._hash

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, Expression)
            and self._head == other._head
            and self._tail == other._tail
            and self._attributes == other._attributes
        )

    # attribute manipulation
    def has_attribute(self, attr: str) -> bool:
        return attr in self._attributes

    def add_attribute(self, attr: str) -> "Expression":
        if attr in self._attributes:
            return self
        return Expression(
            self._head,
            self._tail,
            self._attributes + (attr,),
        )

    def remove_attribute(self, attr: str) -> "Expression":
        return Expression(
            self._head,
            self._tail,
            tuple(a for a in self._attributes if a != attr),
        )

    # accessors
    @property
    def head(self) -> BaseElement:
        return self._head

    @property
    def tail(self) -> Tuple[BaseElement, ...]:
        return self._tail

    @property
    def attributes(self) -> Tuple[str, ...]:
        return self._attributes
    
    def attributeQ(self, attribute: BaseElement) -> bool:
        return attribute in self._attributes

    # structural substitution
    def replace(
        self,
        head: Optional[BaseElement] = None,
        tail: Optional[Tuple[BaseElement, ...]] = None,
        attributes: Optional[Tuple[str, ...]] = None,
    ) -> "Expression":
        return Expression(
            head if head is not None else self._head,
            tail if tail is not None else self._tail,
            attributes if attributes is not None else self._attributes,
        )

    def map(self, fn: Callable[[BaseElement], BaseElement]) -> "Expression":
        """Return a new expression whose tail is mapped through `fn`."""
        return self.replace(tail=tuple(fn(t) for t in self._tail))
    
    # evaluation
    def evaluate(self, context: Any = None) -> BaseElement:
        if "Executable" in self._attributes:
            return self._head(self._tail).evaluate(context)
        else:
            return self
