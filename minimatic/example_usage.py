# example_usage.py
#
# This script demonstrates the usage of the symbolic
# computation classes: Context, Symbol, Literal, and Expression.

from core.base_element import (Context, Symbol, 
                               Literal, Expression, 
                               BaseElement, EvaluationError)
from builtin.arithmetic import Plus

def main():
    print("=" * 70)
    print("Symbolic Computation Framework Demo")
    print("=" * 70)

    # --- 1. Basic Construction ---
    print("\n[1] Basic Construction of Elements")
    print("-" * 40)

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
    print("\n[2] Expression Evaluation")
    print("-" * 40)

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
    print("\n[3] Nested Expressions (Recursion)")
    print("-" * 40)

    # Represents: Add(Square(x), y)
    # Structure: Add( Square(x), y )
    nested_expr = Expression('Add', Expression('Square', x), y)

    print(f"Nested Expression: {nested_expr}")

    # Evaluate: Square(5) + 3 -> 25 + 3 -> 28
    result_nested = nested_expr.evaluate(ctx)
    print(f"Evaluation result: {result_nested}")

    # --- 4. Immutability and Hashability ---
    print("\n[4] Immutability and Hashability")
    print("-" * 40)

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
    print("\n[5] Structural Operations (map, replace)")
    print("-" * 40)

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
    print("\n[6] Error Handling and Reporting")
    print("-" * 40)

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
    print("\n[7] Convenience Methods")
    print("-" * 40)

    # Using callable syntax
    my_expr = Expression('Add', x, y)
    result_callable = my_expr(ctx)
    print(f"Using expr(context) syntax: {result_callable}")

    # Using From Function factory
    factory_expr = Expression.from_function('Multiply', Literal(2), Literal(3))
    ctx.set('Multiply', lambda a, b: Literal(a.value * b.value))
    print(f"Factory result: {factory_expr.evaluate(ctx)}")

    print("\n" + "=" * 70)
    print("Demo Complete")
    print("=" * 70)


if __name__ == "__main__":
    main()
