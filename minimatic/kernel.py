from typing import Any
from core.expression import Expression
from core.evaluation import Context
from core.attributes import Atom
from builtin.arithmetic import Plus


# ============================================================================
# 1. BASIC CONSTRUCTION
# ============================================================================

# Simple expressions with string heads
add_expr = Expression("Plus", 2, 3)
multiply_expr = Expression("Times", 5, 4)

# Nested expressions
nested = Expression("Plus", Expression("Times", 2, 3), 4)

# Expression with no tail
symbol = Expression("x")

print("=== CONSTRUCTION ===")
print(f"add_expr: {add_expr}")
print(f"multiply_expr: {multiply_expr}")
print(f"nested: {nested}")
print(f"symbol: {symbol}")


# ============================================================================
# 2. STRING REPRESENTATIONS
# ============================================================================

print("\n=== STRING REPRESENTATIONS ===")
print(f"repr(add_expr): {repr(add_expr)}")
print(f"str(add_expr): {str(add_expr)}")
print(f"repr(nested): {repr(nested)}")


# ============================================================================
# 3. SEQUENCE PROTOCOL
# ============================================================================

print("\n=== SEQUENCE PROTOCOL ===")

# __len__: get number of arguments
print(f"len(add_expr): {len(add_expr)}")  # 2
print(f"len(symbol): {len(symbol)}")      # 0

# __getitem__: access arguments by index
print(f"add_expr[0]: {add_expr[0]}")      # 2
print(f"add_expr[1]: {add_expr[1]}")      # 3

# __iter__: iterate over arguments
print(f"Elements in add_expr: {list(add_expr)}")  # [2, 3]

# Iterate over nested expression
print(f"Elements in nested: {list(nested)}")  # [Plus(2, 3), 4]


# ============================================================================
# 4. EQUALITY AND HASHING
# ============================================================================

print("\n=== EQUALITY AND HASHING ===")

expr1 = Expression("Plus", 2, 3)
expr2 = Expression("Plus", 2, 3)
expr3 = Expression("Plus", 3, 2)
expr4 = Expression("Times", 2, 3)

print(f"expr1 == expr2: {expr1 == expr2}")  # True (same structure)
print(f"expr1 == expr3: {expr1 == expr3}")  # False (different argument order)
print(f"expr1 == expr4: {expr1 == expr4}")  # False (different head)

# Use in sets and dicts (via hashing)
expr_set = {expr1, expr2, expr3}
print(f"Set of 3 expressions: {len(expr_set)} unique")  # 2 unique (expr1 and expr2 are identical)

expr_dict = {expr1: "addition", expr4: "multiplication"}
print(f"expr_dict[expr2]: {expr_dict[expr2]}")  # "addition" (expr2 hashes to same as expr1)


# ============================================================================
# 5. ATTRIBUTE MANIPULATION
# ============================================================================

print("\n=== ATTRIBUTE MANIPULATION ===")

# Create expression without attributes
plain_expr = Expression("f", 1, 2)
print(f"plain_expr.attributes: {plain_expr.attributes}")  # ()

# Check for attribute
print(f"plain_expr.has_attribute('Hold'): {plain_expr.has_attribute('Hold')}")  # False

# Add an attribute
held_expr = plain_expr.add_attribute("Hold")
print(f"held_expr.attributes: {held_expr.attributes}")  # ('Hold',)
print(f"held_expr.has_attribute('Hold'): {held_expr.has_attribute('Hold')}")  # True

# Add multiple attributes
exec_held = held_expr.add_attribute("Executable")
print(f"exec_held.attributes: {exec_held.attributes}")  # ('Hold', 'Executable')

# Adding duplicate attribute returns self (no change)
exec_held_2 = exec_held.add_attribute("Executable")
print(f"exec_held is exec_held_2: {exec_held is exec_held_2}")  # True

# Remove an attribute
no_hold = exec_held.remove_attribute("Hold")
print(f"no_hold.attributes: {no_hold.attributes}")  # ('Executable',)

# Remove non-existent attribute (no error, just returns new expression)
still_no_hold = no_hold.remove_attribute("Hold")
print(f"still_no_hold.attributes: {still_no_hold.attributes}")  # ('Executable',)


# ============================================================================
# 6. PROPERTY ACCESSORS
# ============================================================================

print("\n=== PROPERTY ACCESSORS ===")

example = Expression("MyFunc", "a", "b", "c", attributes=("Attr1", "Attr2"))

print(f"example.head: {example.head}")           # MyFunc
print(f"example.tail: {example.tail}")           # ('a', 'b', 'c')
print(f"example.attributes: {example.attributes}")  # ('Attr1', 'Attr2')


# ============================================================================
# 7. STRUCTURAL SUBSTITUTION (replace)
# ============================================================================

print("\n=== STRUCTURAL SUBSTITUTION ===")

original = Expression("Plus", 10, 20, attributes=("Attr1",))

# Replace head only
replaced_head = original.replace(head="Minus")
print(f"replaced_head: {replaced_head}")  # Minus(10, 20)
print(f"replaced_head.attributes: {replaced_head.attributes}")  # ('Attr1',)

# Replace tail only
replaced_tail = original.replace(tail=(5, 15))
print(f"replaced_tail: {replaced_tail}")  # Plus(5, 15)
print(f"replaced_tail.attributes: {replaced_tail.attributes}")  # ('Attr1',)

