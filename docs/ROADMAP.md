# Minimatic Roadmap

> **Status: v0.1.0 — Foundation**
> The symbolic engine, pattern matcher, and evaluation loop are complete and tested (496 tests passing).
> Arithmetic and control flow builtins are implemented. The system needs comparison, logic, list, and string builtins to become usable for real programs.

---

## Phase 0 — Foundation ✅

The core symbolic computation engine is complete.

| Component | Status |
|-----------|--------|
| Immutable symbols with interning | ✅ Done |
| Immutable expressions `(head, args, attrs)` | ✅ Done |
| Evaluation attributes (Hold, Flat, Orderless, Listable) | ✅ Done |
| Standard evaluation procedure (10-step loop) | ✅ Done |
| Pattern matching with backtracking | ✅ Done |
| Bindings (immutable, frozenset-backed) | ✅ Done |
| Evaluation contexts with scoping | ✅ Done |
| OwnValues, DownValues, UpValues, SubValues | ✅ Done |
| Sequence flattening, Flat, Orderless, Listable transforms | ✅ Done |
| Builtin registry and dispatch | ✅ Done |

---

## Phase 1 — Usability (Current)

Making minimatic usable for basic programs. **In progress.**

### 1.1 — Comparison & Logic Builtins

| Builtin | Signature | Description |
|---------|-----------|-------------|
| `Less` | `Less[a, b]` | `Less[1, 2]` → `True` |
| `Greater` | `Greater[a, b]` | `Greater[2, 1]` → `True` |
| `LessEqual` | `LessEqual[a, b]` | `LessEqual[1, 1]` → `True` |
| `GreaterEqual` | `GreaterEqual[a, b]` | `GreaterEqual[2, 1]` → `True` |
| `Equal` | `Equal[a, b]` | Mathematical equality: `Equal[1, 1.0]` → `True` |
| `Unequal` | `Unequal[a, b]` | `Unequal[1, 2]` → `True` |
| `And` | `And[a, b, ...]` | Short-circuit AND: `And[True, False]` → `False` |
| `Or` | `Or[a, b, ...]` | Short-circuit OR: `Or[False, True]` → `True` |
| `Not` | `Not[expr]` | `Not[True]` → `False` |
| `EvenQ` | `EvenQ[n]` | `EvenQ[4]` → `True` |
| `OddQ` | `OddQ[n]` | `OddQ[3]` → `True` |

### 1.2 — List Builtins

| Builtin | Signature | Description |
|---------|-----------|-------------|
| `Part` | `Part[expr, i]` or `Part[expr, i, j, ...]` | Index: `Part[{a,b,c}, 2]` → `b` |
| `Length` | `Length[expr]` | `Length[{1,2,3}]` → `3` |
| `Range` | `Range[n]` or `Range[min, max, step]` | `Range[5]` → `{1,2,3,4,5}` |
| `Append` | `Append[list, elem]` | `Append[{1,2}, 3]` → `{1,2,3}` |
| `Prepend` | `Prepend[list, elem]` | `Prepend[{2,3}, 1]` → `{1,2,3}` |
| `Join` | `Join[list1, list2, ...]` | `Join[{1,2}, {3,4}]` → `{1,2,3,4}` |
| `Flatten` | `Flatten[list]` or `Flatten[list, depth]` | `Flatten[{{1},{2,3}}]` → `{1,2,3}` |
| `Sort` | `Sort[list]` or `Sort[list, comp]` | `Sort[{3,1,2}]` → `{1,2,3}` |
| `Reverse` | `Reverse[list]` | `Reverse[{1,2,3}]` → `{3,2,1}` |
| `Select` | `Select[list, test]` | `Select[{1,2,3,4}, EvenQ]` → `{2,4}` |
| `Take` | `Take[list, n]` | `Take[{1,2,3,4}, 2]` → `{1,2}` |
| `Drop` | `Drop[list, n]` | `Drop[{1,2,3,4}, 2]` → `{3,4}` |
| `First` | `First[list]` | `First[{1,2,3}]` → `1` |
| `Last` | `Last[list]` | `Last[{1,2,3}]` → `3` |
| `Most` | `Most[list]` | `Most[{1,2,3}]` → `{1,2}` |
| `Rest` | `Rest[list]` | `Rest[{1,2,3}]` → `{2,3}` |
| `Total` | `Total[list]` | `Total[{1,2,3}]` → `6` |
| `MemberQ` | `MemberQ[list, elem]` | `MemberQ[{1,2}, 2]` → `True` |
| `FreeQ` | `FreeQ[expr, elem]` | `FreeQ[{1,2}, 3]` → `True` |
| `Position` | `Position[expr, elem]` | `Position[{a,b,a}, a]` → `{{1},{3}}` |
| `Count` | `Count[expr, elem]` | `Count[{1,2,1,3}, 1]` → `2` |
| `DeleteDuplicates` | `DeleteDuplicates[list]` | `DeleteDuplicates[{1,2,1}]` → `{1,2}` |
| `MapIndexed` | `MapIndexed[f, list]` | `MapIndexed[f, {a,b}]` → `{f[a,1], f[b,2]}` |
| `MapThread` | `MapThread[f, {list1, list2}]` | `MapThread[f, {{1,2},{3,4}}]` → `{f[1,3], f[2,4]}` |

