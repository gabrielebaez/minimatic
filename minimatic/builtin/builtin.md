# Extending the Language: Builtins & Special Forms

This guide explains how to extend the symbolic language with new operations. There are two primary methods for integrating custom logic: **Context Registration** (for pure functions) and **Expression Subclassing** (for control flow and state management).

## Method 1: Context Registration (Pure Functions)

This method involves defining a standard Python function and registering it in the evaluation context. The `Expression` class will look up the function by name (the "head" of the expression) and execute it.

### How it Works

When an expression's head is a string (e.g., `'Add'`), the evaluator looks up that string in the `Context`. It then calls the retrieved Python function, passing the **evaluated** tail elements as arguments.

### Implementation Steps

1.  Define a Python function that accepts `BaseElement` arguments.
2.  Extract the underlying values from `Literal` objects or handle other `BaseElement` types as needed.
3.  Return a new `BaseElement` (usually a `Literal` or a new `Expression`).
4.  Register the function in the context using `context.set('Name', function)`.

### Example: Implementing a `Multiply` Builtin

```python
def multiply_func(a: BaseElement, b: BaseElement) -> BaseElement:
    """
    Python function that performs multiplication.
    Assumes arguments are evaluated Literals containing numbers.
    """
    # Extract Python values from the DSL wrapper
    val_a = a.value if isinstance(a, Literal) else 0
    val_b = b.value if isinstance(b, Literal) else 0
    
    # Return a new Literal wrapping the result
    return Literal(val_a * val_b)

# Register in context
ctx = Context()
ctx.set('Multiply', multiply_func)

# Usage: Multiply(5, 2) -> 10
expr = Expression('Multiply', Literal(5), Literal(2))
print(expr.evaluate(ctx))  # Output: 10
```

### Characteristics

-   **Evaluation Strategy**: **Eager**. All arguments (the tail) are fully evaluated *before* your function is called.
-   **Context Access**: **None**. The function only receives the evaluated arguments; it does not receive the `Context` object.
-   **State**: **Immutable**. These functions should be pure and cannot modify the variables stored in the context.

---

## Method 2: Expression Subclassing (Special Forms)

This method involves creating a new class that inherits from `Expression`. You override the `evaluate()` method to implement custom logic, giving you full control over execution flow.

### How it Works

Because you are subclassing `Expression`, you are defining the behavior of the AST Node itself. You can access the raw, unevaluated arguments in `self.tail` and decide which (if any) to evaluate and when.

### Implementation Steps

1.  Create a class inheriting from `Expression`.
2.  (Optional) Override `__init__` if you need specific validationlogic.
3.  Override `evaluate(self, context: Context) -> BaseElement`.
4.  Inside `evaluate`, manually call `.evaluate(context)` on specific tail elements as needed.
5.  Implement logic that may mutate the `context` or branch based on conditions.

### Example: Implementing an `If` Special Form

This example requires lazy evaluation. If we used Method 1, both the "true" and "false" branches would be evaluated before the `If` logic ran, which is undesirable.

```python
class IfExpression(Expression):
    """
    Special form: If(condition, then_branch, else_branch)
    Only evaluates the branch that matches the condition.
    """
    def evaluate(self, context: Optional[Context]) -> BaseElement:
        if context is None:
            context = Context()

        # 1. Access raw arguments
        condition_node = self.tail[0]
        then_node = self.tail[1]
        else_node = self.tail[2]

        # 2. Evaluate ONLY the condition first
        condition_result = condition_node.evaluate(context)
        
        # Determine truthiness (assuming a Literal boolean)
        # Using Python bool() on the underlying value
        is_true = bool(condition_result.value if isinstance(condition_result, Literal) else False)

        # 3. LAZY EVALUATION: Choose which branch to run
        if is_true:
            return then_node.evaluate(context)
        else:
            return else_node.evaluate(context)

# Usage
if_expr = IfExpression(
    Literal(True), 
    Literal("Yes"), 
    Literal("No")
)

print(if_expr.evaluate(None))  # Outputs: Yes
```

### Characteristics

-   **Evaluation Strategy**: **Lazy**. You have full control and can choose not to evaluate certain arguments (e.g., the "else" branch of an `If`).
-   **Context Access**: **Full**. The `evaluate` method receives the `Context` object, allowing you to read/write variables or inspect the global state.
-   **State**: **Mutable**. These forms can change the context (e.g., defining new variables).

---

## Decision Guide: Which Method Should I Use?

Use the following criteria to decide how to implement your feature:

### Use Method 1 (Context Registration) when:
-   **The operation is stateless.** The result depends only on the input arguments.
-   **You need eager evaluation.** All arguments must be processed (e.g., `Add(a, b)` needs both `a` and `b`).
-   **The logic is simple.** It transforms data A into data B.
-   **Examples:** Math (`Add`, `Sqrt`), String operations (`Concat`), List operations (`Map`, `Filter`).

### Use Method 2 (Subclassing) when:
-   **The operation involves control flow.** You need to skip evaluating certain arguments (e.g., `If`, `And`, `Or` short-circuiting).
-   **The operation mutates state.** You need to define or delete variables in the context (e.g., `Set`, `Let`).
-   **The operation needs context information.** The function relies on global variables or settings not passed as arguments.
-   **Examples:** Logic control (`If`, `Switch`), Loops (`While`, `For`), Definition (`Def`, `Set`).