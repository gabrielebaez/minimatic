from typing import Any, Iterator, Optional, Tuple, Callable
from core.evaluation import Context
from core.base_element import BaseElement
from core.attributes import Atom, HoldAll


class Expression(BaseElement):
    """
    Immutable n-ary symbolic expression.
    head(...) with optional attributes and shared sub-expressions.
    """

    __slots__ = ("_head", "_tail", "_attributes", "_hash")

    def __init__(self, 
                 head: BaseElement|str, 
                 *tail: BaseElement,
                 attributes: tuple[str]=()):
        self._head = head
        self._tail = tail
        self._attributes = attributes
        self._hash: Optional[int] = None  # cached hash

    def __repr__(self) -> str:
        tail_str = ", ".join(repr(t) for t in self._tail)
        return f"{self._head}({tail_str})"

    def __str__(self) -> str:
        """User-friendly string representation."""
        return repr(self)

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
            *self._tail,
            attributes=self._attributes + (attr,),
        )

    def remove_attribute(self, attr: str) -> "Expression":
        return Expression(
            self._head,
            *self._tail,
            attributes=tuple(a for a in self._attributes if a != attr),
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

    # structural substitution
    def replace(
        self,
        head: Optional[BaseElement] = None,
        tail: Optional[Tuple[BaseElement, ...]] = None,
        attributes: Optional[Tuple[str, ...]] = None,
    ) -> "Expression":
        new_head = head if head is not None else self._head
        new_tail = tail if tail is not None else self._tail
        new_attributes = attributes if attributes is not None else self._attributes

        return Expression(
            new_head,
            *new_tail,
            attributes=new_attributes,
        )

    def map(self, fn: Callable[[BaseElement], BaseElement]) -> "Expression":
        """Return a new expression whose tail is mapped through `fn`."""
        return self.replace(tail=tuple(fn(t) for t in self._tail))
    
    # Helper function
    def evaluate_tail(self, context: Context):
        return tuple(
            t.evaluate(context) if isinstance(t, Expression) else t
            for t in self._tail)


    # evaluation
    def evaluate(self, context: Any = None) -> BaseElement:
        """
        Evaluate the expression based on its head and attributes.
        - If "Hold" in attributes: return unevaluated
        - If "Atom" in attributes: return unevaluated
        - If Head is BaseElement: Evaluate head, and return -> evaluated_head(evaluated_tail)
        - Else: return head(evaluated_tail)
        """
        # If HoldAll attribute is present, return unevaluated
        if self.has_attribute(HoldAll):
            return self

        # If Atom attribute is present, return unevaluated
        if self.has_attribute(Atom):
            return self

        # Evaluate tail elements recursively
        evaluated_tail = self.evaluate_tail(context)

        # If head BaseElement, evaluate it and return expression with evaluated tail
        if isinstance(self._head, BaseElement):
            evaluated_head = self._head.evaluate()
            return self.replace(head=evaluated_head, tail=evaluated_tail)
        else:
            return self.replace(tail=evaluated_tail)
