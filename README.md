# Minimatic

> **Experimental Prototype**
> Research-grade software. APIs, semantics, and internal structure are subject to change without notice.

A minimal implementation of a Wolfram Language-style symbolic computation engine in Python. Minimatic provides immutable symbolic expressions, pattern matching, and an evaluation loop with structural attributes (Flat, Orderless, Listable) and hold semantics.

---

## Architecture

```
src/
  core/          Fundamental data structures
    symbol.py      Immutable interned symbols
    expression.py  Immutable expressions: (head, args, attributes)
    atoms.py       Python-native primitives (int, float, complex, str, bool, None)
    attributes.py  Evaluation attributes (Hold, Flat, Orderless, Listable, ...)

  pattern/       Wolfram-style pattern matching
    blanks.py      Wildcard patterns (_, __, ___)
    structural.py  Pattern, Condition, Alternatives, PatternTest, Optional, ...
    bindings.py    Immutable match result bindings
    matcher.py     Core matching engine

  eval/          Evaluation engine
    evaluator.py   Standard evaluation procedure
    context.py     Evaluation contexts with scoping
    rules.py       Rule and RuleDelayed types
    values.py      OwnValues, DownValues, UpValues, SubValues, NValues
    transforms.py  Sequence flattening, Flat, Orderless, Listable transforms

  builtins/      Built-in function implementations
    registry.py    Function registration and dispatch
    arithmetic.py  Plus, Times, Power, Minus, Divide, Abs, Sqrt, Exp, Log, Sum, Product
```

---

## Core Types

### Symbol

Interned, immutable symbolic identifiers. Two symbols with the same name are the same object.

```python
from src.core import Symbol, symbol, gensym

x = Symbol("x")
y = symbol("y")
g = gensym("tmp")  # Symbol("tmp1")

x is Symbol("x")   # True (interned)
```

### Expression

Immutable compound structures: `(head, args, attributes)`.

```python
from src.core import Expression, Symbol

Plus = Symbol("Plus")
expr = Expression(Plus, 1, 2, 3)

expr.head       # Symbol("Plus")
expr.args       # (1, 2, 3)
expr.attributes # frozenset()

# With attributes
from src.core import Hold
held = Expression(Plus, 1, 2, _attrs={Hold})
held.has_attr(Hold)  # True
```

### Atoms

Python's native types are used directly -- no wrappers.

| Python type | Head symbol |
|-------------|-------------|
| `int` | `Integer` |
| `float` | `Real` |
| `complex` | `Complex` |
| `str` | `String` |
| `bool` | `Symbol` |
| `None` | `Symbol` |

---

## Evaluation

The evaluator implements the standard Wolfram Language evaluation procedure:

```
1. Dispatch by type     Atom → self.  Symbol → OwnValues.  Expression → continue.
2. Evaluate head        (skip if HoldAllComplete)
3. Resolve attributes   head_attrs ∪ expression_attrs
4. Evaluate arguments   (respecting HoldAll / HoldFirst / HoldRest)
5. Flatten Sequences    splice Sequence[...] into argument lists
6. Apply Flat           Plus[Plus[a,b], c] → Plus[a,b,c]
7. Apply Orderless      canonical sort arguments
8. Apply Listable       f[{a,b}, c] → {f[a,c], f[b,c]}
9. Try rules            UpValues → DownValues → SubValues → NValues → Built-in
10. Fixed-point check   if changed, re-evaluate (up to $IterationLimit)
```

```python
from src.core import Symbol, Expression
from src.eval import evaluate, GlobalContext

ctx = GlobalContext

Plus = Symbol("Plus")

evaluate(Expression(Plus, 1, 2, 3), ctx)                   # 6
evaluate(Expression(Plus, Expression(Plus, 1, 2), 3), ctx) # 6 (Flat)
```

### Hold Attributes

| Attribute | Effect |
|-----------|--------|
| `HoldAll` | No arguments evaluated |
| `HoldFirst` | First argument not evaluated |
| `HoldRest` | Arguments after first not evaluated |
| `HoldAllComplete` | Nothing evaluated (including head) |
| `SequenceHold` | `Sequence[...]` not flattened |

### Value Types

| Type | Purpose |
|------|---------|
| `OwnValues` | Symbol definitions (`x = 5`) |
| `DownValues` | Function definitions (`f[x_] := ...`) |
| `UpValues` | Operator overloading (`expr_f := ...`) |
| `SubValues` | Subscripted functions (`f[a][b] := ...`) |
| `NValues` | Numeric approximation (`N[expr]`) |

---

## Pattern Matching

Full Wolfram Language-style pattern matching with backtracking.

### Pattern Types

