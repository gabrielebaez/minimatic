# Control Flow Builtins

Reference documentation for all control flow, evaluation control, scoping, and predicate builtins in `minimatic.builtins.control`.

---

## Assignment

### `Set[sym, val]` — Immediate assignment

Evaluates `val` and assigns the result to `sym`. Returns the assigned value.

```python
from minimatic import Symbol, Expression, evaluate
from minimatic.eval import GlobalContext

ctx = GlobalContext
x = Symbol("x")

# x = 5
evaluate(Expression(Symbol("Set"), x, 5), ctx)   # 5
evaluate(x, ctx)                                  # 5

# x = x + 1  (evaluates RHS first)
evaluate(Expression(Symbol("Set"), x, Expression(Symbol("Plus"), x, 1)), ctx)  # 6
evaluate(x, ctx)                                  # 6
```

### `SetDelayed[sym, body]` — Delayed assignment

Stores `body` unevaluated. The body is evaluated each time `sym` is referenced.

```python
# x := Random[]  (re-evaluates on each access)
SetDelayed = Symbol("SetDelayed")
Random = Symbol("Random")
evaluate(Expression(SetDelayed, x, Expression(Random)), ctx)
```

---

## Conditionals

### `If[cond, then]` — Conditional (two-arg)

Evaluates `then` if `cond` is `True`, otherwise returns `Null`.

```python
If = Symbol("If")
evaluate(Expression(If, True, 42), ctx)    # 42
evaluate(Expression(If, False, 42), ctx)   # Null
```

### `If[cond, then, else]` — Conditional (three-arg)

Evaluates `then` if `cond` is `True`, else evaluates `else`.

```python
evaluate(Expression(If, True, "yes", "no"), ctx)    # "yes"
evaluate(Expression(If, False, "yes", "no"), ctx)   # "no"
```

Only the taken branch is evaluated — the skipped branch is never evaluated:

```python
# The failing branch is never evaluated, so no error
evaluate(Expression(If, True, 1, Expression(Symbol("Plus"))), ctx)  # 1
```

### `Which[test1, val1, test2, val2, ...]` — First-match dispatch

Evaluates tests in order. Returns the value corresponding to the first `True` test.

```python
Which = Symbol("Which")
evaluate(Expression(Which,
    False, "a",
    True,  "b",
    True,  "c",
), ctx)  # "b"
```

Returns `Null` if no test is `True`.

### `Switch[expr, pat1, val1, pat2, val2, ..., default]` — Pattern-match dispatch

Evaluates `expr` once, then matches the result against patterns in order. Returns the value for the first matching pattern. An optional trailing argument is the default.

```python
Switch = Symbol("Switch")
evaluate(Expression(Switch,
    2,
    1, "one",
    2, "two",
    3, "three",
    "other",
), ctx)  # "two"
```

---

## Evaluation Control

### `CompoundExpression[a, b, ..., c]` — Sequential evaluation

Evaluates all arguments left to right, returns the last result.

```python
CompoundExpression = Symbol("CompoundExpression")
evaluate(Expression(CompoundExpression, 1, 2, 3), ctx)  # 3
evaluate(Expression(CompoundExpression), ctx)            # Null
```

### `Evaluate[expr]` — Force evaluation

Forces evaluation of an expression that would otherwise be held.

```python
Evaluate = Symbol("Evaluate")
# Evaluate overrides HoldAll on the enclosing function
```

### `ReleaseHold[expr]` — Unwrap and evaluate

Unwraps a `Hold[...]` expression and evaluates the inner expression.

```python
ReleaseHold = Symbol("ReleaseHold")
Hold = Symbol("Hold")
Plus = Symbol("Plus")

held = Expression(Hold, Expression(Plus, 1, 2))
evaluate(Expression(ReleaseHold, held), ctx)  # 3
```

### `Hold[expr]` — Prevent evaluation

Returns the expression unevaluated. Arguments are not evaluated (HoldAll).

```python
Hold = Symbol("Hold")
result = evaluate(Expression(Hold, Expression(Plus, 1, 2)), ctx)
# result is Hold[Plus[1, 2]], not 3
```

### `HoldForm[expr]` — Prevent evaluation (display)

Same as `Hold` but intended for display purposes.

```python
HoldForm = Symbol("HoldForm")
result = evaluate(Expression(HoldForm, Expression(Plus, 1, 2)), ctx)
# result is HoldForm[Plus[1, 2]]
```

---

## Looping

### `Do[body, {i, imin, imax}]` — Imperative loop

Evaluates `body` for each value of `i` from `imin` to `imax`. Returns `Null`.

```python
Do = Symbol("Do")
i = Symbol("i")
evaluate(Expression(Do, 42, Expression(Symbol("List"), i, 1, 5)), ctx)  # Null
```

### `Do[body, {i, list}]` — Iterate over list

Evaluates `body` for each element in `list`.

```python
List = Symbol("List")
evaluate(Expression(Do, 42,
    Expression(Symbol("List"), i, Expression(List, 10, 20, 30))
), ctx)  # Null
```

