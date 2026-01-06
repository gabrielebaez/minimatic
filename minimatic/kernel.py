from core.base_element import Symbol, Literal, Expression
from core.evaluation import Context
from builtin.heads import Integer, Float, Number, Bool
from builtin.arithmetic import Plus
from builtin.core import If
from copy import copy, deepcopy
from typing import Dict, Any

context = Context()


a = Literal(Integer, -23)
b = Literal(Float, 24.34)
c = Literal(Number, 12)

expr = Plus(a,b,c)

expr_if = If(Plus(a,b), Literal(Bool, True), Literal(Bool, False))
print(expr_if, expr_if.evaluate(context=context))
print(expr)
print(expr.evaluate(context))


# ============================================================================
# BASIC CONSTRUCTION
# ============================================================================

# Simple expression: Plus(1, 2)
expr1 = Plus(Literal(Integer, 1), Literal(Integer,2))
print(expr1)  # Plus(1, 2)

# Nested expression: Times(2, Plus(3, 4))
expr2 = Expression("Times", Literal(Integer,2), 
                   Expression("Plus", Literal(Integer,3), Literal(Integer,4)))
print(expr2)  # Times(2, Plus(3, 4))

# Expression with no arguments
expr3 = Expression("Pi")
print(expr3)  # Pi()


# ============================================================================
# SEQUENCE PROTOCOL (iteration, length, indexing)
# ============================================================================

expr = Expression("Plus", Literal(Integer, 1), Literal(Integer, 2), Literal(Integer, 3))

# __len__: Get number of arguments
print(len(expr))  # 3

# __getitem__: Access individual arguments by index
print(expr[0])  # 1
print(expr[1])  # 2
print(expr[-1])  # 3 (negative indexing supported)

# __iter__: Iterate over arguments
for arg in expr:
    print(arg)  # 1, then 2, then 3

# __contains__: Check if argument exists
print(Literal(Integer, 2) in expr)  # True
print(Literal(Integer, 5) in expr)  # False


# ============================================================================
# EQUALITY AND HASHING
# ============================================================================

expr_a = Expression("Plus", Literal(Integer, 1), Literal(Integer, 2))
expr_b = Expression("Plus", Literal(Integer, 1), Literal(Integer, 2))
expr_c = Expression("Plus", Literal(Integer, 2), Literal(Integer, 1))

# __eq__: Check equality
print(expr_a == expr_b)  # True (same structure and values)
print(expr_a == expr_c)  # False (different argument order)

# __hash__: Use as dictionary key or in sets
expr_dict = {expr_a: "my_expression"}
print(expr_dict[expr_a])  # "my_expression" (expr_a and expr_b hash the same)

unique_exprs = {expr_a, expr_b, expr_c}
print(len(unique_exprs))  # 2 (expr_a and expr_b are considered the same)

# ============================================================================
# COPYING
# ============================================================================

original = Expression("Times", Literal(Integer, 2), Literal(Integer, 3))

# __copy__: Shallow copy
shallow = copy(original)
print(shallow == original)  # True
print(shallow is original)  # False (different objects)

# __deepcopy__: Deep copy (useful for nested expressions)
nested = Expression("Plus", Literal(Integer, 1), 
                   Expression("Times", Literal(Integer, 2), Literal(Integer, 3)))
deep_copy = deepcopy(nested)
print(deep_copy == nested)  # True
print(deep_copy is nested)  # False

# Handles circular references gracefully
memo: Dict[Any, Any] = {}
deep_copy_with_memo = deepcopy(nested, memo)
print(id(nested) in memo)  # True


# ============================================================================
# PROPERTY ACCESSORS
# ============================================================================

expr = Expression("Power", Literal(Integer, 2), Literal(Integer, 3))

# head: Access the function/operator
print(expr.head)  # "Power"

# tail: Access all arguments as tuple
print(expr.tail)  # (Literal(Integer, 2), Literal(Integer, 3))

# ============================================================================
# STRUCTURAL REPLACEMENT
# ============================================================================

original = Expression("Plus", Literal(Integer, 1), Literal(Integer, 2))

# replace: Modify head
new_expr = original.replace(head="Times")
print(new_expr)  # Times(1, 2)
print(original)  # Plus(1, 2) (unchanged)

# replace: Modify tail
new_expr = original.replace(tail=(Literal(Integer, 10), Literal(Integer, 20)))
print(new_expr)  # Plus(10, 20)

# replace: Modify multiple components at once
new_expr = original.replace(
    head="Times",
    tail=(Literal(Integer, 5), Literal(Integer, 6))
)
print(new_expr)  # Times(5, 6)

# ============================================================================
# MAPPING OVER TAIL
# ============================================================================

expr = Expression("Plus", Literal(Integer, 1), Literal(Integer, 2), Literal(Integer, 3))

# map: Apply function to each argument
doubled = expr.map(lambda x: x if isinstance(x, Literal) 
                            else Literal(Integer, x.value * 2)) # type: ignore
print(doubled)  # Plus(2, 4, 6)
print(expr)    # Plus(1, 2, 3) (unchanged)

# map with nested expressions
expr = Expression("List", 
                  Expression("Plus", Literal(Integer, 1), Literal(Integer, 2)),
                  Expression("Times", Literal(Integer, 3), Literal(Integer, 4)))

# Increment each nested expression's first argument
def increment_first_arg(elem):
    if isinstance(elem, Expression):
        new_tail = (Literal(Integer, elem[0].value + 1),) + elem.tail[1:]
        return elem.replace(tail=new_tail)
    return elem

result = expr.map(increment_first_arg)
print(result)  # List(Plus(2, 2), Times(4, 4))

# ============================================================================
# EVALUATION
# ============================================================================

# evaluate: Normal expression
expr = Expression("Plus", Literal(Integer, 1), Literal(Integer, 2))
result = expr.evaluate(context)
print(result)
# Result depends on context implementation; tail is evaluated

# evaluate: Expression with BaseElement head
inner_expr = Expression("Plus", Literal(Integer, 1), Literal(Integer, 2))
compound = Expression(inner_expr, Literal(Integer, 3))
result = compound.evaluate(context)
print(result)
# Head and tail are both evaluated

# ============================================================================
# ERROR HANDLING
# ============================================================================

# Invalid head type
try:
    Expression(123, Literal(Integer, 1))  # TypeError: head must be BaseElement or str
except Exception as e:
    print(f"Error: {e}")

# Invalid tail element type
try:
    Expression("Plus", Literal(Integer, 1), "invalid")  # TypeError in runtime usage
except Exception as e:
    print(f"Error: {e}")

# ============================================================================
# STRING REPRESENTATION
# ============================================================================

expr = Expression("Function", Symbol("x"), Literal(Integer, 42))

# __repr__: Machine-readable representation
print(repr(expr))  # Function(x, 42)

# __str__: User-friendly representation (same as __repr__ here)
print(str(expr))  # Function(x, 42)
