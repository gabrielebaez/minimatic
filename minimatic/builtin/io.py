from core.expression import Expression, BaseElement
from core.evaluation import Context
from builtin.symbols import (
    Integer, Number, Float, Executable, Atom,
    IntegerSymbol, NumberSymbol, FloatSymbol
)

class Print(Expression):
    """
    Print(a, b, ...)
    Prints all arguments to the console.
    Supports any type of symbols.
    Returns an Expression with head 'Null'.
    """
    def __init__(self, tail: tuple[BaseElement]):
        super().__init__(head=Print, tail=tail, attributes=(Executable,))
    
    def evaluate(self, _) -> Expression:
        output = ' '.join(str(element.tail) for element in self._tail)
        print(output)
        return Expression("Null", None, attributes=(Atom,))