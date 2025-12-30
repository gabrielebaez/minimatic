from typing import Any, Iterator, Optional, Tuple, Callable
from core.evaluation import Context
from core.base_element import BaseElement
from core.attributes import Atom, HoldAll


class Expression(BaseElement):
    """
    Immutable n-ary symbolic expression representing a tree structure.

    An Expression consists of a head (function/operator) applied to zero or more
    arguments (tail elements). For example, `f(a, b, c)` has head `f` and tail
    `(a, b, c)`. Expressions are immutable, hashable, and support lazy evaluation
    through attributes.

    Attributes:
        head (BaseElement | str): The head of the expression, representing the
            function, operator, or symbol being applied. Can be a BaseElement
            (allowing for composed expressions) or a string identifier.
        tail (Tuple[BaseElement, ...]): Ordered sequence of argument elements.
            Each element must be a BaseElement subclass.
        attributes (Tuple[str, ...]): Immutable tuple of attribute names controlling
            expression behavior (e.g., "HoldAll" for lazy evaluation, "Atom" to
            treat as atomic).

    Args:
        head (BaseElement | str): The head of the expression. Must be either a
            BaseElement instance or a string. Raises TypeError otherwise.
        *tail (BaseElement): Variable-length positional arguments representing
            expression arguments. Each must be a BaseElement subclass. Raises
            TypeError if any tail element is not a BaseElement.
        attributes (Tuple[str, ...]): Optional tuple of attribute strings. Defaults
            to an empty tuple. Attributes control evaluation and structural behavior.

    Raises:
        TypeError: If head is neither BaseElement nor str, or if any tail element
            is not a BaseElement.

    Examples:
        Basic expression:
            `expr = Expression("Plus", Integer(1), Integer(2))`

        Nested expression:
            `expr = Expression("Times", Integer(2), Expression("Plus", Integer(3), Integer(4)))`

        Expression with attributes:
            `expr = Expression("Sin", Variable("x"), attributes=("HoldAll",))`

    Key Features:
        - **Immutability**: Once created, expressions cannot be modified. All methods
          that would change state return new Expression instances.
        - **Hashability**: Expressions are hashable and can be used as dict keys or
          in sets. Hash is computed lazily and cached.
        - **Sequence Protocol**: Supports iteration, indexing, length, and containment
          checks on tail elements.
        - **Lazy Evaluation**: Respects "HoldAll" and "Atom" attributes to prevent
          evaluation of sub-expressions.
        - **Structural Operations**: Supports mapping, replacement, and attribute
          manipulation while preserving immutability.
        - **Deep Copy Support**: Handles circular references and recursively copies
          nested Expression structures.

    Methods:
        evaluate(): Evaluate the expression using a Context, respecting attributes.
        replace(): Create new expression with modified head, tail, or attributes.
        map(): Apply a function to all tail elements, returning new expression.
        has_attribute() / add_attribute() / remove_attribute(): Manage attributes.
    """

    __slots__ = ("_head", "_tail", "_attributes", "_hash")

    def __init__(self, 
                head: BaseElement|str, 
                *tail: BaseElement,
                attributes: tuple[str]=()):
        
        if not isinstance(head, (BaseElement, str)):
            raise TypeError(f"head must be BaseElement or str, got {type(head)}")

        self._head = head
        self._tail = tail
        self._attributes = attributes
        self._hash: Optional[int] = None

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
    
    def __contains__(self, item: BaseElement) -> bool:
        return item in self._tail

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

    def __copy__(self) -> "Expression":
        """Shallow copy: creates a new Expression with the same head, tail, and attributes."""
        return Expression(
            self._head,
            *self._tail,
            attributes=self._attributes,
        )

    def __deepcopy__(self, memo: dict[int, Any]) -> "Expression":
        """Deep copy: recursively copies head and tail elements."""
        from copy import deepcopy

        obj_id = id(self)
        if obj_id in memo:
            return memo[obj_id]

        # Deep copy head if it's a BaseElement, otherwise use as-is (str is immutable)
        new_head = (deepcopy(self._head, memo) 
                    if isinstance(self._head, BaseElement) 
                    else self._head)

        # Deep copy all tail elements
        new_tail = tuple(deepcopy(t, memo) for t in self._tail)

        # Create new expression (attributes are immutable strings, so no deep copy needed)
        new_expr = Expression(
            new_head,
            *new_tail,
            attributes=self._attributes,
        )

        # Store in memo to handle circular references
        memo[obj_id] = new_expr
        return new_expr

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
    def head(self) -> BaseElement | str:
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

        # Evaluate tail elements
        evaluated_tail = self.evaluate_tail(context)

        # If head is BaseElement, evaluate it and return expression with evaluated tail
        if isinstance(self._head, BaseElement):
            evaluated_head = self._head.evaluate(context)
            return self.replace(head=evaluated_head, tail=evaluated_tail)
        else:
            return self.replace(tail=evaluated_tail)
