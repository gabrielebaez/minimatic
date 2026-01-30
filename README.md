# Minimatic EDSL

> ⚠️ **Project Status: Proof of Concept**
>
> Minimatic is currently in early active development. The **Expression Engine** is implemented and functional, but high-level interfaces (Kernel) and syntax parsing are not yet available. The API is subject to change.

Minimatic is a lightweight **Embedded Domain Specific Language (EDSL)** and symbolic computation engine written in Python. It provides a robust framework for building immutable expression trees, evaluating them within custom contexts, and extending the language with builtins and special forms.

## Architecture Overview

Minimatic is architected around a strictly typed, immutable Abstract Syntax Tree (AST) and a hybrid evaluation model. The design separates the definition of symbolic structures from the rules governing their evaluation, allowing for maximum flexibility.

### 1. The Abstract Syntax Tree (AST)

The core data model consists of three primary classes inheriting from `BaseElement`. This hierarchy ensures type safety and structural consistency throughout the system.

*   **`BaseElement`**: The abstract root interface defining behaviors like `evaluate()`, `__hash__`, and structural properties (`head`, `tail`).
*   **`Symbol`**: Represents an atomic variable name or identifier (e.g., `x`, `user_name`). It acts as a pointer to a value within a Context.
*   **`Literal`**: Represents a concrete Python value wrapped in the symbolic system (e.g., integers, strings). Literals evaluate to themselves.
*   **`Expression`**: The fundamental n-ary tree node. Every Expression consists of a **Head** (operator/function) and a **Tail** (arguments/operands).
    *   **Immutability**: Once constructed, an Expression cannot be changed. This allows for safe caching, thread safety, and reliable structural hashing.
    *   **Structure**: An expression like `Add(x, 5)` is an instance where `head='Add'` and `tail=(Symbol('x'), Literal(5))`.

### 2. The Context (Evaluation Environment)

Evaluation does not happen in a vacuum; it requires a `Context`. The Context serves as the lexical environment for the evaluation engine.

*   **Variable Storage**: Maps `Symbol` names to their current values.
*   **Builtin Registry**: Stores the Python functions and classes that implement the language's operations (e.g., how 'Add' actually performs addition).
*   **Scope Management**: The architecture is designed to support scoped copying (deep copying of variable states) via `context.copy()`, enabling recursive evaluation with isolated state.

### 3. The Hybrid Extension Model

Minimatic distinguishes between two fundamentally different types of operations: **Pure Functions** and **Special Forms**. This distinction is critical for handling the difference between mathematical eager evaluation and logical lazy evaluation.

#### A. Pure Builtins (Context Registration)
Standard operations (math, string manipulation) are implemented as external Python functions registered in the Context.

*   **Mechanism**: You define `def my_func(a, b): ...` and call `context.set('MyOp', my_func)`.
*   **Evaluation Strategy**: **Eager**. The engine evaluates all arguments in the `tail` *before* passing them to `my_func`.
*   **Constraints**: These functions cannot access the Context directly (stateless) and cannot prevent arguments from being evaluated.

#### B. Special Forms (Expression Subclassing)
Language features that require control flow, state mutation, or lazy evaluation are implemented by subclassing the `Expression` class itself.

*   **Mechanism**: You create `class MyControlFlow(Expression)` and override its `evaluate()` method.
*   **Evaluation Strategy**: **Lazy**. The implementation explicitly decides *when* (or if) to evaluate parts of the `tail`.
*   **Capabilities**: These forms have direct access to the `Context` object, allowing them to define variables (`Set`) or branch logic without evaluating unused paths (`If`).

## Project Status & Roadmap

See [docs/roadmap.md](docs/roadmap.md)

## Quick Start (Engine Level)

Since the Parser and Kernel are not yet available, you interact with Minimatic directly by constructing the AST in Python.

