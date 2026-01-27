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

Minimatic is currently in the Proof of Concept (PoC) phase.

### ✅ Currently Available: Expression Engine
The core API to build and manipulate symbolic trees is fully functional.
*   Construction of immutable ASTs.
*   Recursive evaluation engine with Context support.
*   Extension interfaces for builtins and special forms.

### 🚧 In Progress: The Kernel
The Kernel is intended to be the high-level "User Interface" for the language.
*   **Goal**: Simplify interaction with the engine. Instead of manually constructing `Expression` nodes, users will interact with a session manager and a simplified API.
*   **Status**: Design phase.

### 🔜 Planned: The Parser
The component that translates text syntax into Minimatic ASTs.
*   **Goal**: Parse strings like `{ x + 5 * y }` into `Expression` objects.
*   **Status**: Scheduled for development after the Kernel stabilizes.

## Quick Start (Engine Level)

Since the Parser and Kernel are not yet available, you interact with Minimatic directly by constructing the AST in Python.

```python
from minimatic import Context, Expression, Literal, Symbol

# 1. Initialize a context
ctx = Context()

# 2. Define a Builtin (Method A: Pure Function)
def my_add(a, b):
    # Implementation detail: unwrap values
    return Literal(a.value + b.value)

ctx.set('Add', my_add)

# 3. Build AST manually
expression = Expression('Add', Literal(5), Literal(10))

# 4. Evaluate
result = expression.evaluate(ctx)
# Result is a Literal wrapping 15
```
