"""
## Variables & Scope

- Let(name, value, body)         # local binding
- Block([vars], body)            # block scope
- Module([vars], body)           # module scope
- Def(name, [params], body)      # function definition
"""

from core.expression import Expression
from core.evaluation import Context
from builtin.symbols import Atom, Expr, Executable


class Let(Expression):
    def __init__(self, 
                 name: Expression, 
                 value: Expression, 
                 body: Expression, 
                 attributes = ...):
        super().__init__(head="Let", 
                         tail=(name, value, body), 
                         attributes=attributes)

    def evaluate(self, context: Context):
        pass


class Block(Expression):
    def __init__(self, 
                 vars: list[Expression], 
                 body: Expression, 
                 attributes = ...):
        super().__init__(head="Block", 
                         tail=(vars, body), 
                         attributes=attributes)

    def evaluate(self, context: Context):
        pass


class Module(Expression):
    def __init__(self, 
                 vars: list[Expression], 
                 body: Expression, 
                 attributes = ...):
        super().__init__(head="Module", 
                         tail=(vars, body), 
                         attributes=attributes)

    def evaluate(self, context: Context):
        pass


class Def(Expression):
    def __init__(self, 
                 name: Expression, 
                 params: list[Expression], 
                 body: Expression, 
                 attributes = ...):
        super().__init__(head="Def", 
                         tail=(name, params, body), 
                         attributes=attributes)

    def evaluate(self, context: Context):
        pass