```python
from core.base_element import (Context, Symbol, 
                               Literal, Expression, 
                               BaseElement, EvaluationError)


# --- 1. Basic Construction ---

# Creating Literals
num = Literal(42)
text = Literal("Hello")
print(f"Literal: {num}")
print(f"Literal type: {num.head}")

# Creating Symbols
x = Symbol('x')
y = Symbol('y')
func_name = Symbol('Add')
print(f"Symbol: {x}")
print(f"Symbol hash: {hash(x)}")

# Creating Expressions (Tree structure)
# Represents: Add(x, 10)
expr1 = Expression('Add', x, Literal(10))
print(f"Expression: {expr1}")
print(f"Expression head: {expr1.head}")
print(f"Expression tail: {expr1.tail}")

# --- 2. Evaluation Strategy ---

ctx = Context()

# Define a custom Add function that works with our Literals
def add_func(a: BaseElement, b: BaseElement) -> BaseElement:
    # In a real system, we'd check types. Here we assume numeric Literals.
    val_a = a.value if isinstance(a, Literal) else str(a)
    val_b = b.value if isinstance(b, Literal) else str(a)
    return Literal(val_a + val_b)

def square_func(a: BaseElement) -> BaseElement:
    val = a.value if isinstance(a, Literal) else int(str(a))
    return Literal(val ** 2)

# Register functions in context
ctx.set('Add', add_func)
ctx.set('Square', square_func)

# Register variables
ctx.set('x', Literal(5))
ctx.set('y', Literal(3))

# Evaluate: Add(x, 10) where x=5 -> 15
try:
    result = expr1.evaluate(ctx)
    print(f"Evaluation of '{expr1}' with x=5: {result}")
except Exception as e:
    print(f"Error: {e}")

# Evaluate: Square(x) where x=5 -> 25
expr_square = Expression('Square', x)
print(f"Evaluation of '{expr_square}' with x=5: {expr_square.evaluate(ctx)}")

# --- 3. Nesting and Recursion ---

# Represents: Add(Square(x), y)
# Structure: Add( Square(x), y )
nested_expr = Expression('Add', Expression('Square', x), y)

print(f"Nested Expression: {nested_expr}")

# Evaluate: Square(5) + 3 -> 25 + 3 -> 28
result_nested = nested_expr.evaluate(ctx)
print(f"Evaluation result: {result_nested}")

# --- 4. Immutability and Hashability ---

# Expressions are immutable and hashable, making them safe for Sets/Dicts
expr_a = Expression('Add', x, y)
expr_b = Expression('Add', x, y)
expr_c = Expression('Add', y, x) # Different structure

print(f"expr_a == expr_b: {expr_a == expr_b}") # True
print(f"expr_a == expr_c: {expr_a == expr_c}") # False
print(f"hash(expr_a) == hash(expr_b): {hash(expr_a) == hash(expr_b)}")

# Using as dictionary keys
expression_map = {
    expr_a: "Sum of x and y",
    Expression('Square', x): "x squared"
}
print(f"Lookup '{expr_a}' in map: {expression_map.get(expr_a)}")

# --- 5. Structural Operations ---

# Create a list of elements
list_expr = Expression.list_of(x, y, Literal(10))
print(f"Original List: {list_expr}")

# Map: Add 1 to every literal in the tail
def incrementor(elem):
    if isinstance(elem, Literal) and isinstance(elem.value, (int, float)):
        return Literal(elem.value + 1)
    return elem

new_list = list_expr.map(incrementor)
print(f"Mapped List (incremented literals): {new_list}")

# Replace: Change the head of the expression
replaced_head = list_expr.replace(head="Vector")
print(f"Replaced Head (List -> Vector): {replaced_head}")

# --- 6. Error Handling ---

# Case A: Undefined Symbol
z_expr = Expression('Add', Symbol('undefined_var'), Literal(1))
try:
    z_expr.evaluate(ctx)
except KeyError as e:
    print(f"Caught KeyError: {e}")
except EvaluationError as e:
    print(f"Caught EvaluationError: {e}")

# Case B: Function Application Failure
# Creating a function that requires 2 args but passing 1
def strict_add(a, b):
    return Literal(a.value + b.value)

ctx.set('StrictAdd', strict_add)
bad_expr = Expression('StrictAdd', x) # Missing 'y'

try:
    bad_expr.evaluate(ctx)
except EvaluationError as e:
    print(f"Caught EvaluationError: {e}")

# --- 7. Factory Methods and Callable Interface ---

# Using callable syntax
my_expr = Expression('Add', x, y)
result_callable = my_expr(ctx)
print(f"Using expr(context) syntax: {result_callable}")

# Using From Function factory
factory_expr = Expression.from_function('Multiply', Literal(2), Literal(3))
ctx.set('Multiply', lambda a, b: Literal(a.value * b.value))
print(f"Factory result: {factory_expr.evaluate(ctx)}")
```
