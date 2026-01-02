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
- And(a, b)            # logical an
- Or(a, b)             # logical or
- Not(a)               # logical not
"""
from core.base_element import BaseElement, Context, Expression, Literal
from builtin.heads import Integer, Number, Float
from typing import Optional


NUMERIC = (Integer, Number, Float)


class Plus(Expression):
    """
    Plus(a, b, ...)
    Sums all numeric arguments.
    Supports Integer, Number, and Float symbols.
    Returns an Expression with the appropriate numeric type.
    """
    def __init__(self, *tail: BaseElement):
        super().__init__("Plus", *tail)

    def evaluate(self, context: Optional[Context]) -> Literal:
        # First, evaluate tail elements
        evaluated_tail = self.evaluate_tail(context)

        total = 0
        result_type = None

        for element in evaluated_tail:
            # Extract numeric value from evaluated element
            if isinstance(element, Literal):
                head = element.head
                value = element.value

                if head == Integer:
                    total += int(value)
                    result_type = "Integer"
                elif head == Number:
                    total += float(value)
                    if result_type != "Float":
                        result_type = "Number"
                elif head == Float:
                    total += float(value)
                    result_type = "Float"
                else:
                    raise TypeError(f"Plus does not support type '{head}'.")
            else:
                raise ValueError(f"Invalid numeric expression: {element}")

        # Return result with appropriate type
        if result_type == "Integer":
            return Literal(Integer, total)
        elif result_type == "Float":
            return Literal(Float, total)
        else:
            return Literal(Number, total)


class Subtract(Expression):
    """
    Subtract(a, b, ...)
    Subtracts all subsequent numeric arguments from the first.
    Supports Integer, Number, and Float symbols.
    Returns an Expression with the appropriate numeric type.
    """
    def __init__(self, *tail: tuple[BaseElement]):
        super().__init__(head="Subtract", *tail)
    
    def evaluate(self, context: Optional[Context]) -> Literal:
        if not self._tail:
            raise ValueError("Subtract operation requires at least one argument.")

        first_element = self._tail[0]
        if first_element.head not in NUMERIC:
            raise TypeError("Subtract operation only supports Integer, Number, and Float symbols.")

        result = first_element.tail

        for element in self._tail[1:]:
            value = element.tail
            if element.head in NUMERIC:
                result -= value
            else:
                raise TypeError("Subtract operation only supports Integer, Number, and Float symbols.")

        if all(element.head == "Integer" for element in self._tail):
            return Literal(element.head, result)
        elif all(element.head == "Number" for element in self._tail):
            return Literal(Number, result)
        else:
            return Literal(Float, result)


class Times(Expression):
    """
    Times(a, b, ...)
    Multiplies all numeric arguments.
    Supports Integer, Number, and Float symbols.
    Returns an Expression with the appropriate numeric type.
    """
    def __init__(self, tail: tuple[BaseElement]):
        super().__init__(head=Times, tail=tail)
    
    def evaluate(self, _) -> Expression:
        product = 1
        for element in self._tail:
            value = element.tail
            if element.head in NUMERIC:
                product *= value
            else:
                raise TypeError("Times operation only supports Integer, Number, and Float symbols.")

        if all(element.head == "Integer" for element in self._tail):
            return IntegerSymbol(product)
        elif all(element.head == "Number" for element in self._tail):
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
        super().__init__(head=LessThan, tail=tail)

    def evaluate(self, _) -> Expression:
        a_val = self._tail[0]
        b_val = self._tail[1]

        head_a = a_val.head
        head_b = b_val.head

        _valid_types = NUMERIC

        if head_a not in _valid_types or head_b not in _valid_types:
            raise TypeError("LessThan operation only supports Integer, Number, and Float symbols.")
        result = a_val.tail < b_val.tail
        return Expression("Boolean", result)


class GreaterThan(Expression):
    """
    GreaterThan(a, b)
    Compares two values for greater-than.
    Supports Integer, Number, and Float symbols.
    Returns a Boolean expression.
    """
    def __init__(self, *tail: BaseElement):
        super().__init__(head=GreaterThan, *tail)

    def evaluate(self, _) -> Expression:
        a_val = self._tail[0]
        b_val = self._tail[1]

        _valid_types = NUMERIC

        if a_val.head not in _valid_types or b_val.head not in _valid_types:
            raise TypeError("GreaterThan operation only supports Integer, Number, and Float symbols.")
        result = a_val.tail > b_val.tail
        return Expression("Boolean", result)