### `While[test, body]` — While loop

Evaluates `body` repeatedly while `test` evaluates to `True`. Returns `Null`.

```python
While = Symbol("While")
x = Symbol("x")
evaluate(Expression(Symbol("Set"), x, 0), ctx)
evaluate(Expression(While,
    Expression(Symbol("SameQ"), x, x),  # always True — use with care
    Expression(Symbol("Set"), x, 1)
), ctx)  # Null
```

### `For[start, test, incr, body]` — C-style for loop

Evaluates `start` once, then loops: check `test`, execute `body`, evaluate `incr`. Returns `Null`.

```python
For = Symbol("For")
evaluate(Expression(For,
    Expression(Symbol("Set"), x, 0),                  # start
    Expression(Symbol("SameQ"), x, x),                # test
    Expression(Symbol("Set"), x, Expression(Symbol("Plus"), x, 1)),  # incr
    Expression(Symbol("Set"), x, 10)                  # body
), ctx)
```

### `Table[expr, {i, imin, imax}]` — Generate list

Like `Do`, but collects results into a `List`.

```python
Table = Symbol("Table")
result = evaluate(Expression(Table,
    Expression(Symbol("Plus"), Symbol("i"), 1),
    Expression(Symbol("List"), Symbol("i"), 1, 5)
), ctx)
# List[2, 3, 4, 5, 6]
```

With step:

```python
result = evaluate(Expression(Table,
    Symbol("i"),
    Expression(Symbol("List"), Symbol("i"), 0, 10, 2)
), ctx)
# List[0, 2, 4, 6, 8, 10]
```

Over a list:

```python
result = evaluate(Expression(Table,
    Expression(Symbol("Plus"), Symbol("i"), 1),
    Expression(Symbol("List"), Symbol("i"), Expression(List, 10, 20, 30))
), ctx)
# List[11, 21, 31]
```

### `Nest[f, expr, n]` — Apply function n times

Applies `f` to `expr` repeatedly, `n` times.

```python
Nest = Symbol("Nest")
# Nest[f, x, 0] => x
# Nest[f, x, 1] => f[x]
# Nest[f, x, 2] => f[f[x]]
evaluate(Expression(Nest, Symbol("Null"), 42, 0), ctx)  # 42
```

### `NestList[f, expr, n]` — Collect intermediate results

Like `Nest`, but returns a list of all intermediate values `[x, f[x], f[f[x]], ...]`.

```python
NestList = Symbol("NestList")
result = evaluate(Expression(NestList, Symbol("Null"), 42, 2), ctx)
# List[42, Null[42], Null[Null[42]]]
```

### `Fold[f, expr, list]` — Left fold

Folds `f` over `list` with initial value `expr`:

```
f[f[f[expr, x1], x2], x3]
```

```python
Fold = Symbol("Fold")
Plus = Symbol("Plus")
result = evaluate(Expression(Fold, Plus, 0,
    Expression(Symbol("List"), 1, 2, 3)
), ctx)  # 6  (0+1+2+3)
```

### `Map[f, list]` — Apply function to each element

Returns a new list with `f` applied to each element.

```python
Map = Symbol("Map")
result = evaluate(Expression(Map, Plus,
    Expression(Symbol("List"), 10, 20, 30)
), ctx)
# List[Plus[10], Plus[20], Plus[30]] => List[10, 20, 30]
```

---

## Scoping

### `Module[{x=val, ...}, body]` — Lexical scoping

Creates unique local variables (via `gensym`) and substitutes their values into the body. Local variables do not leak to the outer context.

```python
Module = Symbol("Module")
x = Symbol("x")
result = evaluate(Expression(Module,
    Expression(Symbol("List"),
        Expression(Symbol("Set"), x, 10)
    ),
    Expression(Symbol("Plus"), x, 5)
), ctx)  # 15

# x is not modified in the outer context
evaluate(x, ctx)  # x (unevaluated symbol)
```

Multiple bindings:

```python
x, y = Symbol("x"), Symbol("y")
result = evaluate(Expression(Module,
    Expression(Symbol("List"),
        Expression(Symbol("Set"), x, 3),
        Expression(Symbol("Set"), y, 4)
    ),
    Expression(Symbol("Plus"), x, y)
), ctx)  # 7
```

### `Block[{x=val, ...}, body]` — Dynamic scoping

Temporarily sets values, evaluates the body, then restores the original values.

```python
Block = Symbol("Block")
x = Symbol("x")

# Set x = 1 in outer context
evaluate(Expression(Symbol("Set"), x, 1), ctx)

# Block temporarily changes x
result = evaluate(Expression(Block,
    Expression(Symbol("List"),
        Expression(Symbol("Set"), x, 99)
    ),
    x
), ctx)  # 99

# x is restored
evaluate(x, ctx)  # 1
```

### `With[{x=val, ...}, body]` — Constant substitution

Evaluates all values first, then substitutes them into the body (like `Module` but values are pre-evaluated constants).

