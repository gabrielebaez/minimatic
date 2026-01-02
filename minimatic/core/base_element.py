from abc import ABC
from copy import deepcopy
from typing import (
    Any, Optional, Sequence, Tuple, Iterator, Callable
)


class Context:
    """
    Represents the evaluation context for expressions.
    """
    def __init__(self, variables: dict[str, Any] | None = None):
        self.variables = variables or {}


class BaseElement(ABC):

    @property
    def head(self) -> str|BaseElement:
        raise NotImplementedError("Subclasses should implement this method.")
    
    @property
    def tail(self) -> Tuple[()]|Sequence[BaseElement]:
        raise NotImplementedError("Subclasses should implement this method.")

    def evaluate(self, context: Optional[Context]) -> BaseElement:
        raise NotImplementedError("Subclasses should implement this method.")


class Symbol(BaseElement):
    def __init__(self, head: str|BaseElement):
        self._head = head
    
    @property
    def head(self) -> str|BaseElement:
        return self._head
    
    @property
    def tail(self) -> Tuple[()]:
        return ()
    
    def __repr__(self) -> str:
        return str(self.head)

    def evaluate(self, context:Optional[Context]):
        return self


class Literal(BaseElement):
    def __init__(self, head: str|BaseElement,
                 value: Any):
        self._head = head
        self._value = value
    
    @property
    def head(self) -> str|BaseElement:
        return self._head

    @property
    def tail(self) -> Tuple[BaseElement]:
        return (Symbol(self.value),)
    
    @property
    def value(self) -> Any:
        return self._value
    
    def __repr__(self) -> str:
        return f"{self.head}({self.value})"
    
    def evaluate(self, context:Optional[Context]):
        return self


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

    Args:
        head (BaseElement | str): The head of the expression. Must be either a
            BaseElement instance or a string. Raises TypeError otherwise.
        *tail (BaseElement): Variable-length positional arguments representing
            expression arguments. Each must be a BaseElement subclass. Raises
            TypeError if any tail element is not a BaseElement.

    Examples:
        Basic expression:
            `expr = Expression("Plus", Integer(1), Integer(2))`

        Nested expression:
            `expr = Expression("Times", Integer(2), Expression("Plus", Integer(3), Integer(4)))`

    Key Features:
        - **Immutability**: Once created, expressions cannot be modified. All methods
          that would change state return new Expression instances.
        - **Hashability**: Expressions are hashable and can be used as dict keys or
          in sets. Hash is computed lazily and cached.
        - **Sequence Protocol**: Supports iteration, indexing, length, and containment
          checks on tail elements.
        - **Structural Operations**: Supports mapping, replacement, and attribute
          manipulation while preserving immutability.
        - **Deep Copy Support**: Handles circular references and recursively copies
          nested Expression structures.

    Methods:
        evaluate(): Evaluate the expression using a Context, respecting attributes.
        replace(): Create new expression with modified head, tail, or attributes.
        map(): Apply a function to all tail elements, returning new expression.
    """

    def __init__(self, 
                head: BaseElement|str, 
                *tail: BaseElement):
        self._head = head
        self._tail = tail
        self._hash: Optional[int] = None

    def __repr__(self) -> str:
        tail_str = ", ".join(repr(t) for t in self._tail)
        return f"{self._head}({tail_str})"

    def __str__(self) -> str:
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
                (self._head, self._tail)
            )
        return self._hash

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, BaseElement)
            and self._head == other.head
            and self._tail == other.tail
        )

    def __copy__(self) -> Expression:
        """Shallow copy: creates a new Expression with the same head, tail, and attributes."""
        return Expression(
            self._head,
            *self._tail,
        )

    def __deepcopy__(self, memo: dict[int, Any]) -> Expression:
        """Deep copy: recursively copies head and tail elements."""

        obj_id = id(self)
        if obj_id in memo:
            return memo[obj_id]

        new_head = (deepcopy(self._head, memo) 
                    if isinstance(self._head, BaseElement) 
                    else self._head)

        new_tail = tuple(deepcopy(t, memo) for t in self._tail)

        new_expr = Expression(
            new_head,
            *new_tail,
        )

        # Store in memo to handle circular references
        memo[obj_id] = new_expr
        return new_expr

    @property
    def head(self) -> BaseElement | str:
        return self._head

    @property
    def tail(self) -> Tuple[BaseElement, ...]:
        return self._tail

    def replace(
        self,
        head: Optional[BaseElement|str] = None,
        tail: Optional[Tuple[BaseElement, ...]] = None,
    ) -> Expression:
        new_head = head if head is not None else self._head
        new_tail = tail if tail is not None else self._tail

        return Expression(
            new_head,
            *new_tail,
        )

    def map(self, fn: Callable[[BaseElement], BaseElement]) -> Expression:
        """Return a new expression whose tail is mapped through `fn`."""
        return self.replace(tail=tuple(fn(t) for t in self._tail))
    
    def evaluate_tail(self, context: Optional[Context]) -> Tuple[BaseElement,...]:
        return tuple(t.evaluate(context) for t in self._tail)

    def evaluate(self, context: Optional[Context]) -> BaseElement:
        """
        Evaluate the expression based on its head and attributes.
        - If Head is BaseElement: Evaluate head, and return -> evaluated_head(evaluated_tail)
        - Else: return head(evaluated_tail)
        """

        evaluated_tail = self.evaluate_tail(context)

        if isinstance(self._head, BaseElement):
            evaluated_head = self._head.evaluate(context)
            return self.replace(head=evaluated_head, tail=evaluated_tail)
        else:
            return self.replace(tail=evaluated_tail)