### 1.3 — Expression Inspection Builtins

| Builtin | Signature | Description |
|---------|-----------|-------------|
| `Head` | `Head[expr]` | `Head[Plus[1,2]]` → `Plus` |
| `Apply` | `Apply[f, expr]` or `f @@ expr` | `Apply[f, Plus[1,2]]` → `f[1,2]` |
| `Replace` | `Replace[expr, rules]` | First-match replacement |
| `ReplaceAll` | `ReplaceAll[expr, rules]` or `expr /. rules` | Replace all matches |
| `MapAt` | `MapAt[f, expr, pos]` | Apply f at specific position |
| `Scan` | `Scan[f, expr]` | Apply f for side effects, return `Null` |
| `Depth` | `Depth[expr]` | `Depth[f[g[x]]]` → `3` |
| `LeafCount` | `LeafCount[expr]` | `LeafCount[f[a,b]]` → `3` |

---

## Phase 2 — Functional Programming

Enabling higher-order and functional programming patterns.

### 2.1 — Pure Functions

| Builtin | Signature | Description |
|---------|-----------|-------------|
| `Function` | `Function[x, body]` or `Function[{x,y}, body]` | Anonymous function: `Function[x, x+1]` |
| `Slot` | `#` | Positional arg placeholder: `# + 1 &` |
| `SlotSequence` | `##` | Sequence placeholder: `## &` |

### 2.2 — Extended Functional Builtins

| Builtin | Signature | Description |
|---------|-----------|-------------|
| `FoldList` | `FoldList[f, x, list]` | Like Fold, collecting intermediates |
| `FoldRight` | `FoldRight[f, x, list]` | Right fold |
| `NestWhile` | `NestWhile[f, expr, test]` | Apply while test passes |
| `NestWhileList` | `NestWhileList[f, expr, test]` | Collect intermediates |
| `FixedPoint` | `FixedPoint[f, expr]` | Apply until stable |
| `FixedPointList` | `FixedPointList[f, expr]` | Collect intermediates |
| `Array` | `Array[f, n]` | `Array[f, 3]` → `{f[1], f[2], f[3]}` |
| `ConstantArray` | `ConstantArray[val, n]` | `ConstantArray[0, 5]` → `{0,0,0,0,0}` |
| `Outer` | `Outer[f, list1, list2]` | Outer product |
| `Inner` | `Inner[f, list1, list2, g]` | Inner product |
| `Thread` | `Thread[f[{a,b}, {c,d}]]` | → `{f[a,c], f[b,d]}` |
| `Distribute` | `Distribute[f[{a,b}, {c,d}]]` | Distribute over lists |
| `Subsets` | `Subsets[list]` | All subsets |
| `Permutations` | `Permutations[list]` | All permutations |
| `Tuples` | `Tuples[list, n]` | All n-tuples |

---

## Phase 3 — String Processing

