# Minimatic Design Document

> **Status**: Living document — reflects current implementation and near-term intent.

## 1. Goals

Minimatic is a minimal, self-contained implementation of a Wolfram Language-style symbolic computation engine in Python. The design prioritizes:

- **Immutability** — all core types are immutable value objects
- **Correctness** — faithful implementation of the standard evaluation procedure
- **Minimalism** — no external dependencies; pure Python
- **Extensibility** — builtins are registered externally, not wired into core types
- **Thread safety** — evaluation state is per-thread; no global mutable state beyond registration

Non-goals: parser/lexer, JIT compilation, numerical performance, full Wolfram Language compatibility.

---

## 2. Type System

### 2.1 Element — the universal type

```
Element = Atom | Symbol | Expression
```

Every value in minimatic is an `Element`. Atoms are leaves; Symbols are named references; Expressions are compound structures. The evaluator processes `Element`s and returns `Element`s.

### 2.2 Symbol

**File**: `minimatic/core/symbol.py`

- Subclass of `tuple` — structure is `(name: str,)`
- **Interned**: two `Symbol("x")` calls return the same object
- Thread-safe interning via `threading.Lock` + double-check locking
- `__slots__ = ()` — no instance dictionary, memory efficient
- Ordering via `__lt__` etc. for `Orderless` canonical sort

**Why tuple subclass**: Immutability by construction, hashability (dict keys, set members), no `__dict__` overhead. Interning eliminates name comparison in hot paths — identity check (`is`) is sufficient.

**System symbols** are pre-interned at module load: `Symbol`, `Integer`, `Real`, `List`, `Rule`, `Pattern`, `Blank`, `Sequence`, `True`, `False`, `Null`, etc.

### 2.3 Expression

**File**: `minimatic/core/expression.py`

- Subclass of `tuple` — structure is `(head, tail, attributes)`
- `head`: `Symbol | Expression` — the function/operator
- `tail`: `tuple[Element, ...]` — the arguments
- `attributes`: `frozenset[Symbol]` — evaluation modifiers

**Why tuple subclass**: Same rationale as Symbol. An `Expression` is a 3-tuple at the C level. `hash()` and `eq()` are O(1) tuple operations. No per-instance memory beyond the tuple storage.

**Immutable transformation API**: `with_head()`, `with_tail()`, `with_attrs()`, `map_args()`, `append()`, `prepend()` — all return new `Expression` objects, never mutate.

**Design constraint**: `__slots__ = ()` means no instance attributes can be added. Extension of Expression must be external (decorators, registries, or additional methods at class definition time).

### 2.4 Atoms

**File**: `minimatic/core/atoms.py`

Python native types are used directly — no wrapper classes:

| Python type | Head symbol | Notes |
|-------------|-------------|-------|
| `int` | `Integer` | |
| `float` | `Real` | |
| `complex` | `Complex` | |
| `str` | `String` | |
| `bool` | `Symbol` | `True`/`False` are symbols |
| `None` | `Symbol` | `Null` is a symbol |

**Why no wrappers**: Python's numeric tower (`int < float < complex`) already provides the right semantics. Wrapping would add allocation overhead and break interop with Python libraries.

---

## 3. Evaluation Model

### 3.1 Standard Evaluation Procedure

**File**: `minimatic/eval/evaluator.py`

The evaluator implements the 10-step Wolfram Language standard evaluation procedure:

```
1. Dispatch by type
   ├── Atom → return self
   ├── Symbol → apply OwnValues
   └── Expression → continue

2. Evaluate head (skip if HoldAllComplete)

3. Resolve effective attributes
   effective_attrs = head_ctx_attrs ∪ builtin_attrs ∪ expr_attrs

4. Evaluate arguments (respecting Hold* attributes)

5. Flatten Sequences
   h[a, Sequence[x, y], b] → h[a, x, y, b]

6. Apply Flat (associativity)
   Plus[Plus[a, b], c] → Plus[a, b, c]

7. Apply Orderless (commutativity)
   canonical sort arguments

8. Apply Listable (threading)
   f[{a, b}, c] → {f[a, c], f[b, c]}

9. Try rules (priority order)
   a. UpValues — operator overloading (left-to-right in args)
   b. DownValues — function definitions on head
   c. SubValues — subscripted function definitions
   d. NValues — numeric approximation
   e. Built-in — native implementation via registry

10. Fixed-point check
    If expression changed, re-evaluate (up to $IterationLimit)
```

