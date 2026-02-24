"""
Expression - Immutable symbolic expressions.

Expressions are the compound structures of the language, consisting of:
    - head: The function/operator (Symbol or Expression)
    - tail: The arguments (tuple of Elements)
    - attributes: Evaluation modifiers (frozenset of Symbols)

Implementation:
    Expressions are implemented as a tuple subclass: (head, tail, attributes)
    This provides immutability, hashability, and memory efficiency.

Examples:
    Plus[1, 2, 3]  →  Expression(Plus, 1, 2, 3)
    f[x, y]       →  Expression(f, x, y)
    Hold[x + 1]   →  Expression(Hold, Expression(Plus, x, 1), _attrs={HoldAll})
"""

from typing import (
    Any, 
    Callable, 
    Iterator, 
    Union, 
    TYPE_CHECKING,
    overload,
)

if TYPE_CHECKING:
    from .symbol import Symbol
    from .atoms import Atom, Element


# EXPRESSION CLASS

class Expression(tuple):
    """
    Immutable symbolic expression.

    Structure: (head, tail, attributes)
        - head: Symbol | Expression — the function or operator
        - tail: tuple[Element, ...] — the arguments
        - attributes: frozenset[Symbol] — evaluation attributes
    """

    __slots__ = ()

    def __new__(
        cls,
        head: Union[Symbol, Expression],
        *args: Element,
        _attrs: Union[frozenset[Symbol], set[Symbol], None] = None,
    ) -> Expression:
        """
        Construct an expression.

        Args:
            head: The head of the expression (function/operator).
            *args: The arguments (tail) of the expression.
            _attrs: Optional evaluation attributes (keyword-only via underscore).

        Returns:
            New immutable Expression instance.

        Raises:
            TypeError: If head is not a Symbol or Expression.

        Examples:
            >>> Expression(Plus, 1, 2)
            Plus[1, 2]

            >>> Expression(f, x, y, _attrs={HoldAll})
            f[x, y]  # with HoldAll attribute
        """
        # Validate head
        from .symbol import Symbol  # Local import to avoid circularity
        if not isinstance(head, (Symbol, Expression)):
            raise TypeError(
                f"Expression head must be Symbol or Expression, got {type(head).__name__}"
            )

        # Normalize attributes to frozenset
        if _attrs is None:
            attributes: frozenset[Symbol] = frozenset()
        elif isinstance(_attrs, frozenset):
            attributes = _attrs
        else:
            attributes = frozenset(_attrs)

        # Validate attributes are all Symbols
        for attr in attributes:
            if not isinstance(attr, Symbol):
                raise TypeError(
                    f"Expression attributes must be Symbols, got {type(attr).__name__}"
                )

        # Create the tuple: (head, tail, attributes)
        tail = tuple(args)
        return super().__new__(cls, (head, tail, attributes))

    @property
    def head(self) -> Union[Symbol, Expression]:
        """The function/operator of this expression."""
        return tuple.__getitem__(self, 0)

    @property
    def tail(self) -> tuple[Element, ...]:
        """The arguments of this expression as a tuple."""
        return tuple.__getitem__(self, 1)

    @property
    def args(self) -> tuple[Element, ...]:
        """Alias for tail — the arguments of this expression."""
        return tuple.__getitem__(self, 1)

    @property
    def attributes(self) -> frozenset[Symbol]:
        """The evaluation attributes of this expression."""
        return tuple.__getitem__(self, 2)

    def __len__(self) -> int:
        """Number of arguments (tail length)."""
        return len(self.tail)

    def __iter__(self) -> Iterator[Element]:
        """Iterate over arguments."""
        return iter(self.tail)

    def __contains__(self, item: object) -> bool:
        """Check if item is in arguments."""
        return item in self.tail

    @overload
    def __getitem__(self, key: int) -> Element: ...
    @overload
    def __getitem__(self, key: slice) -> tuple[Element, ...]: ...

    def __getitem__(self, key: Union[int, slice]) -> Union[Element, tuple[Element, ...]]:
        """
        Index into arguments.

        Note: This indexes into tail (arguments), not the internal
        (head, tail, attrs) structure. Use .head, .tail, .attributes
        for direct component access.

        Args:
            key: Integer index or slice.

        Returns:
            Single argument or tuple of arguments.

        Raises:
            IndexError: If index is out of range.
        """
        return self.tail[key]

    def has_attr(self, attr: Symbol) -> bool:
        """
        Check if expression has a specific attribute.

        Args:
            attr: The attribute Symbol to check for.

        Returns:
            True if the attribute is present.
        """
        return attr in self.attributes

    def has_any_attr(self, *attrs: Symbol) -> bool:
        """Check if expression has any of the specified attributes."""
        return bool(self.attributes & frozenset(attrs))

    def has_all_attrs(self, *attrs: Symbol) -> bool:
        """Check if expression has all of the specified attributes."""
        return frozenset(attrs) <= self.attributes

    def with_head(self, new_head: Union[Symbol, Expression]) -> Expression:
        """Return new expression with different head."""
        return Expression(new_head, *self.tail, _attrs=self.attributes)

    def with_tail(self, *new_args: Element) -> Expression:
        """Return new expression with different arguments."""
        return Expression(self.head, *new_args, _attrs=self.attributes)

    def with_attrs(self, *attrs: Symbol) -> Expression:
        """Return new expression with additional attributes."""
        return Expression(self.head, *self.tail, _attrs=self.attributes | frozenset(attrs))

    def without_attrs(self, *attrs: Symbol) -> Expression:
        """Return new expression with attributes removed."""
        return Expression(self.head, *self.tail, _attrs=self.attributes - frozenset(attrs))

    def with_only_attrs(self, *attrs: Symbol) -> Expression:
        """Return new expression with only the specified attributes."""
        return Expression(self.head, *self.tail, _attrs=frozenset(attrs))

    def map_args(self, fn: Callable[[Element], Element]) -> Expression:
        """
        Apply function to each argument, return new expression.

        Args:
            fn: Function to apply to each argument.

        Returns:
            New Expression with transformed arguments.
        """
        return Expression(self.head, *(fn(arg) for arg in self.tail), _attrs=self.attributes)

    def map_args_indexed(
        self, 
        fn: Callable[[int, Element], Element]
    ) -> Expression:
        """
        Apply function to each (index, argument) pair.

        Args:
            fn: Function taking (index, arg) and returning transformed arg.

        Returns:
            New Expression with transformed arguments.
        """
        return Expression(
            self.head, 
            *(fn(i, arg) for i, arg in enumerate(self.tail)), 
            _attrs=self.attributes
        )

    def append(self, *new_args: Element) -> Expression:
        """Return new expression with arguments appended."""
        return Expression(self.head, *self.tail, *new_args, _attrs=self.attributes)

    def prepend(self, *new_args: Element) -> Expression:
        """Return new expression with arguments prepended."""
        return Expression(self.head, *new_args, *self.tail, _attrs=self.attributes)

    def __hash__(self) -> int:
        """Hash based on structure."""
        return hash(("Expression", self.head, self.tail, self.attributes))

    def __eq__(self, other: object) -> bool:
        """
        Structural equality.

        Two expressions are equal if they have the same head, tail,
        and attributes.
        """
        if self is other:
            return True
        if not isinstance(other, Expression):
            return False
        return (
            self.head == other.head
            and self.tail == other.tail
            and self.attributes == other.attributes
        )

    def __repr__(self) -> str:
        """
        Detailed representation showing structure.

        Format: Head[arg1, arg2, ...]  or  Head[arg1, arg2, ...] {attrs}
        """
        head_str = str(self.head)
        args_str = ", ".join(_format_element(arg) for arg in self.tail)
        base = f"{head_str}[{args_str}]"

        if self.attributes:
            attrs_str = ", ".join(
                str(a) for a in sorted(self.attributes, key=lambda s: str(s))
            )
            return f"{base} {{attrs: {attrs_str}}}"
        return base

    def __str__(self) -> str:
        """Human-readable representation."""
        head_str = str(self.head)
        args_str = ", ".join(_format_element(arg) for arg in self.tail)
        return f"{head_str}[{args_str}]"


