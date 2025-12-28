"""
## Arithmetic & Logic

- Plus(a, b, ...)      # +
- Subtract(a, b, ...)  # -
- Times(a, b, ...)     # *
- div(a, b, ...)       # /
- mod(a, b)            # %
- Eq(a, b)             # ==
- LessThan(a, b)       # <
- GreaterThan(a, b)    # >
- And(a, b)            # logical and
- Or(a, b)             # logical or
- Not(a)               # logical not
"""

from core.expression import Expression, BaseElement
from core.evaluation import Context
from builtin.symbols import (
    Integer, Number, Float, Executable, Atom,
    IntegerSymbol, NumberSymbol, FloatSymbol
)


class Plus(Expression):
    """
    Plus(a, b, ...)
    Sums all numeric arguments.
    Supports Integer, Number, and Float symbols.
    Returns an Expression with the appropriate numeric type.
    """
    def __init__(self, tail: tuple[BaseElement]):
        super().__init__(head=Plus, tail=tail, attributes=(Executable,))
    
    def evaluate(self, _) -> Expression:
        total = 0
        for element in self._tail:
            value = element.tail
            if element.head in (Integer, Number, Float):
                total += value
            else:
                raise TypeError("Plus operation only supports Integer, Number, and Float symbols.")

        if all(element.head == Integer for element in self._tail):
            return IntegerSymbol(total)
        elif all(element.head == Number for element in self._tail):
            return NumberSymbol(total)
        else:
            return FloatSymbol(total)


class Subtract(Expression):
    """
    Subtract(a, b, ...)
    Subtracts all subsequent numeric arguments from the first.
    Supports Integer, Number, and Float symbols.
    Returns an Expression with the appropriate numeric type.
    """
    def __init__(self, tail: tuple[BaseElement]):
        super().__init__(head=Subtract, tail=tail, attributes=(Executable,))
    
    def evaluate(self, _) -> Expression:
        if not self._tail:
            raise ValueError("Subtract operation requires at least one argument.")

        first_element = self._tail[0]
        if first_element.head not in (Integer, Number, Float):
            raise TypeError("Subtract operation only supports Integer, Number, and Float symbols.")

        result = first_element.tail

        for element in self._tail[1:]:
            value = element.tail
            if element.head in (Integer, Number, Float):
                result -= value
            else:
                raise TypeError("Subtract operation only supports Integer, Number, and Float symbols.")

        if all(element.head == Integer for element in self._tail):
            return IntegerSymbol(result)
        elif all(element.head == Number for element in self._tail):
            return NumberSymbol(result)
        else:
            return FloatSymbol(result)


class Times(Expression):
    """
    Times(a, b, ...)
    Multiplies all numeric arguments.
    Supports Integer, Number, and Float symbols.
    Returns an Expression with the appropriate numeric type.
    """
    def __init__(self, tail: tuple[BaseElement]):
        super().__init__(head=Times, tail=tail, attributes=(Executable,))
    
    def evaluate(self, _) -> Expression:
        product = 1
        for element in self._tail:
            value = element.tail
            if element.head in (Integer, Number, Float):
                product *= value
            else:
                raise TypeError("Times operation only supports Integer, Number, and Float symbols.")

        if all(element.head == Integer for element in self._tail):
            return IntegerSymbol(product)
        elif all(element.head == Number for element in self._tail):
            return NumberSymbol(product)
        else:
            return FloatSymbol(product)


class LessThan(Expression):
    """
    LessThan(a, b)
    Compares two values for less-than.
    Supports Integer, Number, and Float symbols.
    Returns a Boolean expression.
    """
    def __init__(self, tail: tuple[BaseElement]):
        super().__init__(head=LessThan, tail=tail, attributes=(Executable,))

    def evaluate(self, _) -> Expression:
        a_val = self._tail[0]
        b_val = self._tail[1]

        head_a = a_val.head
        head_b = b_val.head

        _valid_types = (Integer, Number, Float)

        if head_a not in _valid_types or head_b not in _valid_types:
            raise TypeError("LessThan operation only supports Integer, Number, and Float symbols.")
        result = a_val.tail < b_val.tail
        return Expression("Boolean", result, attributes=(Atom,))


class GreaterThan(Expression):
    """
    GreaterThan(a, b)
    Compares two values for greater-than.
    Supports Integer, Number, and Float symbols.
    Returns a Boolean expression.
    """
    def __init__(self, *tail: BaseElement):
        super().__init__(head=GreaterThan, *tail, attributes=(Executable,))

    def evaluate(self, _) -> Expression:
        a_val = self._tail[0]
        b_val = self._tail[1]

        _valid_types = (Integer, Number, Float)

        if a_val.head not in _valid_types or b_val.head not in _valid_types:
            raise TypeError("GreaterThan operation only supports Integer, Number, and Float symbols.")
        result = a_val.tail > b_val.tail
        return Expression("Boolean", result, attributes=(Atom,))