| Builtin | Signature | Description |
|---------|-----------|-------------|
| `StringJoin` | `StringJoin["a", "b"]` | Concatenate: `"ab"` |
| `StringSplit` | `StringSplit["a,b,c", ","]` | Split: `{"a","b","c"}` |
| `StringLength` | `StringLength["hello"]` | Length: `5` |
| `StringTake` | `StringTake["hello", 3]` | `"hel"` |
| `StringDrop` | `StringDrop["hello", 2]` | `"llo"` |
| `StringReverse` | `StringReverse["abc"]` | `"cba"` |
| `StringTrim` | `StringTrim["  hi  "]` | `"hi"` |
| `StringContainsQ` | `StringContainsQ["hello", "ell"]` | `True` |
| `StringStartsQ` | `StringStartsQ["hello", "he"]` | `True` |
| `StringEndsQ` | `StringEndsQ["hello", "lo"]` | `True` |
| `StringPosition` | `StringPosition["hello", "l"]` | `{{3,3},{4,4}}` |
| `StringCount` | `StringCount["hello", "l"]` | `2` |
| `StringReplace` | `StringReplace["abc", "b"->"B"]` | `"aBc"` |
| `StringCases` | `StringCases["abc123", DigitCharacter..]` | `{"123"}` |
| `StringRiffle` | `StringRiffle[{"a","b"}, ","]` | `"a,b"` |
| `Characters` | `Characters["abc"]` | `{"a","b","c"}` |
| `FromCharacters` | `FromCharacters[{"a","b","c"}]` | `"abc"` |
| `ToString` | `ToString[42]` | `"42"` |
| `ToExpression` | `ToExpression["1+2"]` | `3` |
| `UpperCaseQ` | `UpperCaseQ["ABC"]` | `True` |
| `LowerCaseQ` | `LowerCaseQ["abc"]` | `True` |
| `ToUpperCase` | `ToUpperCase["abc"]` | `"ABC"` |
| `ToLowerCase` | `ToLowerCase["ABC"]` | `"abc"` |
| `StringPadLeft` | `StringPadLeft["hi", 5]` | `"   hi"` |
| `StringPadRight` | `StringPadRight["hi", 5]` | `"hi   "` |
| `StringInsert` | `StringInsert["ac", "b", 2]` | `"abc"` |
| `StringDelete` | `StringDelete["abc", 2]` | `"ac"` |

---

## Phase 4 — Numeric & Math

### 4.1 — Trigonometric & Hyperbolic

| Builtin | Description |
|---------|-------------|
| `Sin`, `Cos`, `Tan` | Trigonometric functions |
| `ArcSin`, `ArcCos`, `ArcTan` | Inverse trig |
| `Sinh`, `Cosh`, `Tanh` | Hyperbolic functions |
| `ArcSinh`, `ArcCosh`, `ArcTanh` | Inverse hyperbolic |

### 4.2 — Numeric Utilities

| Builtin | Signature | Description |
|---------|-----------|-------------|
| `Max` | `Max[a, b, ...]` | Maximum of arguments |
| `Min` | `Min[a, b, ...]` | Minimum of arguments |
| `Mod` | `Mod[a, b]` | Modulo: `Mod[7, 3]` → `1` |
| `Quotient` | `Quotient[a, b]` | Integer division |
| `Floor` | `Floor[x]` | `Floor[3.7]` → `3` |
| `Ceiling` | `Ceiling[x]` | `Ceiling[3.2]` → `4` |
| `Round` | `Round[x]` | `Round[3.5]` → `4` |
| `Sign` | `Sign[x]` | `Sign[-5]` → `-1` |
| `Chop` | `Chop[expr]` | Round near-zero to zero |
| `N` | `N[expr]` or `N[expr, digits]` | Numeric approximation |

### 4.3 — Integer & Number Theory

| Builtin | Signature | Description |
|---------|-----------|-------------|
| `Factorial` | `Factorial[n]` or `n!` | `5!` → `120` |
| `GCD` | `GCD[a, b]` | Greatest common divisor |
| `LCM` | `LCM[a, b]` | Least common multiple |
| `PrimeQ` | `PrimeQ[n]` | Is prime? |
| `Divisors` | `Divisors[n]` | All divisors |
| `Prime` | `Prime[n]` | nth prime |