# MODULE-LEVEL FUNCTIONS

def _format_element(elem: Any) -> str:
    """Format an element for display in expression representation."""
    if isinstance(elem, str):
        return repr(elem)
    return str(elem)


def is_expr(obj: object) -> bool:
    """Check if an object is an Expression."""
    return isinstance(obj, Expression)


def head_of(elem: Element) -> Union[Symbol, Expression, type]:
    """
    Get the head of any element.

    - Expression: returns the head
    - Symbol: returns Symbol("Symbol")
    - int: returns Symbol("Integer")
    - float: returns Symbol("Real")
    - str: returns Symbol("String")
    - etc.

    Args:
        elem: Any element.

    Returns:
        The head of the element.
    """
    from .symbol import Symbol
    from .atoms import atom_head

    if isinstance(elem, Expression):
        return elem.head
    if isinstance(elem, Symbol):
        return Symbol("Symbol")
    return atom_head(elem)


def tail_of(elem: Element) -> tuple:
    """
    Get the tail (arguments) of any element.

    - Expression: returns arguments tuple
    - Symbol/Atoms: returns empty tuple

    Args:
        elem: Any element.

    Returns:
        The tail of the element (empty tuple for atoms).
    """
    if isinstance(elem, Expression):
        return elem.tail
    return ()


def attrs_of(elem: Element) -> frozenset[Symbol]:
    """
    Get the attributes of any element.

    - Expression: returns the expression's attributes
    - Symbol/Atoms: returns empty frozenset

    Args:
        elem: Any element.

    Returns:
        The attributes (empty frozenset for non-expressions).
    """
    if isinstance(elem, Expression):
        return elem.attributes
    return frozenset()


def has_attr(elem: Element, attr: Symbol) -> bool:
    """
    Check if an element has a specific attribute.

    Args:
        elem: Any element.
        attr: The attribute to check for.

    Returns:
        True if the element has the attribute.
    """
    return attr in attrs_of(elem)


def map_args(Expression: Expression, fn: Callable[[Element], Element]) -> Expression:
    """
    Functional interface to map over expression arguments.

    Args:
        Expression: The expression.
        fn: Function to apply to each argument.

    Returns:
        New Expression with transformed arguments.
    """
    return Expression.map_args(fn)


def replace_head(Expression: Expression, new_head: Union[Symbol, Expression]) -> Expression:
    """Functional interface to replace expression head."""
    return Expression.with_head(new_head)


def replace_tail(Expression: Expression, *new_args: Element) -> Expression:
    """Functional interface to replace expression arguments."""
    return Expression.with_tail(*new_args)


def replace_attrs(Expression: Expression, *new_attrs: Symbol) -> Expression:
    """Functional interface to replace expression attributes."""
    return Expression.with_only_attrs(*new_attrs)
