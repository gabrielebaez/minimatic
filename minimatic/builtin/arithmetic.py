"""
## Arithmetic & Logic

- Plus(a, b, ...)      # +
- sub(a, b, ...)      # -
- mul(a, b, ...)      # *
- div(a, b, ...)      # /
- mod(a, b)           # %
- Eq(a, b)            # ==
- LessThan(a, b)      # <
- GreaterThan(a, b)   # >
- And(a, b)           # logical and
- Or(a, b)            # logical or
- Not(a)              # logical not
"""

from core.expression import Expression, BaseElement
from builtin.symbols import Integer, Number, Float, Executable, Atom


class Plus(Expression):
    """
    Plus(a, b, ...)
    Sums all numeric arguments.
    Supports Integer, Number, and Float symbols.
    Returns an Expression with the appropriate numeric type.
    """
    def __init__(self, tail: tuple[BaseElement]):
        super().__init__(head=Plus, tail=tail, attributes=(Executable,))
    
    def evaluate(self) -> Expression:
        total = 0
        for element in self._tail:
            value = element.get_tail
            if element.get_head == Integer:
                total += value
            elif element.get_head == Number:
                total += value
            elif element.get_head == Float:
                total += value
            else:
                raise TypeError("Plus operation only supports Integer, Number, and Float symbols.")
        
        if all(element.get_head == Integer for element in self._tail):
            return Expression(Integer, total, attributes=(Atom,))
        elif all(element.get_head == Number for element in self._tail):
            return Expression(Number, total, attributes=(Atom,))
        else:
            return Expression(Float, total, attributes=(Atom,))


class Subtract(Expression):
    """
    Subtract(a, b, ...)
    Subtracts all subsequent numeric arguments from the first.
    Supports Integer, Number, and Float symbols.
    Returns an Expression with the appropriate numeric type.
    """
    def __init__(self, tail: tuple[BaseElement]):
        super().__init__(head=Subtract, tail=tail, attributes=(Executable,))
    
    def evaluate(self) -> Expression:
        if not self._tail:
            raise ValueError("Subtract operation requires at least one argument.")
        
        first_value = self._tail[0].get_tail
        if self._tail[0].get_head == Integer:
            total = first_value
            for element in self._tail[1:]:
                if element.get_head != Integer:
                    raise TypeError("Subtract operation only supports Integer symbols.")
                total -= element.get_tail
            return Expression(Integer, total, attributes=(Atom,))
        
        elif self._tail[0].get_head == Number:
            total = first_value
            for element in self._tail[1:]:
                if element.get_head != Number:
                    raise TypeError("Subtract operation only supports Number symbols.")
                total -= element.get_tail
            return Expression(Number, total, attributes=(Atom,))
        
        elif self._tail[0].get_head == Float:
            total = first_value
            for element in self._tail[1:]:
                if element.get_head != Float:
                    raise TypeError("Subtract operation only supports Float symbols.")
                total -= element.get_tail
            return Expression(Float, total, attributes=(Atom,))
        
        else:
            raise TypeError("Subtract operation only supports Integer, Number, and Float symbols.")


class Times(Expression):
    """
    Times(a, b, ...)
    Multiplies all numeric arguments.
    Supports Integer, Number, and Float symbols.
    Returns an Expression with the appropriate numeric type.
    """
    def __init__(self, tail: tuple[BaseElement]):
        super().__init__(head=Times, tail=tail, attributes=(Executable,))
    
    def evaluate(self) -> Expression:
        product = 1
        for element in self._tail:
            value = element.get_tail
            if element.get_head == Integer:
                product *= value
            elif element.get_head == Number:
                product *= value
            elif element.get_head == Float:
                product *= value
            else:
                raise TypeError("Times operation only supports Integer, Number, and Float symbols.")
        
        if all(element.get_head == Integer for element in self._tail):
            return Expression(Integer, product, attributes=(Atom,))
        elif all(element.get_head == Number for element in self._tail):
            return Expression(Number, product, attributes=(Atom,))
        else:
            return Expression(Float, product, attributes=(Atom,))


class LessThan(Expression):
    """
    LessThan(a, b)
    Compares two values for less-than.
    Supports Integer, Number, and Float symbols.
    Returns a Boolean expression.
    """
    def __init__(self, tail: tuple[BaseElement]):
        super().__init__(head=LessThan, tail=tail, attributes=(Executable,))

    def evaluate(self) -> Expression:
        a_val = self._tail[0]
        b_val = self._tail[1]

        _valid_types = (Integer, Number, Float)

        if a_val.get_head not in _valid_types or b_val.get_head not in _valid_types:
            raise TypeError("LessThan operation only supports Integer, Number, and Float symbols.")
        result = a_val.get_value < b_val.get_value
        return Expression("Boolean", result, attributes=(Atom,))


class GreaterThan(Expression):
    """
    GreaterThan(a, b)
    Compares two values for greater-than.
    Supports Integer, Number, and Float symbols.
    Returns a Boolean expression.
    """
    def __init__(self, tail: tuple[BaseElement]):
        super().__init__(head=GreaterThan, tail=tail, attributes=(Executable,))

    def evaluate(self) -> Expression:
        a_val = self._tail[0]
        b_val = self._tail[1]

        _valid_types = (Integer, Number, Float)

        if a_val.get_head not in _valid_types or b_val.get_head not in _valid_types:
            raise TypeError("GreaterThan operation only supports Integer, Number, and Float symbols.")
        result = a_val.get_value > b_val.get_value
        return Expression("Boolean", result, attributes=(Atom,))