### 4.4 — Constants & Random

| Builtin | Description |
|---------|-------------|
| `Pi` | π (symbolic constant) |
| `E` | Euler's number |
| `Degree` | π/180 |
| `GoldenRatio` | (1+√5)/2 |
| `I` | Imaginary unit |
| `RandomReal` | Random real in [0,1) |
| `RandomInteger` | Random integer in range |
| `SeedRandom` | Seed the PRNG |

---

## Phase 5 — Expression Manipulation & Metaprogramming

### 5.1 — Structure Inspection

| Builtin | Signature | Description |
|---------|-----------|-------------|
| `FullForm` | `FullForm[expr]` | Canonical representation |
| `InputForm` | `InputForm[expr]` | Input-compatible form |
| `TreeForm` | `TreeForm[expr]` | Tree visualization |
| `ByteCount` | `ByteCount[expr]` | Memory usage |

### 5.2 — Transformation

| Builtin | Signature | Description |
|---------|-----------|-------------|
| `MapAll` | `MapAll[f, expr]` | Map at all levels |
| `ReplaceList` | `ReplaceList[expr, rule]` | All possible replacements |
| `ReplaceRepeated` | `ReplaceRepeated[expr, rules]` | Apply until stable (`//.`) |
| `Operate` | `Operate[p, expr]` | Apply operator to head |
| `Level` | `Level[expr, n]` | Extract at level n |
| `Cases` | `Cases[expr, pattern]` | Extract matching subexpressions |
| `DeleteCases` | `DeleteCases[expr, pattern]` | Remove matching subexpressions |
| `Extract` | `Extract[expr, pos]` | Extract at position |
| `HoldComplete` | `HoldComplete[expr]` | Prevent all evaluation |

### 5.3 — Symbol Management

| Builtin | Signature | Description |
|---------|-----------|-------------|
| `Clear` | `Clear[sym]` | Remove all values from symbol |
| `ClearAll` | `ClearAll[sym]` | Clear values and attributes |
| `Attributes` | `Attributes[sym]` | Get attributes |
| `SetAttributes` | `SetAttributes[sym, attr]` | Set attributes |
| `OwnValues` | `OwnValues[sym]` | Get own values |
| `DownValues` | `DownValues[sym]` | Get down values |
| `UpValues` | `UpValues[sym]` | Get up values |
| `Definition` | `Definition[sym]` | Show all definitions |
| `Information` | `Information[sym]` | Show info |
| `Names` | `Names["pattern"]` | List matching symbols |
| `Context` | `Context[sym]` | Get symbol context |

---

## Phase 6 — Error Handling & Control Flow Extensions

### 6.1 — Exception-like Control

| Builtin | Signature | Description |
|---------|-----------|-------------|
| `Catch` | `Catch[expr]` | Catch thrown values |
| `Throw` | `Throw[val]` | Throw a value |
| `Return` | `Return[val]` | Early return from function |
| `Break` | `Break[]` | Break from loop |
| `Continue` | `Continue[]` | Continue to next iteration |
| `Check` | `Check[expr, failexpr]` | Handle messages |
| `Abort` | `Abort[]` | Abort evaluation |
| `AbortProtect` | `AbortProtect[expr]` | Evaluate despite abort |
| `TimeConstrained` | `TimeConstrained[expr, t]` | Time limit |
| `MemoryConstrained` | `MemoryConstrained[expr, n]` | Memory limit |
| `Once` | `Once[expr]` | Evaluate once, cache result |

### 6.2 — Messages

| Builtin | Description |
|---------|-------------|
| `Message` | Generate a message |
| `Messages` | Get messages for a symbol |
| `MessageName` | `General::usage` style names |
| `$MessageList` | Recent messages |
| `$Messages` | Message stream |

---

## Phase 7 — Associations & Structured Data

