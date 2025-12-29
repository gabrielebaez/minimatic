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
from core.attributes import Atom, Function


# Tabular structure
class Tabular(Expression):
    pass


# Get element
class Get(Expression):
    pass


# Set element
class Set(Expression):
    pass


# Get length
class Len(Expression):
    pass


# Append element
class Append(Expression):
    pass