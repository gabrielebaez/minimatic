from core.expression import Expression
from typing import Any


# Symbol heads
Integer = "Integer"
Number = "Number"
Float = "Float"
String = "String"

# Symbol types
Atom = "Atom"
Expr = "Expr"
Executable = "Executable"


class AtomSymbol(Expression):
    def __init__(self, head: str, value: Any):
        super().__init__(head=head, tail=value, attributes=(Atom,))


class IntegerSymbol(Expression):
    def __init__(self, value: int):
        super().__init__(head=Integer, tail=value, attributes=(Atom,))


class FloatSymbol(Expression):
    def __init__(self, value: float):
        super().__init__(head=Float, tail=value, attributes=(Atom,))


class StringSymbol(Expression):
    def __init__(self, value: str):
        super().__init__(head=String, tail=value, attributes=(Atom,))