# Replace attributes only
replaced_attrs = original.replace(attributes=("NewAttr",))
print(f"replaced_attrs: {replaced_attrs}")  # Plus(10, 20)
print(f"replaced_attrs.attributes: {replaced_attrs.attributes}")  # ('NewAttr',)

# Replace everything
replaced_all = original.replace(
    head="Times",
    tail=(2, 3),
    attributes=("Attr1", "Attr2")
)
print(f"replaced_all: {replaced_all}")  # Times(2, 3)
print(f"replaced_all.attributes: {replaced_all.attributes}")  # ('Attr1', 'Attr2')


# ============================================================================
# 8. MAPPING (map)
# ============================================================================

print("\n=== MAPPING ===")

expr = Expression("List", 1, 2, 3)

# Double each element
doubled = expr.map(lambda x: x * 2)
print(f"doubled: {doubled}")  # List(2, 4, 6)

# Square each element
squared = expr.map(lambda x: x ** 2)
print(f"squared: {squared}")  # List(1, 4, 9)

# Map with nested expressions
nested_expr = Expression("Container",
                         Expression("Item", 1),
                         Expression("Item", 2))

# Map to extract just the head
heads_only = nested_expr.map(lambda x: x.head if isinstance(x, Expression) else x)
print(f"heads_only: {heads_only}")  # Container(Item, Item)


# ============================================================================
# 9. EVALUATION (evaluate)
# ============================================================================

print("\n=== EVALUATION ===")

# 9a. Hold attribute - prevents evaluation
hold_expr = Expression("Plus", 2, 3, attributes=("Hold",))
result = hold_expr.evaluate()
print(f"Hold expression evaluates to itself: {result is hold_expr}")  # True

# 9b. No Executable attribute - returns unevaluated
plain = Expression("Plus", 2, 3)  # No "Executable" attribute
result = plain.evaluate()
print(f"Non-executable expression: {result is plain}")  # True

# 9c. Callable head with Executable attribute
def add(*args):
    return sum(args)

exec_expr = Expression(add, 2, 3, attributes=("Executable",))
result = exec_expr.evaluate()
print(f"Callable head result: {result}")  # 5

# 9d. Nested evaluation with Executable
def multiply(x, y):
    return x * y

inner_expr = Expression(add, 1, 2, attributes=("Executable",))
outer_expr = Expression(multiply, inner_expr, 10, attributes=("Executable",))
result = outer_expr.evaluate()
print(f"Nested evaluation: {result}")  # 30 (add(1,2) = 3, multiply(3, 10) = 30)

# 9e. String head with Executable (evaluates tail, returns expression)
exec_string_head = Expression("Print", 
                              Expression(add, 5, 5, attributes=("Executable",)),
                              attributes=("Executable",))
result = exec_string_head.evaluate()
print(f"String head result: {result}")  # Print(10)

# 9f. Evaluation failure gracefully degrades
def faulty_op(x):
    raise ValueError("Oops!")

faulty = Expression(faulty_op, 10, attributes=("Executable",))
result = faulty.evaluate()
print(f"Failed evaluation returns expression: {isinstance(result, Expression)}")  # True


# ============================================================================
# 10. VALIDATION (Executable attribute requires callable head)
# ============================================================================

print("\n=== VALIDATION ===")

# This raises TypeError
try:
    bad_expr = Expression("NotCallable", 1, 2, attributes=("Executable",))
except TypeError as e:
    print(f"Constructor validation: {e}")

# This also raises TypeError when using replace
try:
    expr = Expression("SomeHead", 1, 2)
    bad_replace = expr.replace(head="NotCallable", attributes=("Executable",))
except TypeError as e:
    print(f"Replace validation: {e}")


# ============================================================================
# 11. IMMUTABILITY DEMONSTRATION
# ============================================================================

print("\n=== IMMUTABILITY ===")

original = Expression("f", 1, 2)
modified = original.add_attribute("MyAttr")

print(f"original is modified: {original is modified}")  # False
print(f"original.attributes: {original.attributes}")  # ()
print(f"modified.attributes: {modified.attributes}")  # ('MyAttr',)

# Tail and head are not modified
print(f"original.tail: {original.tail}")  # (1, 2)
print(f"modified.tail: {modified.tail}")  # (1, 2)


# ============================================================================
# 12. COMPLEX EXAMPLE: SYMBOLIC MATH EXPRESSION
# ============================================================================

print("\n=== COMPLEX EXAMPLE: SYMBOLIC MATH ===")

# Build: (2 * 3) + (4 * 5)
two_times_three = Expression("Times", 2, 3, attributes=("Executable",))
four_times_five = Expression("Times", 4, 5, attributes=("Executable",))
full_expr = Expression("Plus", two_times_three, four_times_five, attributes=("Executable",))

print(f"Expression: {full_expr}")

# Define actual operations
import operator
expr_with_ops = Expression(
    operator.add,
    Expression(operator.mul, 2, 3, attributes=("Executable",)),
    Expression(operator.mul, 4, 5, attributes=("Executable",)),
    attributes=("Executable",)
)

result = expr_with_ops.evaluate()
print(f"Evaluated result: {result}")  # 26

# Hold one part for inspection
held_version = full_expr.add_attribute("Hold")
held_result = held_version.evaluate()
print(f"Held expression returns itself: {held_result is held_version}")  # True
