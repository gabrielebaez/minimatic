from core.expression import Expression
from core.base_element import BaseElement
from core.attributes import Atom
from typing import Any


class Atom(Expression):
    def __init__(self, head: str|BaseElement, value: Any):
        super().__init__(head=head, tail=value, attributes=(Atom,))


class NumberSymbol(Expression):
    def __init__(self, value: float):
        super().__init__(head="Number", tail=value, attributes=(Atom,))


class IntegerSymbol(Expression):
    def __init__(self, value: int):
        super().__init__("Integer", value, attributes=(Atom,))


class FloatSymbol(Expression):
    def __init__(self, value: float):
        super().__init__(head="Float", tail=value, attributes=(Atom,))


class StringSymbol(Expression):
    def __init__(self, value: str):
        super().__init__(head="String", tail=value, attributes=(Atom,))
