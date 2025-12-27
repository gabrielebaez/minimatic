"""
## Variables & Scope

- let(name, value, body)              # local binding
- def(name, params, body)             # function definition
- call(function, args...)
"""

from core.expression import Expression
from builtin.symbols import Atom, Expr, Executable

# Variable binding
class LetBinding(Expression):
    def __init__(self, name: str, value: Expression, body: Expression):
        super().__init__(head="Let", tail=(name, value, body), attributes=(Expr, Executable))


# Function definition
class DefBinding(Expression):
    def __init__(self, name: str, params: tuple, body: Expression):
        super().__init__(head="Def", tail=(name, params, body), attributes=(Expr, Executable))


# Function call
class CallExpression(Expression):
    def __init__(self, function: Expression, args: tuple):
        super().__init__(head="Call", tail=(function, *args), attributes=(Expr, Executable))
