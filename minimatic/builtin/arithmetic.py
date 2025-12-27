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
from core.attributes import Integer, Number, Float, Complex, Executable, Atom


class Plus(Expression):
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

class LessThan(Expression):
    def __init__(self, tail: tuple[BaseElement]):
        super().__init__(head=LessThan, tail=tail, attributes=(Executable,))

    def evaluate(self) -> Expression:
        a_val = self._tail[0].get_tail
        b_val = self._tail[1].get_tail

        if self._tail[0].get_head == Integer and self._tail[1].get_head == Integer:
            result = a_val < b_val
            return Expression(Integer, int(result), attributes=(Atom,))
        elif self._tail[0].get_head == Number and self._tail[1].get_head == Number:
            result = a_val < b_val
            return Expression(Number, int(result), attributes=(Atom,))
        elif self._tail[0].get_head == Float and self._tail[1].get_head == Float:
            result = a_val < b_val
            return Expression(Float, int(result), attributes=(Atom,))
        elif self._tail[0].get_head == Complex and self._tail[1].get_head == Complex:
            raise ValueError("Less-than comparison not supported for Complex numbers.")
        else:
            raise TypeError("LT operation only supports Integer, Number, and Float symbols.")