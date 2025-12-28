"""
## Control Flow

- If(condition, then_expr, else_expr)
- While(condition, body)
- Seq(expr1, expr2, ...)              # sequential execution
"""

from core.expression import Expression
from builtin.symbols import Atom, Expr, Executable


class If(Expression):
    def __init__(self, 
                 condition: Expression, 
                 then_expr: Expression, 
                 else_expr: Expression):
        super().__init__(head=If, 
                         tail=(condition, then_expr, else_expr), 
                         attributes=(Expr, Executable))
        
        def evaluate(self, context) -> Expression:
            condition_expr = self._tail[0].evaluate(context)
            if condition_expr.tail:  # Assuming the condition evaluates to a boolean-like value
                return self._tail[1].evaluate(context)
            else:
                return self._tail[2].evaluate(context)


class While(Expression):
    def __init__(self, condition: Expression, body: Expression):
        super().__init__(head="While", 
                         tail=(condition, body), 
                         attributes=(Expr, Executable))


class Seq(Expression):
    def __init__(self, *exprs: Expression):
        super().__init__(head="Seq", 
                         tail=tuple(exprs), 
                         attributes=(Expr, Executable))