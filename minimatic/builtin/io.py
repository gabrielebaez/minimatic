from core.expression import Expression, BaseElement
from core.evaluation import Context


class Print(Expression):
    """
    Print(a, b, ...)
    Prints all arguments to the console.
    Supports any type of symbols.
    Returns an Expression with head 'Null'.
    """
    pass