### 3.2 Attribute Resolution

Attributes come from three sources, merged in this order:

```
effective_attrs = head_ctx_attrs | builtin_attrs | expr.attributes
```

1. **Context attributes** — set via `context.set_attributes(sym, attrs)` at runtime
2. **Builtin attributes** — registered via `@register_builtin(sym, attributes={...})`
3. **Expression attributes** — set at construction via `_attrs={...}`

Expression-level attributes take precedence (last wins in frozenset union). This allows per-expression overrides of built-in behavior.

### 3.3 Hold Semantics

| Attribute | Effect |
|-----------|--------|
| `Hold` | Don't evaluate this expression |
| `HoldAll` | No arguments evaluated |
| `HoldFirst` | First argument not evaluated |
| `HoldRest` | Arguments after first not evaluated |
| `HoldAllComplete` | Nothing evaluated (including head) |
| `SequenceHold` | `Sequence[...]` not flattened |

### 3.4 Value Types

**File**: `minimatic/eval/values.py`

| Type | Storage | Purpose |
|------|---------|---------|
| `OwnValues` | `Symbol → [(pattern, replacement, condition)]` | Symbol definitions (`x = 5`) |
| `DownValues` | `Symbol → [(pattern, replacement, condition)]` | Function definitions (`f[x_] := ...`) |
| `UpValues` | `Symbol → [(pattern, replacement, condition)]` | Operator overloading (`expr_f := ...`) |
| `SubValues` | `Symbol → [(pattern, replacement, condition)]` | Subscripted functions (`f[a][b] := ...`) |
| `NValues` | `Symbol → [(pattern, replacement, condition)]` | Numeric approximation |
| `DefaultValues` | `Symbol → value` | Pattern defaults |
| `FormatValues` | `Symbol → [(pattern, replacement, condition)]` | Output formatting |

Rules are tried in priority order within each type, then across types (UpValues → DownValues → SubValues → NValues → Built-in).

### 3.5 Rules

**File**: `minimatic/eval/rules.py`

Two rule types:

- **Rule** (`->`): Immediate — RHS is evaluated when rule matches
- **RuleDelayed** (`:>`): Delayed — RHS is substituted but not evaluated until next evaluation cycle

Both support optional `condition` and `priority` for ordering.

---

## 4. Pattern Matching

**Files**: `minimatic/pattern/`

### 4.1 Pattern Types

| Pattern | Representation | Description |
|---------|---------------|-------------|
| Blank | `Expression(Blank, head?)` | Matches any single expression (optionally head-constrained) |
| BlankSequence | `Expression(BlankSequence, head?)` | Matches one or more expressions |
| BlankNullSequence | `Expression(BlankNullSequence, head?)` | Matches zero or more expressions |
| Pattern | `Expression(Pattern, name, blank)` | Named binding |
| Condition | `Expression(Condition, pattern, test)` | Conditional match |
| Alternatives | `Expression(Alternatives, p1, p2, ...)` | Match any of |
| PatternTest | `Expression(PatternTest, pattern, test)` | Predicate test |
| Optional | `Expression(Optional, pattern, default)` | Optional with default |
| Repeated | `Expression(Repeated, pattern)` | One or more |
| RepeatedNull | `Expression(RepeatedNull, pattern)` | Zero or more |
| Verbatim | `Expression(Verbatim, expr)` | Literal match |
| HoldPattern | `Expression(HoldPattern, pattern)` | Prevent pattern evaluation |

**Key design choice**: Patterns are represented as regular `Expression` objects with special head symbols. This means patterns can be manipulated, composed, and inspected using the same infrastructure as any other expression. No separate pattern AST is needed.

### 4.2 Matching Algorithm

**File**: `minimatic/pattern/matcher.py` (871 lines)

The matcher is a recursive descent engine with backtracking:

