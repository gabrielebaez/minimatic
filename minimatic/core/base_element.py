from abc import ABC, abstractmethod
from typing import Any, Tuple, Iterator, Callable, Union, Dict, TypeVar, Optional


T = TypeVar('T', bound='BaseElement')


class KeyError(Exception):
    """Raised when a symbol is not found in the context."""
    pass


class EvaluationError(Exception):
    """Raised when evaluation of an expression fails."""
    pass


class Context:
    """
    Represents the evaluation context for expressions.

    Provides variable storage and scope management for expression evaluation.
    This implementation distinguishes between "key not found" and "value is None".
    """

    def __init__(self, variables: Optional[Dict[str, Any]] = None):
        """
        Initialize a new context.

        Args:
            variables: Optional dictionary of variable names to their values.
        """
        self._variables: Dict[str, Any] = variables or {}

    def get(self, name: str) -> Any:
        """
        Get a variable value by name.

        Args:
            name: The variable name to look up.

        Returns:
            The variable value.

        Raises:
            KeyError: If the variable does not exist.
        """
        if name not in self._variables:
            raise KeyError(f"Symbol '{name}' not found in context.")
        return self._variables[name]

    def set(self, name: str, value: Any) -> None:
        """
        Set a variable value.

        Args:
            name: The variable name.
            value: The value to store.
        """
        self._variables[name] = value

    def has(self, name: str) -> bool:
        """
        Check if a variable exists in the context.

        Args:
            name: The variable name to check.

        Returns:
            True if the variable exists, False otherwise.
        """
        return name in self._variables

    @property
    def variables(self) -> Dict[str, Any]:
        """Get all variables in the context."""
        return self._variables.copy()

    def copy(self) -> 'Context':
        """
        Create a shallow copy of this context.

        Returns:
            A new Context with the same variables.
        """
        return Context(self._variables.copy())


class BaseElement(ABC):
    """
    Abstract base class for all symbolic elements.

    All symbolic computation elements inherit from this class, providing
    a common interface for symbolic manipulation and evaluation.
    """

    @property
    @abstractmethod
    def head(self) -> Union[str, 'BaseElement']:
        """
        Get the head (function/operator) of this element.

        Returns:
            A string or BaseElement representing the head.
        """
        raise NotImplementedError("Subclasses should implement this method.")

    @property
    @abstractmethod
    def tail(self) -> Tuple['BaseElement', ...]:
        """
        Get the tail (arguments) of this element.

        Returns:
            A tuple of BaseElement instances representing arguments.
        """
        raise NotImplementedError("Subclasses should implement this method.")

    @abstractmethod
    def evaluate(self, context: Optional[Context]) -> 'BaseElement':
        """
        Evaluate this element within the given context.

        Args:
            context: The evaluation context containing variables and functions.

        Returns:
            The evaluated result. Never returns None.

        Raises:
            KeyError: If a required symbol is not found in the context.
            EvaluationError: If evaluation fails for any reason.
        """
        raise NotImplementedError("Subclasses should implement this method.")

    @abstractmethod
    def __hash__(self) -> int:
        """Get hash value for this element."""
        raise NotImplementedError("Subclasses should implement this method.")

    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        """Check equality with another object."""
        raise NotImplementedError("Subclasses should implement this method.")

    def __bool__(self) -> bool:
        """
        Prevent truthiness confusion by explicitly defining boolean conversion.

        Raises:
            TypeError: To prevent implicit boolean conversion.
        """
        raise TypeError(
            f"Cannot convert {type(self).__name__} to bool. "
            "Use explicit comparison or check attributes instead."
        )


class Symbol(BaseElement):
    """
    Represents a symbolic variable or identifier.

    Symbols are atomic elements that can represent variables, function names,
    or symbolic constants.
    """

    def __init__(self, name: str):
        """
        Initialize a Symbol.

        Args:
            name: The symbol name (must be a string).

        Raises:
            TypeError: If name is not a string.
        """
        if not isinstance(name, str):
            raise TypeError(f"Symbol name must be a string, got {type(name).__name__}")
        self._name = name

    @property
    def head(self) -> str:
        """Get the symbol name."""
        return self._name

    @property
    def tail(self) -> Tuple['BaseElement', ...]:
        """Symbols have no tail (empty tuple)."""
        return ()

    @property
    def name(self) -> str:
        """Get the symbol name (alias for head)."""
        return self._name

    def __repr__(self) -> str:
        return self._name

    def __str__(self) -> str:
        return self._name

    def __hash__(self) -> int:
        return hash((Symbol, self._name))

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Symbol):
            return False
        return self._name == other._name

    def evaluate(self, context: Optional[Context]) -> 'BaseElement':
        """
        Evaluate the symbol in the given context.

        If the symbol exists in the context, returns its value.
        Otherwise, returns the symbol unchanged.

        Args:
            context: The evaluation context.

        Returns:
            The symbol's value from context, or the symbol itself.

        Raises:
            KeyError: If the context is provided but the symbol is not found.
        """
        if context is None:
            return self

        if context.has(self._name):
            return context.get(self._name)

        return self


