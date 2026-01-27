from core.base_element import BaseElement, Context, Expression, Literal
from typing import Callable, Optional


class Plus(Expression):
    """
    Plus(a, b, ...)
    Sum all subsequent numeric arguments from the first.
    Supports Integer, Number, and Float symbols.
    Returns an Expression with the appropriate numeric type.
    """
    ...


class Subtracts(Expression):
    """
    Subtracts(a, b, ...)
    Subtracts all subsequent numeric arguments from the first.
    Supports Integer, Number, and Float symbols.
    Returns an Expression with the appropriate numeric type.
    """
    ...


class Times(Expression):
    """
    Times(a, b, ...)
    Multiplies all numeric arguments.
    Supports Integer, Number, and Float symbols.
    Returns an Expression with the appropriate numeric type.
    """
    ...


class Divide(Expression):
    """
    Divide(a, b, ...)
    Divides the first numeric argument by all subsequent ones.
    Supports Integer, Number, and Float symbols.
    Returns an Expression with the appropriate numeric type.
    """
    ...