| Pattern | Syntax | Description |
|---------|--------|-------------|
| Blank | `_` or `_h` | Matches any single expression (optionally with head constraint) |
| BlankSequence | `__` or `__h` | Matches one or more expressions |
| BlankNullSequence | `___` or `___h` | Matches zero or more expressions |
| Pattern | `x_` or `x_h` | Named binding |
| Condition | `pat /; test` | Conditional match |
| Alternatives | `a \| b` | Match either pattern |
| PatternTest | `pat ? test` | Test predicate |
| Optional | `x_ : default` | Optional with default |
| Repeated | `pat..` | One or more |
| RepeatedNull | `pat...` | Zero or more |
| Verbatim | `Verbatim[expr]` | Literal match |
| HoldPattern | `HoldPattern[pat]` | Prevent pattern evaluation |

```python
from src.core import Symbol, Expression
from src.core.attributes import Flat, Orderless
from src.pattern import match, pattern, blank, blank_seq, alternatives, condition, optional, replace_with_bindings, Bindings

x, y = Symbol("x"), Symbol("y")
Plus = Symbol("Plus")

# Basic matching
r = match(Expression(Plus, pattern(x), pattern(y)), Expression(Plus, 1, 2))
r.success   # True
r[x]        # 1
r[y]        # 2

# Head-constrained blank
from src.core import Integer
match(blank(Integer), 42).success    # True
match(blank(Integer), 3.14).success  # False

# Sequence matching
r = match(
    Expression(Plus, blank_seq(), pattern(y)),
    Expression(Plus, 1, 2, 3)
)
r[y]  # 3

# Flat matching (pass expr_attrs from evaluator context)
r = match(
    Expression(Plus, pattern(x), pattern(y), pattern(z)),
    Expression(Plus, Expression(Plus, 1, 2), 3),
    expr_attrs=frozenset({Flat})
)
r[x], r[y], r[z]  # 1, 2, 3

# Orderless matching
r = match(
    Expression(Plus, pattern(x), pattern(y)),
    Expression(Plus, 3, 1),
    expr_attrs=frozenset({Orderless})
)
# x and y bound to 1 and 3 (in some order)

# Substitution
b = Bindings({x: 1, y: 2})
replace_with_bindings(Expression(Plus, x, y), b)  # Plus[1, 2]
```

### Bindings

Immutable match results backed by `frozenset`. Safe for backtracking.

```python
from src.pattern import Bindings, BindingConflict

b = Bindings({x: 42})
b2 = b.bind(y, 3.14)  # New Bindings; b unchanged

b.bind(x, 99)  # Raises BindingConflict
```

---

## Built-in Functions

Registered via `@register_builtin` decorator with attribute metadata.

| Function | Attributes | Description |
|----------|------------|-------------|
| `Plus` | Flat, Orderless, Listable, NumericFunction | Addition |
| `Times` | Flat, Orderless, Listable, NumericFunction | Multiplication |
| `Power` | NumericFunction, Listable | Exponentiation |
| `Minus` | Listable, NumericFunction | Unary minus |
| `Divide` | Listable, NumericFunction | Division |
| `Subtract` | Listable, NumericFunction | Binary subtraction |
| `Abs` | Listable, NumericFunction | Absolute value |
| `Sqrt` | Listable, NumericFunction | Square root |
| `Exp` | Listable, NumericFunction | Exponential |
| `Log` | Listable, NumericFunction | Logarithm |
| `Sum` | HoldRest | Summation |
| `Product` | HoldRest | Product |

```python
from src.core import Symbol, Expression
from src.eval import evaluate, GlobalContext
from src.builtins import arithmetic  # Registers all arithmetic builtins

ctx = GlobalContext
Plus, Times, Power = Symbol("Plus"), Symbol("Times"), Symbol("Power")

evaluate(Expression(Plus, 1, 2, 3), ctx)       # 6
evaluate(Expression(Times, 2, 3, 4), ctx)      # 24
evaluate(Expression(Power, 2, 10), ctx)        # 1024
evaluate(Expression(Plus, Expression(Times, 2, 3), 4), ctx)  # 10
```

---

## Current Limitations

- **No parser** -- expressions are constructed programmatically via `Expression(head, *args)`
- **No lexer/AST** -- the `.m` example files are not yet parsed by this engine
- **Limited built-ins** -- only arithmetic; no list, string, or logic functions
- **No user-defined functions** -- `DownValues`/`UpValues` infrastructure exists but no syntactic sugar for defining them
- **No symbolic algebra** -- no simplification, expansion, or factoring
- **Performance** -- pure Python; no compilation or JIT
- **Tests** -- no formal test suite; verified via ad-hoc scripts

---

## Running

```python
from src.core import Symbol, Expression
from src.eval import evaluate, GlobalContext
from src.builtins import arithmetic

ctx = GlobalContext
Plus = Symbol("Plus")

# Build expressions programmatically
expr = Expression(Plus, 1, 2, 3)
print(evaluate(expr, ctx))  # 6
```

---

## License

MIT
