# Project Status & Roadmap

Minimatic is currently in the Proof of Concept (PoC) phase.

## ✅ Currently Available

### Expression Engine

The core API to build and manipulate symbolic trees is fully functional.

- Construction of immutable ASTs
- Recursive evaluation engine with Context support
- Extension interfaces for builtins and special forms

## 🚧 In Progress

### Context & Scope Management

- **Feature:** `ScopedContext` allowing push/pop of variable scopes.
- **Capability:** Support local variables in functions or lexical scoping within lambda expressions.
- **Why:** Required for writing complex analytical functions without variable collision.

**Transactional Context** 
- Make operations on the context ACID.
- Add traceability with a transaction log.
- Context as queryable object.

## 🔜 Planned

### The Core Engine (Foundation)

*Goal: Solidify the symbolic architecture and make the syntax ergonomic.*

#### Operator Overloading & Syntax Sugar

- **Feature:** Override magic methods (`__add__`, `__sub__`, `__mul__`, `__matmul__`) on `BaseElement`.
- **Capability:** Allow users to write `x + y * z` instead of `Expression('Add', x, Expression('Mul', y, z))`.
- **Why:** Essential for adoption. An EDSL must be indistinguishable from native Python algebra.

### The Kernel

The Kernel is intended to be the high-level "User Interface" for the language.

- **Goal:** Simplify interaction with the engine. Instead of manually constructing `Expression` nodes, users will interact with a session manager and a simplified API.
- **Status:** Design phase

#### Type System & Coercion

- **Feature:** Implement `Type` symbols and a `TypeInference` evaluator.
- **Capability:** Enforce strict typing on expressions (e.g., `Expression('Add', Float, Int)` → `Float`). Automatically cast compatible types.
- **Why:** Prevents runtime errors when bridging libraries with different type strictness (e.g., NumPy vs. pure Python).

### The Pattern Matching Engine

*Goal: Build the declarative logic layer that distinguishes Minimatic from standard Python.*

#### Pattern Primitives

- **Feature:** Introduction of `Pattern` and `Blank` (`_`) classes.
- **Capability:** Define structural patterns like `Expression('Add', _, _)` to match any addition operation.
- **Why:** Enables structural querying of the AST and data validation.

#### The Match Expression

- **Feature:** A specialized `MatchExpression` class with lazy evaluation.
- **Capability:** Execute different branches of logic based on structural matching of data.
- **Why:** Facilitates writing cleaner, declarative data validation and cleaning scripts.

#### Rule-Based Rewriting

- **Feature:** A `Rule` engine defined by patterns (e.g., `Pattern → Replacement`).
- **Capability:** Simplify symbolic expressions (e.g., `x * 0 → 0`) or optimize algorithms based on mathematical identities before execution.
- **Why:** Critical for "Pre-computation" optimization.

## 🔜 Planned

### The Language Backend

*Goal: Implement the "Unified Interface" by abstracting execution targets.*

#### Abstract Backend Interface

- **Feature:** A `BaseBackend` abstract class defining `compile(expression)` and `execute(context)`.
- **Capability:** Decouple the definition of the logic from its execution.
- **Why:** The core architecture that allows swapping Pandas for SQL.

#### The Pandas Backend

- **Feature:** A compiler that translates Minimatic `Expression` trees into Pandas method chains.
- **Capability:** `Expression('Select', df, 'col1')` → `df[['col1']]`.
- **Why:** The initial "MVP" for analytics.

#### The SQL Backend (String Generator)

- **Feature:** A compiler traversing the AST to generate SQLAlchemy queries or raw SQL strings.
- **Capability:** Execute the same Minimatic script on a PostgreSQL database without changing the DSL code.
- **Why:** The primary value proposition for "Internal Systems" (scaling data processing to the DB).

#### The NumPy/Tensor Backend

- **Feature:** Optimized execution path for vector/matrix operations.
- **Capability:** Compile linear algebra expressions to NumPy calls or PyTorch graphs.

### Data Abstractions & I/O

*Goal: Provide the tools necessary for actual data workflows.*

#### Symbolic Tables

- **Feature:** A `DataFrameElement` class inheriting from `BaseElement`.
- **Capability:** Represents a "Table" abstractly. It doesn't hold data, just metadata (schema, source, transformations).
- **Why:** Allows pipelines to be built without pulling data into memory until necessary (Lazy Evaluation).

#### I/O Connectors

- **Feature:** Standard I/O expressions (`ReadCSV`, `ReadParquet`, `WriteSQL`).
- **Capability:** Treat file/database access as symbolic nodes in the graph.
- **Why:** Allows the I/O to be included in the audit trail and dry-run plans.

#### Schema Validation

- **Feature:** Integration of the Pattern Engine with I/O.
- **Capability:** Define an expected `Pattern` for a CSV file. The `ReadCSV` node fails fast if the data doesn't match the pattern.
- **Why:** Improves data hygiene and pipeline reliability.

### Operational Excellence

*Goal: Features required for maintenance, debugging, and governance.*

#### AST Serialization

- **Feature:** `.to_json()` and `.from_json()` methods for `Expression`.
- **Capability:** Save a computation graph to a database or text file.
- **Why:** Critical for "Auditability"—storing exactly how a number was calculated.

#### Execution Plan Visualization

- **Feature:** A `.graphviz()` or `.explain()` method.
- **Capability:** Generate a visual tree of the operations that will be performed, including which backend they target.
- **Why:** Debugging efficiency; users can see if their query is running on the DB or in-memory.

#### The "Dry Run" Mode

- **Feature:** An execution mode that traverses the tree and outputs resource estimates (e.g., "This will scan 50GB of data") or permission checks without actually running data.
- **Why:** Essential for cost management in cloud environments.

#### Error Recovery & Lineage

- **Feature:** Detailed stack traces that map the `Expression` node back to the original line of user code.
- **Capability:** When a step fails, identify exactly which transformation caused it and what the state of the data was before that step.

#### Standard Library (stdlib)

- **Feature:** A bundled library of common patterns (financial calendars, regex patterns for PII, standard aggregations).
- **Why:** Accelerates development for internal users.

#### Caching

- **Feature:** Decorators or expression nodes that cache results based on input hash (memoization).
- **Capability:** `Cache('1hr', expensive_computation)`.
- **Why:** Performance optimization for iterative analytical work.