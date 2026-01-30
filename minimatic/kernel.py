
from typing import Optional
from core.base_element import (Context, Symbol, 
                               Literal, Expression, 
                               BaseElement, EvaluationError)

ctx = Context()


class Kernel:
    def __init__(self, 
                 ctx: Optional[Context] = None) -> None:
        self.ctx = ctx if ctx else Context()

    def evaluate(self, expr: BaseElement):
        return expr.evaluate(self.ctx)