| Builtin | Signature | Description |
|---------|-----------|-------------|
| `Association` | `Association[k1->v1, ...]` | Create association |
| `Key` | `Key["name"]` | Key accessor |
| `Keys` | `Keys[assoc]` | List keys |
| `Values` | `Values[assoc]` | List values |
| `Lookup` | `Lookup[assoc, key]` | Safe key access |
| `KeyExistsQ` | `KeyExistsQ[assoc, key]` | Key exists? |
| `KeyTake` | `KeyTake[assoc, keys]` | Extract keys |
| `KeyDrop` | `KeyDrop[assoc, keys]` | Remove keys |
| `KeySort` | `KeySort[assoc]` | Sort by key |
| `KeySelect` | `KeySelect[assoc, test]` | Filter by key |
| `Merge` | `Merge[assoc1, assoc2]` | Merge associations |
| `GroupBy` | `GroupBy[list, f]` | Group elements |
| `Counts` | `Counts[list]` | Element counts |
| `Tally` | `Tally[list]` | Element tallies |
| `Gather` | `Gather[list, test]` | Group by equality |
| `GatherBy` | `GatherBy[list, f]` | Group by function |

---

## Phase 8 — File I/O & System

### 8.1 — File Operations

| Builtin | Signature | Description |
|---------|-----------|-------------|
| `Get` | `Get["file.m"]` | Read and evaluate file |
| `Put` | `Put[expr, "file.m"]` | Write expression to file |
| `Import` | `Import["file.ext"]` | Import data |
| `Export` | `Export["file.ext", data]` | Export data |
| `OpenRead` | `OpenRead["file"]` | Open for reading |
| `OpenWrite` | `OpenWrite["file"]` | Open for writing |
| `Close` | `Close[stream]` | Close stream |
| `Read` | `Read[stream]` | Read from stream |
| `Write` | `Write[stream, expr]` | Write to stream |
| `Print` | `Print[expr]` | Print to stdout |
| `Input` | `Input["prompt"]` | Read from stdin |

### 8.2 — System Functions

| Builtin | Description |
|---------|-------------|
| `$Version` | Minimatic version |
| `$OperatingSystem` | OS name |
| `$MachineName` | Machine hostname |
| `$UserName` | Current user |
| `DateString` | Current date/time |
| `AbsoluteTime` | Unix timestamp |
| `Pause` | Sleep for n seconds |
| `Run` | Run shell command |
| `RunProcess` | Run and capture output |

---

## Phase 9 — Parsing & Syntax

A lexer and parser for `.mm` syntax:

```mathematica
(* Instead of: *)
Expression(Plus, 1, 2)

(* Write: *)
1 + 2
```

| Feature | Description |
|---------|-------------|
| Lexer | Tokenize `.mm` source |
| Parser | Build AST from tokens |
| Operator precedence | `+`, `*`, `^`, etc. |
| Infix/postfix operators | `+`, `//`, `/@`, `\|>` |
| Function call syntax | `f[x, y]` |
| Pure function syntax | `# + 1 &` |
| Pattern syntax | `x_`, `__`, `/;`, `?` |
| Rule syntax | `->`, `:=`, `:>` |
| Compound expressions | `a; b; c` |
| Comments | `(* ... *)` |

---

## Phase 10 — Performance & Polish

| Feature | Description |
|---------|-------------|
| Expression caching | Hash-consing for structural sharing |
| Bytecode compilation | Compile common patterns |
| JIT compilation | Optional acceleration |
| Lazy evaluation | On-demand evaluation |
| Memoization | Automatic result caching |
| Documentation | Full API reference |
| REPL | Interactive evaluation |
| Notebook support | Jupyter-style interface |

---

## Milestones

| Milestone | Phase | What It Unlocks |
|-----------|-------|-----------------|
| **v0.2.0 — Usable** | 1 + 1.4 | Conditional logic, list processing, basic programs |
| **v0.3.0 — Functional** | 2 | Higher-order programming, pure functions |
| **v0.4.0 — Text** | 3 | String processing, serialization |
| **v0.5.0 — Math** | 4 | Scientific computing, numeric algorithms |
| **v0.6.0 — Meta** | 5 | Metaprogramming, code generation |
| **v0.7.0 — Robust** | 6 | Error handling, resource management |
| **v0.8.0 — Data** | 7 | Structured data, JSON-like objects |
| **v0.9.0 — System** | 8 | File I/O, system integration |
| **v1.0.0 — Complete** | 9 + 10 | Parser, syntax, performance, polish |
