from copy import copy, deepcopy
from core.expression import Expression
from core.base_element import BaseElement

# Assuming these exist or are mocked
class Integer(BaseElement):
    def __init__(self, value):
        self.value = value
    def evaluate(self, context=None):
        return self
    def __repr__(self):
        return str(self.value)
    def __eq__(self, other):
        return isinstance(other, Integer) and self.value == other.value
    def __hash__(self):
        return hash(self.value)

class Variable(BaseElement):
    def __init__(self, name):
        self.name = name
    def evaluate(self, context=None):
        return self
    def __repr__(self):
        return self.name
    def __eq__(self, other):
        return isinstance(other, Variable) and self.name == other.name
    def __hash__(self):
        return hash(self.name)

class MockContext:
    pass

# ============================================================================
# BASIC CONSTRUCTION
# ============================================================================

# Simple expression: Plus(1, 2)
expr1 = Expression("Plus", Integer(1), Integer(2))
print(expr1)  # Plus(1, 2)

# Nested expression: Times(2, Plus(3, 4))
expr2 = Expression("Times", Integer(2), 
                   Expression("Plus", Integer(3), Integer(4)))
print(expr2)  # Times(2, Plus(3, 4))

# Expression with no arguments
expr3 = Expression("Pi")
print(expr3)  # Pi()

# ============================================================================
# SEQUENCE PROTOCOL (iteration, length, indexing)
# ============================================================================

expr = Expression("Plus", Integer(1), Integer(2), Integer(3))

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
print(Integer(2) in expr)  # True
print(Integer(5) in expr)  # False

# ============================================================================
# EQUALITY AND HASHING
# ============================================================================

expr_a = Expression("Plus", Integer(1), Integer(2))
expr_b = Expression("Plus", Integer(1), Integer(2))
expr_c = Expression("Plus", Integer(2), Integer(1))

# __eq__: Check equality
print(expr_a == expr_b)  # True (same structure and values)
print(expr_a == expr_c)  # False (different argument order)

# __hash__: Use as dictionary key or in sets
expr_dict = {expr_a: "my_expression"}
print(expr_dict[expr_b])  # "my_expression" (expr_a and expr_b hash the same)

unique_exprs = {expr_a, expr_b, expr_c}
print(len(unique_exprs))  # 2 (expr_a and expr_b are considered the same)

# ============================================================================
# COPYING
# ============================================================================

original = Expression("Times", Integer(2), Integer(3))

# __copy__: Shallow copy
shallow = copy(original)
print(shallow == original)  # True
print(shallow is original)  # False (different objects)

# __deepcopy__: Deep copy (useful for nested expressions)
nested = Expression("Plus", Integer(1), 
                   Expression("Times", Integer(2), Integer(3)))
deep_copy = deepcopy(nested)
print(deep_copy == nested)  # True
print(deep_copy is nested)  # False

# Handles circular references gracefully
memo = {}
deep_copy_with_memo = deepcopy(nested, memo)
print(id(nested) in memo)  # True

# ============================================================================
# ATTRIBUTE MANIPULATION
# ============================================================================

expr = Expression("Sin", Variable("x"))

# has_attribute: Check if attribute exists
print(expr.has_attribute("HoldAll"))  # False

# add_attribute: Add attribute (returns new Expression)
expr_with_hold = expr.add_attribute("HoldAll")
print(expr_with_hold.has_attribute("HoldAll"))  # True
print(expr.has_attribute("HoldAll"))  # False (original unchanged)

# Multiple attributes
expr_multi = expr.add_attribute("HoldAll").add_attribute("Protected")
print(expr_multi.attributes)  # ("HoldAll", "Protected")

# remove_attribute: Remove attribute (returns new Expression)
expr_removed = expr_multi.remove_attribute("HoldAll")
print(expr_removed.attributes)  # ("Protected",)

# Adding duplicate attribute does nothing
expr_again = expr_with_hold.add_attribute("HoldAll")
print(expr_again is expr_with_hold)  # True (returns same object)

# ============================================================================
# PROPERTY ACCESSORS
# ============================================================================

expr = Expression("Power", Integer(2), Integer(3), attributes=("Protected",))

