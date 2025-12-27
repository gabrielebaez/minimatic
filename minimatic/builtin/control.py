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
        super().__init__(head="If", 
                         tail=(condition, then_expr, else_expr), 
                         attributes=(Expr, Executable))


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