1. **HoldPattern** — unwrap and continue
2. **Verbatim** — literal equality
3. **Blank** — head constraint check via `head_of(expr)`
4. **Pattern** — match inner, then bind name
5. **Condition** — match inner, evaluate test (requires evaluator)
6. **Alternatives** — try each, first success wins
7. **PatternTest** — match inner, apply test function
8. **Except** — check exclusion, optionally check alternative
9. **Repeated/RepeatedNull** — delegation to inner pattern
10. **Atoms** — equality
11. **Symbols** — equality (interned, so identity works)
12. **Expressions** — match head recursively, then match arguments

**Flat matching**: When `Flat` attribute is active, nested same-head expressions are flattened before matching. Both pattern and expression arguments are flattened: `Plus[Plus[a, b], c]` → `(a, b, c)`.

**Orderless matching**: When `Orderless` is active, the matcher tries each remaining expression for each pattern position (permutation search), pruning early on binding conflicts.

**Sequence matching**: `BlankSequence` and `BlankNullSequence` try matching different numbers of expressions, computing the minimum required by remaining patterns to prune the search.

### 4.3 Bindings

**File**: `minimatic/pattern/bindings.py`

- Immutable, backed by `frozenset`
- `bind()` returns new `Bindings` (or self if same value already bound)
- `BindingConflict` raised on contradictory bindings
- Safe for backtracking — no mutation, no copy needed

### 4.4 Substitution

`replace_with_bindings(expr, bindings)` performs structural substitution:
- Symbols in `bindings` are replaced with their values
- `List[...]`-bound sequences are flattened into argument lists
- Returns original object if nothing changed (structural sharing)

---

## 5. Evaluation Context

**File**: `minimatic/eval/context.py`

An `EvaluationContext` holds:
- Symbol table (name → Symbol)
- Attribute storage (Symbol → frozenset[Symbol])
- Value storage (all 7 value types)
- Parent context (for scoping)

Contexts chain: child → parent → ... → global. Reads traverse the chain; writes go to the innermost context.

**Thread safety**: Context stack is `threading.local()`. Each thread has its own stack. `with_context` context manager pushes/pops from the current thread's stack.

**GlobalContext**: A singleton `EvaluationContext("Global")` at module level. All top-level evaluation uses this context by default.

---

## 6. Builtins and Extensibility

### 6.1 Builtin Registry

**File**: `minimatic/builtins/registry.py`

Builtins are registered via `@register_builtin` decorator:

```python
@register_builtin(Plus, attributes={Flat, Orderless, Listable, NumericFunction}, auto_evaluate=True)
def plus_builtin(expr: Expression, context: EvaluationContext) -> Any:
    ...
```

The decorator:
1. Creates a `BuiltinFunction` dataclass (symbol, implementation, attributes, auto_evaluate)
2. Stores it in a global `_registry: dict[Symbol, BuiltinFunction]`
3. Returns the original function unchanged

**Why decorator-based registration**:
- **Separation of concerns**: builtins don't pollute the Expression class
- **External registration**: can add builtins without modifying core code
- **Attribute bundling**: evaluation attributes are tied to the implementation
- **Testability**: `clear_registry()` for isolated tests
- **Scoped overrides**: `BuiltinRegistry` with parent chaining

### 6.2 Scoped Built-in Registry

`BuiltinRegistry` supports parent chaining for context-specific built-in overrides:

```python
custom = BuiltinRegistry(parent=global_registry)
custom.register(Symbol("Simplify"), my_simplify_impl, attributes=None)
```

Lookup order: local → parent → global registry.

### 6.3 Dispatch

When no rules match (step 9e), the evaluator calls `dispatch_builtin(expr, context)`:

1. Check if head is a Symbol
2. Look up `BuiltinFunction` in registry
3. Call `builtin(expr, context)` — the implementation receives the fully-evaluated expression

### 6.4 Current Builtins

**Arithmetic** (`minimatic/builtins/arithmetic.py`):