# head: Access the function/operator
print(expr.head)  # "Power"

# tail: Access all arguments as tuple
print(expr.tail)  # (Integer(2), Integer(3))

# attributes: Access attribute tuple
print(expr.attributes)  # ("Protected",)

# ============================================================================
# STRUCTURAL REPLACEMENT
# ============================================================================

original = Expression("Plus", Integer(1), Integer(2))

# replace: Modify head
new_expr = original.replace(head="Times")
print(new_expr)  # Times(1, 2)
print(original)  # Plus(1, 2) (unchanged)

# replace: Modify tail
new_expr = original.replace(tail=(Integer(10), Integer(20)))
print(new_expr)  # Plus(10, 20)

# replace: Modify attributes
new_expr = original.replace(attributes=("HoldAll",))
print(new_expr.attributes)  # ("HoldAll",)

# replace: Modify multiple components at once
new_expr = original.replace(
    head="Times",
    tail=(Integer(5), Integer(6)),
    attributes=("Protected",)
)
print(new_expr)  # Times(5, 6)
print(new_expr.attributes)  # ("Protected",)

# ============================================================================
# MAPPING OVER TAIL
# ============================================================================

expr = Expression("Plus", Integer(1), Integer(2), Integer(3))

# map: Apply function to each argument
doubled = expr.map(lambda x: x if isinstance(x, Variable) 
                            else Integer(x.value * 2))
print(doubled)  # Plus(2, 4, 6)
print(expr)    # Plus(1, 2, 3) (unchanged)

# map with nested expressions
expr = Expression("List", 
                  Expression("Plus", Integer(1), Integer(2)),
                  Expression("Times", Integer(3), Integer(4)))

# Increment each nested expression's first argument
def increment_first_arg(elem):
    if isinstance(elem, Expression):
        new_tail = (Integer(elem[0].value + 1),) + elem.tail[1:]
        return elem.replace(tail=new_tail)
    return elem

result = expr.map(increment_first_arg)
print(result)  # List(Plus(2, 2), Times(4, 4))

# ============================================================================
# EVALUATION
# ============================================================================

context = MockContext()

# evaluate: Atom attribute prevents evaluation
atom_expr = Expression("Plus", Integer(1), Integer(2), attributes=("Atom",))
result = atom_expr.evaluate(context)
print(result == atom_expr)  # True (returned unevaluated)

# evaluate: HoldAll attribute prevents evaluation
held_expr = Expression("Sin", Variable("x"), attributes=("HoldAll",))
result = held_expr.evaluate(context)
print(result == held_expr)  # True (returned unevaluated)

# evaluate: Normal expression (without attributes)
expr = Expression("Plus", Integer(1), Integer(2))
result = expr.evaluate(context)
# Result depends on context implementation; tail is evaluated

# evaluate: Expression with BaseElement head
inner_expr = Expression("Plus", Integer(1), Integer(2))
compound = Expression(inner_expr, Integer(3))
result = compound.evaluate(context)
# Head and tail are both evaluated

# ============================================================================
# ERROR HANDLING
# ============================================================================

# Invalid head type
try:
    Expression(123, Integer(1))  # TypeError: head must be BaseElement or str
except TypeError as e:
    print(f"Error: {e}")

# Invalid tail element type
try:
    Expression("Plus", Integer(1), "invalid")  # TypeError in runtime usage
except TypeError as e:
    print(f"Error: {e}")

# ============================================================================
# CHAINING OPERATIONS
# ============================================================================

# Combine multiple operations
expr = (Expression("Plus", Integer(1), Integer(2))
        .add_attribute("Protected")
        .add_attribute("HoldAll")
        .replace(tail=(Integer(5), Integer(6)))
        .remove_attribute("Protected"))

print(expr)  # Plus(5, 6)
print(expr.attributes)  # ("HoldAll",)

# ============================================================================
# STRING REPRESENTATION
# ============================================================================

expr = Expression("Function", Variable("x"), Integer(42))

# __repr__: Machine-readable representation
print(repr(expr))  # Function(x, 42)

# __str__: User-friendly representation (same as __repr__ here)
print(str(expr))  # Function(x, 42)
