from core.base_element import BaseElement, Context, Expression, Literal
from builtin.heads import Integer, Number, Float
from typing import Callable, Optional


NUMERIC = (Integer, Number, Float)

from functools import reduce

def _fold_numeric(elements, reducer, identity, promote_float=False):
    def folder(state, element):
        total, result_type = state
        head, value = element.head, element.value

        if head == Integer:
            numeric = int(value)
            new_type = "Integer" if result_type in (None, "Integer") else result_type
        elif head == Number:
            numeric = float(value)
            new_type = "Float" if promote_float else "Number"
        elif head == Float:
            numeric = float(value)
            new_type = "Float"
        else:
            raise TypeError(f"Unsupported type '{head}'.")

        return reducer(total, numeric), new_type

    return reduce(folder, elements, (identity, None))


def _numeric_eval(self: Expression, head: str, reducer: Callable, context: Context|None):
    evaluated = self.evaluate_tail(context)
    numeric_parts = []
    symbolic_parts = []

    for element in evaluated:
        if isinstance(element, Literal) and element.head in (Integer, Number, Float):
            numeric_parts.append(element)
        else:
            symbolic_parts.append(element)

    total, result_type = _fold_numeric(
        numeric_parts,
        reducer=reducer,
        identity=0,
    )

    if result_type is not None:
        literal = (
            Literal(Integer, total) if result_type == "Integer"
            else Literal(Float, total) if result_type == "Float"
            else Literal(Number, total)
        )
        symbolic_parts.insert(0, literal)

    if len(symbolic_parts) == 1 and isinstance(symbolic_parts[0], Literal):
        return symbolic_parts[0]

    return Expression(head, *symbolic_parts)


class Plus(Expression):
    """
    Plus(a, b, ...)
    Sum all subsequent numeric arguments from the first.
    Supports Integer, Number, and Float symbols.
    Returns an Expression with the appropriate numeric type.
    """
    def __init__(self, *tail):
        super().__init__("Plus", *tail)

    def evaluate(self, context):
        return _numeric_eval(self, "Plus", lambda acc, val: acc + val, context)


class Subtracts(Expression):
    """
    Subtracts(a, b, ...)
    Subtracts all subsequent numeric arguments from the first.
    Supports Integer, Number, and Float symbols.
    Returns an Expression with the appropriate numeric type.
    """
    def __init__(self, *tail: BaseElement):
        super().__init__("Subtracts", *tail)
    
    def evaluate(self, context):
        return _numeric_eval(self, "Substracts", lambda acc, val: acc - val, context)


class Times(Expression):
    """
    Times(a, b, ...)
    Multiplies all numeric arguments.
    Supports Integer, Number, and Float symbols.
    Returns an Expression with the appropriate numeric type.
    """
    def __init__(self, *tail: tuple[BaseElement]):
        super().__init__(head="Times", *tail)

    def evaluate(self, context):
        return _numeric_eval(self, "Times", lambda acc, val: acc * val, context)


class Divide(Expression):
    """
    Divide(a, b, ...)
    Divides the first numeric argument by all subsequent ones.
    Supports Integer, Number, and Float symbols.
    Returns an Expression with the appropriate numeric type.
    """
    def __init__(self, *tail: BaseElement):
        super().__init__("Divide", *tail)

    def evaluate(self, context):
        return _numeric_eval(self, "Divide", lambda acc, val: acc / val, context)