| Function | Attributes | Semantics |
|----------|------------|-----------|
| `Plus` | Flat, Orderless, Listable, NumericFunction | Addition with symbolic simplification |
| `Times` | Flat, Orderless, Listable, NumericFunction | Multiplication with zero/one handling |
| `Power` | NumericFunction, Listable | Exponentiation, x^0=1, x^1=x |
| `Minus` | Listable, NumericFunction | Unary minus → `Times[-1, x]` |
| `Divide` | Listable, NumericFunction | Division → `Times[num, Power[den, -1]]` |
| `Subtract` | Listable, NumericFunction | Subtraction → `Plus[a, Times[-1, b]]` |
| `Abs` | Listable, NumericFunction | Absolute value |
| `Sqrt` | Listable, NumericFunction | Square root → `Power[x, 0.5]` |
| `Exp` | Listable, NumericFunction | Exponential → `Power[E, x]` |
| `Log` | Listable, NumericFunction | Natural log or base-b log |
| `Sum` | HoldRest | Iterated summation with iterator substitution |
| `Product` | HoldRest | Iterated product with iterator substitution |

**I/O** (`minimatic/builtins/io.py`):

| Function | Attributes | Semantics |
|----------|------------|-----------|
| `Request` | (none) | HTTP requests via urllib |

### 6.5 Design Decision: Decorator vs Direct Extension

Given that `Expression` is a `tuple` subclass with `__slots__ = ()`:

**Decorators (`@register_builtin`) for**:
- Head-specific operations with evaluation attributes (Flat, Orderless, HoldRest, etc.)
- Functions that need scoped overrides via `BuiltinRegistry`
- Functions where attribute resolution is part of the semantics
- Anything in `builtins/` — separated from core by design

**Direct methods on Expression for**:
- Universal structural operations (apply to any head): `with_head`, `with_tail`, `map_args`, `append`, `prepend`
- Pure attribute queries: `has_attr`, `has_any_attr`, `has_all_attrs`

**Candidates for future direct extension** (methods on Expression):
- `Map`, `Apply` — higher-order argument transformations
- `Replace`, `ReplaceAll` — pattern-based rewriting
- `Part`, `Length`, `Head` — structural accessors (partially exist as properties)

**Candidates for decorator registration**:
- `Simplify`, `Expand`, `Factor` — algebraic transformations
- `N` — numeric approximation (needs NValues infrastructure)
- `Plot`, `DSolve`, `Integrate` — domain-specific computation

---

## 7. Transforms

**File**: `minimatic/eval/transforms.py`

Structural transforms applied during evaluation (steps 5-8):

| Transform | When | Effect |
|-----------|------|--------|
| `flatten_sequences` | Always (unless SequenceHold) | `h[a, Sequence[x,y], b]` → `h[a, x, y, b]` |
| `apply_flat` | Flat attribute | `f[f[a,b], c]` → `f[a, b, c]` |
| `apply_orderless` | Orderless attribute | Canonical sort arguments |
| `apply_listable` | Listable attribute | `f[{a,b}, c]` → `{f[a,c], f[b,c]}` |

**Canonical ordering** (for Orderless):
1. Numbers (by value)
2. Strings (alphabetical)
3. Symbols (alphabetical by name)
4. Expressions (by depth, then leaf count, then string representation)

---

## 8. Thread Safety

| Mechanism | Implementation |
|-----------|---------------|
| Symbol interning | `threading.Lock` + double-check on `_symbol_cache` |
| Context stack | `threading.local()` — per-thread stack |
| Evaluation state | `threading.local()` — per-thread recursion/iteration counters |
| Builtin registry | Global `_registry` dict (import-time registration, no runtime mutation in normal use) |

The evaluator is safe for concurrent use from multiple threads, each with its own context stack and evaluation state. The only shared mutable state is the builtin registry, which is populated at import time and not modified during normal evaluation.

---

## 9. Design Tradeoffs

### 9.1 Tuple Subclass vs Dataclass

| | Tuple Subclass | Dataclass |
|---|---|---|
| Immutability | By construction | Requires `frozen=True` |
| Hashability | Automatic | Needs `frozen=True` + `unsafe_hash` |
| Memory | Minimal (no `__dict__`) | Per-instance overhead |
| Extensibility | Cannot add attributes | Can add `__init__` params |
| Pattern matching | Structural (is a tuple) | isinstance checks |

Chose tuple subclass for Symbol and Expression — immutability and memory efficiency are critical for a symbolic engine where millions of expressions may be created.

### 9.2 Expression Attributes vs Context Attributes

Expression-level attributes allow per-expression overrides without mutating the symbol's global attributes. This is essential for:
- `Hold[expr]` — the `Hold` attribute is on the expression, not the `Hold` symbol
- Testing attribute behavior in isolation
- Composing expressions with different evaluation semantics

