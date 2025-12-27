"""
## Data Structures

- list(item1, item2, ...)
- get(collection, index)
- set(collection, index, value)
- len(collection)
- append(collection, item)

## Iteration

- map(function, collection)
- filter(function, collection)
- reduce(function, collection, initial)
"""

from core.expression import Expression
from builtin.symbols import Atom, Expr, Executable


# Tabular structure
class Tabular(Expression):
    def __init__(self, 
                 rows: Expression, 
                 columns: Expression):
        super().__init__(head="Tabular", tail=(rows, columns), attributes=(Atom,))


# List creation
class ListExpression(Expression):
    def __init__(self, *items: Expression):
        super().__init__(head="List", tail=items, attributes=(Atom,))


# Get element
class Get(Expression):
    def __init__(self, 
                 collection: Expression, 
                 index: Expression):
        super().__init__(head="Get", tail=(collection, index), attributes=(Executable,))


# Set element
class Set(Expression):
    def __init__(self, 
                 collection: Expression, 
                 index: Expression, 
                 value: Expression):
        super().__init__(head="Set", 
                         tail=(collection, index, value), 
                         attributes=(Executable,))


# Get length
class Len(Expression):
    def __init__(self, collection: Expression):
        super().__init__(head="Len", 
                         tail=(collection,), 
                         attributes=(Executable,))


# Append element
class Append(Expression):
    def __init__(self, 
                 collection: Expression, 
                 item: Expression):
        super().__init__(head="Append", 
                         tail=(collection, item), 
                         attributes=(Executable,))