```python
With = Symbol("With")
x = Symbol("x")
result = evaluate(Expression(With,
    Expression(Symbol("List"),
        Expression(Symbol("Set"), x, 10)
    ),
    Expression(Symbol("Plus"), x, 5)
), ctx)  # 15
```

---

## Predicates

### Boolean predicates

| Builtin | Description |
|---------|-------------|
| `TrueQ[expr]` | `True` if `expr` is `True` or `Symbol("True")`, else `False` |
| `SameQ[a, b]` | Structural equality (`===`) |
| `UnsameQ[a, b]` | `Not[SameQ[a, b]]` |

```python
TrueQ = Symbol("TrueQ")
evaluate(Expression(TrueQ, True), ctx)           # True
evaluate(Expression(TrueQ, Symbol("True")), ctx) # True
evaluate(Expression(TrueQ, False), ctx)          # False
evaluate(Expression(TrueQ, 42), ctx)             # False

SameQ = Symbol("SameQ")
evaluate(Expression(SameQ, 1, 1), ctx)           # True
evaluate(Expression(SameQ, Symbol("a"), Symbol("a")), ctx)  # True
evaluate(Expression(SameQ, Symbol("a"), Symbol("b")), ctx)  # False
```

### Type predicates

| Builtin | Description |
|---------|-------------|
| `NumericQ[expr]` | `True` if `expr` is numeric (int, float, complex) |
| `AtomQ[expr]` | `True` if `expr` is not an `Expression` |
| `HeadQ[expr, head]` | `True` if head of `expr` equals `head` |
| `ListQ[expr]` | `True` if head is `List` |
| `StringQ[expr]` | `True` if `expr` is a string |
| `IntegerQ[expr]` | `True` if `expr` is an integer |
| `RealQ[expr]` | `True` if `expr` is a float |

```python
NumericQ = Symbol("NumericQ")
evaluate(Expression(NumericQ, 42), ctx)      # True
evaluate(Expression(NumericQ, 3.14), ctx)    # True
evaluate(Expression(NumericQ, "hello"), ctx) # False
evaluate(Expression(NumericQ, True), ctx)    # False (bool is not numeric)

AtomQ = Symbol("AtomQ")
evaluate(Expression(AtomQ, 42), ctx)                         # True
evaluate(Expression(AtomQ, "hello"), ctx)                    # True
evaluate(Expression(AtomQ, Symbol("x")), ctx)                # True
evaluate(Expression(AtomQ, Expression(Plus, 1, 2)), ctx)     # False (but auto-evaluates to AtomQ[3] => True)

ListQ = Symbol("ListQ")
evaluate(Expression(ListQ, Expression(Symbol("List"), 1, 2)), ctx)  # True
evaluate(Expression(ListQ, Expression(Plus, 1, 2)), ctx)            # False

IntegerQ = Symbol("IntegerQ")
evaluate(Expression(IntegerQ, 42), ctx)     # True
evaluate(Expression(IntegerQ, 3.14), ctx)   # False

RealQ = Symbol("RealQ")
evaluate(Expression(RealQ, 3.14), ctx)      # True
evaluate(Expression(RealQ, 42), ctx)        # False (int is not float)
```

**Note on auto-evaluation:** Predicates with `auto_evaluate=True` (default) evaluate their arguments before checking. So `AtomQ[Plus[1,2]]` evaluates `Plus[1,2]` to `3`, then checks `AtomQ[3]` → `True`. To inspect unevaluated expressions, wrap in `Hold`:

```python
evaluate(Expression(AtomQ, Expression(Hold, Expression(Plus, 1, 2))), ctx)  # False (Hold[...] is an Expression)
```

---

## Attributes Summary

| Builtin | Attributes | Effect |
|---------|-----------|--------|
| `Set` | HoldFirst | RHS evaluated, LHS held |
| `SetDelayed` | HoldAll | Both sides held |
| `If` | HoldAll | Branches evaluated selectively |
| `Which` | HoldAll | Tests evaluated in order |
| `Switch` | HoldFirst | Only expr evaluated before matching |
| `CompoundExpression` | HoldAll | Evaluated sequentially |
| `Evaluate` | HoldAll | Forces evaluation |
| `ReleaseHold` | HoldAll | Unwraps and evaluates |
| `Hold` | HoldAll | Prevents evaluation |
| `HoldForm` | HoldAll | Prevents evaluation |
| `Do` | HoldAll | Body evaluated in loop |
| `While` | HoldAll | Test and body evaluated in loop |
| `For` | HoldAll | All parts evaluated in loop |
| `Table` | HoldAll | Expression evaluated in loop |
| `Nest` | HoldAll | Function applied repeatedly |
| `NestList` | HoldAll | Function applied repeatedly |
| `Fold` | HoldAll | Function applied over list |
| `Map` | HoldFirst | Function applied to elements |
| `Module` | HoldAll | Body evaluated with local bindings |
| `Block` | HoldAll | Body evaluated with temporary bindings |
| `With` | HoldAll | Body evaluated with constant substitution |
| All predicates | (default) | Arguments auto-evaluated |