### 9.3 Pattern Representation as Expressions

Patterns are `Expression` objects with special heads (`Blank`, `Pattern`, `Condition`, etc.). This means:
- Patterns can be constructed and inspected with the same API as any expression
- No separate AST or parser needed
- Patterns can be dynamically composed
- The matcher only needs to understand `Expression` structure

Tradeoff: pattern matching must check `head_of(expr)` against known pattern-head symbols, which is slightly slower than isinstance checks on dedicated pattern classes.

### 9.4 No Parser

Expressions are constructed programmatically via `Expression(Plus, 1, 2, 3)`. This is intentional:
- Eliminates parser/lexer complexity
- Makes the evaluation semantics the sole focus
- Allows embedding in Python workflows naturally
- Future: a parser can be added as a separate module

---

## 10. File Structure

```
minimatic/
├── core/
│   ├── symbol.py        248 lines   Immutable interned symbols
│   ├── expression.py    335 lines   Immutable expressions (head, tail, attrs)
│   ├── atoms.py         186 lines   Python-native primitives as atoms
│   └── attributes.py    232 lines   Evaluation attribute symbols
│
├── pattern/
│   ├── blanks.py        372 lines   Blank, BlankSequence, BlankNullSequence
│   ├── structural.py    568 lines   Pattern, Condition, Alternatives, etc.
│   ├── bindings.py      376 lines   Immutable match result bindings
│   └── matcher.py       871 lines   Core matching engine with backtracking
│
├── eval/
│   ├── evaluator.py     479 lines   Standard evaluation procedure (10 steps)
│   ├── context.py       207 lines   Evaluation contexts with scoping
│   ├── rules.py         166 lines   Rule and RuleDelayed types
│   ├── values.py        184 lines   Value type storage (OwnValues, DownValues, ...)
│   └── transforms.py    211 lines   Sequence flattening, Flat, Orderless, Listable
│
├── builtins/
│   ├── registry.py      141 lines   @register_builtin + BuiltinRegistry
│   ├── arithmetic.py    598 lines   Plus, Times, Power, and related operations
│   └── io.py             78 lines   HTTP Request builtin
│
└── __init__.py           41 lines   Public API
```

**Total**: ~4,415 lines of implementation code.

---

## 11. Future Directions

### 11.1 Near-term

- **User-defined functions**: Syntactic sugar for `DownValues`/`UpValues` registration
- **Additional builtins**: `Map`, `Apply`, `Thread`, `Join`, `Select`, `Cases`, `Replace`
- **Simplify/Expand**: Algebraic transformation builtins
- **NValues**: Numeric approximation infrastructure (`N[expr, prec]`)

### 11.2 Medium-term

- **Parser**: Wolfram Language syntax → Expression trees
- **Package system**: Module loading, namespaced symbols
- **Formatting**: `FormatValues` for custom display (boxes, typesetting)
- **Compile**: Expression → Python function compilation for performance

### 11.3 Design Considerations for Future Work

- **New builtins**: Use `@register_builtin` — never modify Expression class for head-specific operations
- **New structural operations**: Consider adding as Expression methods if universally applicable
- **New pattern types**: Add head symbol + matcher case (patterns are expressions, so infrastructure scales)
- **New attributes**: Add Symbol to `attributes.py` + evaluator case in step 6-8
- **New value types**: Add storage to `EvaluationContext` + dispatch case in `_apply_rules`

---

## 12. Testing Strategy

Tests are organized to mirror the source structure:

```
tests/
├── test_core/           Symbol, Expression, Atoms, Attributes
├── test_pattern/        Blanks, Structural, Bindings, Matcher
├── test_eval/           Evaluator, Context, Values, Rules, Transforms
└── test_builtins/       Registry, Arithmetic, IO
```

Key testing patterns:
- `conftest.py` provides shared fixtures: `ctx`, `Plus`, `Times`, `x`, `y`, `z`
- Tests use `GlobalContext` directly (no setup/teardown needed)
- Builtin tests import the module to trigger `@register_builtin` side effects
- Pattern tests construct expressions programmatically (no parser)

**Running**: `pytest` from project root. **Linting**: `ruff check minimatic`. **Type checking**: `pyright minimatic`.
