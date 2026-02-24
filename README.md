
# Minimatic

> **⚠️ Experimental Prototype**  
> This is research-grade software. The syntax, semantics, and runtime are subject to radical change without notice. Do not use in production. Expect crashes, performance cliffs, and undocumented corners.

Minimatic is a symbolic expression language optimized for building **embedded DSLs** (domain-specific languages). It combines Lisp-style quotation with specificity-driven pattern matching, implemented atop Python.

**Core idea**: Instead of five different "Hold" attributes and complex rule precedence, Minimatic uses a single `Hold` (universal quotation) and dispatches rules by **pattern specificity alone**—more specific patterns always beat less specific ones, period.

---

## Learn Minimatic in 15 Minutes

### 1. Atoms and Expressions

Everything is an expression. Atoms (numbers, strings) evaluate to themselves:

```mathematica
42           (* evaluates to 42 *)
"hello"      (* evaluates to "hello" *)
```

Symbols evaluate to their bound values:

```mathematica
x = 5
x            (* evaluates to 5 *)
```

### 2. The Hold Attribute (Quotation)

By default, expressions evaluate their arguments. Use the `Hold` attribute to prevent evaluation—treating code as data:

```mathematica
Vocabulary[
  Hold -> {Quote, Workflow}
]

(* This is data, not execution *)
job = Workflow[
  Print["hello"],    (* held - not executed yet *)
  1 + 1              (* held - not evaluated to 2 *)
]
```

`Hold` is binary: it's either present or absent. No more `HoldFirst`, `HoldRest`, `HoldAllComplete` to memorize.

### 3. Eval

Use `Eval` to force evaluation inside held expressions:

```mathematica
config = <| "timeout" -> 30 |>

template = Workflow[
  Eval[config],           (* evaluates to <|"timeout" -> 30|> now *)
  Fetch["https://api.example.com"]
]
```

### 4. Rules and Specificity

Define transformation rules. The **most specific pattern wins**:

```mathematica
(* Generic catch-all *)
process[x_] := "generic"

(* More specific: integers *)
process[x_Integer] := "integer: " <> ToString[x]

(* Most specific: the literal 42 *)
process[42] := "the answer"

process[42]       (* "the answer" - literal wins *)
process[7]        (* "integer: 7" - type constraint wins *)
process["hi"]     (* "generic" - wildcard wins *)
```

Rule to remember: concrete > typed > wildcard.

### 5. Vocabulary Blocks (DSLs)

Define vocabularies to create safe, scoped languages:

```mathematica
Vocabulary DashboardDSL[
  Hold     -> {Page, Chart, For},
  Inline   -> {dataSource},        (* auto-evaluated *)
  Dispatch -> {Render},            (* entry point *)
  
  Rules[
    (* Specificity: time series get special handling *)
    Chart[data_, Type -> "line"] /; TimeSeriesQ[data] :>
      OptimizedChart[data, Sampling -> "auto"],
      
    Chart[data_, type_] :>
      StandardChart[data, type]
  ]
]

(* Usage *)
dashboard = Page[
  Chart[Eval[dataSource], Type -> "line"]
]

Render[dashboard]   (* Dispatches to DashboardDSL rules *)
```

**Key features:**
- `Extends` inherits another vocabulary (specificity shadowing)
- `Private` hides implementation symbols
- `Export` exposes safe constructors
- `Dispatch` marks evaluation entry points

### 6. Staged Computation

Minimatic excels at three-phase workflows:

```mathematica
(* Phase 1: Define (held) *)
query = Select["name", From["users"], Where[Age > 18]]

(* Phase 2: Optimize (still held, but transformed) *)
optimized = SQLPhase[Optimize[query]]

(* Phase 3: Execute (evaluated) *)
result = SQLPhase[Execute[optimized]]
```

---

## Design Philosophy

1. **Cognitive Simplicity**: One `Hold` instead of six. One specificity rule instead of five-tier precedence.
2. **DSL-First**: The language is designed for creating internal tools, report generators, and API specifications—not general-purpose systems programming.
3. **Python Native**: High-level builtins delegate to Python libraries (Jinja, FastAPI, Pandas). Minimatic handles the symbolic routing; Python handles the execution.

---

## Current Limitations

- **Performance**: Specificity sorting is O(n log n) per dispatch. Caching helps but first hits are slow.
- **Error Messages**: Tracebacks show held ASTs, not pretty-printed source.
- **Python Integration**: `Eval` escapes have full Python access—sandboxing is not yet implemented.
- **Documentation**: You're reading most of it.

---

## Contributing

This is a research prototype exploring "what if Wolfram Language had specificity-only dispatch and Lisp-style quotation?" 

Issues and PRs welcome, but be warned: the semantics are still fluid. The `Vocabulary` syntax may change radically based on usage feedback.

---

## License

MIT - Experimental. No warranties. Break it and tell us what broke.