class Literal(BaseElement):
    """
    Represents a literal value in symbolic computation.

    Literals wrap actual Python values (numbers, strings, etc.) with
    a head that represents their type.
    """

    def __init__(self, value: Any):
        """
        Initialize a Literal.

        Args:
            value: The underlying Python value.
        """
        self._value = value
        self._type = type(value).__name__

    @property
    def head(self) -> str:
        """Get the literal type name."""
        return self._type

    @property
    def tail(self) -> Tuple['BaseElement', ...]:
        """Literals have no tail (empty tuple)."""
        return ()

    @property
    def value(self) -> Any:
        """Get the underlying Python value."""
        return self._value

    def __repr__(self) -> str:
        return f"{self.head}({self._value!r})"

    def __str__(self) -> str:
        return self.__repr__()

    def __hash__(self) -> int:
        return hash((Literal, self._type, self._value))

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Literal):
            return False
        return self._type == other._type and self._value == other._value

    def evaluate(self, context: Optional[Context]) -> 'Literal':
        """
        Evaluate the literal.

        Literals evaluate to themselves as they contain concrete values.

        Returns:
            The literal itself.
        """
        return self


class Expression(BaseElement):
    """
    Immutable n-ary symbolic expression representing a tree structure.

    An Expression consists of a head (function/operator) applied to zero or more
    arguments (tail elements). Expressions are immutable, hashable, and support
    structural operations and evaluation.

    Key Features:
        - **Immutability**: Once created, expressions cannot be modified.
        - **Hashability**: Expressions are hashable for use as dict keys or in sets.
        - **Sequence Protocol**: Supports iteration and indexing of tail elements.
        - **Structural Operations**: Mapping, replacement, and transformation methods.
        - **Function-like Interface**: Can be called to evaluate directly.
    """

    def __init__(self, head: Union['BaseElement', str], *tail: 'BaseElement'):
        """
        Initialize an Expression.

        Args:
            head: The head of the expression (function, operator, or symbol).
            *tail: Variable-length positional arguments (expression arguments).

        Raises:
            TypeError: If head is not a string or BaseElement, or if any tail
                       element is not a BaseElement.
        """
        if not isinstance(head, (str, BaseElement)):
            raise TypeError(
                f"Expression head must be a string or BaseElement, got {type(head).__name__}"
            )

        for i, item in enumerate(tail):
            if not isinstance(item, BaseElement):
                raise TypeError(
                    f"Expression tail element at index {i} must be a BaseElement, got {type(item).__name__}"
                )

        self._head = head
        self._tail = tail
        self._hash: Optional[int] = None

    def __repr__(self) -> str:
        tail_str = ", ".join(repr(t) for t in self._tail)
        return f"{self._head}({tail_str})"

    def __str__(self) -> str:
        return repr(self)

    # Sequence protocol implementation
    def __iter__(self) -> Iterator['BaseElement']:
        return iter(self._tail)

    def __len__(self) -> int:
        return len(self._tail)

    def __getitem__(self, idx: int) -> 'BaseElement':
        return self._tail[idx]

    def __contains__(self, item: 'BaseElement') -> bool:
        return item in self._tail

    def __call__(self, context: Optional[Context] = None) -> 'BaseElement':
        """
        Call the expression as a function.

        This provides a convenient way to evaluate expressions using
        function-call syntax.

        Args:
            context: The evaluation context.

        Returns:
            The evaluated result.
        """
        return self.evaluate(context)

    # Immutability and comparison helpers
    def __hash__(self) -> int:
        if self._hash is None:
            # Use a tuple directly without creating a new object
            self._hash = hash((self._head, self._tail))
        return self._hash

    def __eq__(self, other: Any) -> bool:
        """
        Check equality with another object.

        Returns True only for BaseElement instances with matching head and tail.
        """
        if not isinstance(other, BaseElement):
            return False

        if isinstance(other, Expression):
            return self._head == other._head and self._tail == other._tail

        try:
            return self._head == other.head and self._tail == other.tail
        except AttributeError:
            return False

    def __copy__(self) -> 'Expression':
        """Shallow copy returns self due to immutability."""
        return self

    def __deepcopy__(self, memo: Optional[Dict[int, Any]]) -> 'Expression':
        """
        Deep copy returns self due to immutability.

        Since expressions are immutable, deep copying is unnecessary.
        """
        return self

    # Property accessors
    @property
    def head(self) -> Union['BaseElement', str]:
        """Get the head of the expression."""
        return self._head

    @property
    def tail(self) -> Tuple['BaseElement', ...]:
        """Get the tail (arguments) of the expression."""
        return self._tail

    # Structural manipulation methods
    def replace(
        self,
        head: Optional[Union['BaseElement', str]] = None,
        tail: Optional[Tuple['BaseElement', ...]] = None,
    ) -> 'Expression':
        """
        Create a new expression with modified components.

        Args:
            head: Optional new head.
            tail: Optional new tail.

        Returns:
            A new Expression with the specified modifications.
        """
        new_head = head if head is not None else self._head
        new_tail = tail if tail is not None else self._tail
        return Expression(new_head, *new_tail)

    def map(self, fn: Callable[['BaseElement'], 'BaseElement']) -> 'Expression':
        """
        Apply a function to all tail elements.

        Args:
            fn: Function to apply to each tail element.

        Returns:
            A new Expression with mapped tail elements.
        """
        return self.replace(tail=tuple(fn(t) for t in self._tail))

    def _evaluate_tail(self, context: Optional[Context]) -> Tuple['BaseElement', ...]:
        """
        Evaluate all tail elements with error handling.

        Args:
            context: The evaluation context.

        Returns:
            Tuple of evaluated tail elements.

        Raises:
            EvaluationError: If any tail element evaluation fails.
        """
        evaluated = []
        for i, tail_element in enumerate(self._tail):
            try:
                evaluated.append(tail_element.evaluate(context))
            except (KeyError, EvaluationError) as e:
                raise EvaluationError(
                    f"Failed to evaluate tail element at index {i} in {self}: {e}"
                ) from e
        return tuple(evaluated)

    def evaluate(self, context: Optional[Context] = None) -> 'BaseElement':
        """
        Evaluate the expression based on its head and context.

        Evaluation strategy:
        1. Evaluate all tail elements recursively
        2. If head is a Symbol, evaluate it to potentially get a function
        3. If head is a string, look it up in context as a function name
        4. Apply the function to the evaluated arguments

        Args:
            context: The evaluation context containing variables and functions.

        Returns:
            The evaluated result.

        Raises:
            KeyError: If a required symbol or function is not found.
            EvaluationError: If evaluation or function application fails.
        """
        if context is None:
            context = Context()

        # Step 1: Evaluate tail elements
        evaluated_tail = self._evaluate_tail(context)

        # Step 2: Get the callable function from the head
        func = None

        if isinstance(self._head, str):
            # Look up the string as a function name in context
            func = context.get(self._head)
        elif isinstance(self._head, Symbol):
            # Evaluate the symbol to get its value (potentially a function)
            func = self._head.evaluate(context)
        elif isinstance(self._head, BaseElement):
            # Evaluate the element to potentially get a function
            func = self._head.evaluate(context)

        # Step 3: Apply the function if we have one
        if callable(func):
            try:
                result = func(*evaluated_tail)
                if isinstance(result, BaseElement):
                    return result
                else:
                    # TODO: Auto-wrap non-BaseElement results
                    return result
            except Exception as e:
                raise EvaluationError(
                    f"Failed to apply function {self._head} to arguments {evaluated_tail}: {e}"
                ) from e

        # If head is not callable, return expression with evaluated components
        if isinstance(self._head, BaseElement):
            evaluated_head = self._head.evaluate(context)
            return self.replace(head=evaluated_head, tail=evaluated_tail)
        else:
            return self.replace(tail=evaluated_tail)

    # Factory methods for convenient construction
    @classmethod
    def from_function(cls, name: str, *args: 'BaseElement') -> 'Expression':
        """
        Create an expression from a function name and arguments.

        Args:
            name: The function name as string.
            *args: Function arguments.

        Returns:
            A new Expression.
        """
        return cls(name, *args)

    @classmethod
    def list_of(cls, *elements: 'BaseElement') -> 'Expression':
        """
        Create a List expression containing the given elements.

        Args:
            *elements: Elements to include in the list.

        Returns:
            A new Expression with head "List".
        """
        return cls("List", *elements)
