# minimatic

An experiment on language design and system integration.

Minimatic is a symbolic-functional tiny programming language inspired by the wolfram language, 
python and picolisp.

VM + DB + Server + Prelude.

ALERT: Currently in very alpha version, things will move around a lot.


## Core ideas:

1. Everything is an expression  
   - Every piece of data, every program, every structure—even the language’s own code—is represented as a symbolic expression (```head(arg₁, arg₂, …)```).  
   - This uniform representation enables powerful homoiconicity: code can be data and data can be code.

2. Everything is symbolic  
   - Symbols stand for themselves until evaluation rules transform them.  
   - Symbolic representation allows arbitrary, domain-specific constructs without new syntax.

3. Everything is immutable (values are never overwritten in place)  
   - Once created, an expression’s value is fixed.  
   - This makes programs easier to reason about, parallelize, and test.

4. Everything is extensible  
   - Minimatic is easily extensible through the definition of Symbols.
   - A symbol is a simple class definition in python.


## Checklist to 0.0.1

- [x] Foundational classes (Expression, Literal, Symbol).
- [x] Expression evaluation.
- [x] Custom expression evaluation for functions.
- [ ] Core 25 builtin symbols.
- [ ] Initial kernel interpreter implementation.
- [ ] Stabilizing syntax / semantics.
- [ ] Initial Parser.

## A bit of (future) syntax

```
(* This is a comment *)

(* Typing an expression returns the result *)
2*2              (* 4  *)
5+8              (* 13 *)

(* Function Call *)
(* Note, function names (and everything else) are case sensitive *)
Sin(Pi/2)        (* 1 *)

(* Alternate Syntaxes for Function Call with one parameter *)
(Pi/2) // Sin    (* 1 *)

(* Every syntax in minimatic has some equivalent as a function call *)
Times(2, 2)      (* 4 *)
Plus(5, 8)       (* 13 *)

(* Using a variable for the first time defines it *)
x = 5            (* 5 *)
x == 5           (* True, C-style assignment and equality testing *)
x                (* 5 *)
x = x + 5        (* 10 *)
x                (* 10 *)
Set(x, 20)       (* Everything has a function equivalent *)
x                (* 20 *)

(* using undefined variables is fine, they just obstruct evaluation *)
cow + 5          (* 5 + cow, cow is undefined so can't evaluate further *)
cow + 5 + 10     (* 15 + cow, it'll evaluate what it can *)
moo = cow + 5    (* Beware, moo now holds an expression, not a number! *)

(* Defining a function *)
Double(x_) := x * 2     (* Note: _ after x to indicate no pattern matching constraints *)
Double(10)              (* 20 *)
Double(Sin(Pi/2))       (* 2 *)
(Pi/2) // Sin // Double (* 2, //-syntax lists functions in execution order *)

(* For imperative-style programming use ; to separate statements *)
(* Discards any output from LHS and runs RHS *)
MyFirst() := (Print("Hello"); Print("World"))  (* Note outer parens are critical here *)
MyFirst()                                      (* Hello World *)

(* Python-Style For Loop *)
PrintTo(x_) := For(y, Range(10), Print(y))     (* Var, Iterator, body *)
PrintTo(5)                                     (* 0 1 2 3 4 *)

(* While Loop *)
x = 0; While(x < 2, (Print(x); x++))        (* While loop with test and body *)

(* If and conditionals *)
x = 8; If(x==8, Print("Yes"), Print("No"))  (* Condition, true case, else case *)

Switch(x, (* Value match style switch *)
       2, Print("Two"), 
       8, Print("Yes"))

Which(  (* Elif style switch *)
  x==2, Print("No"), 
  x==8, Print("Yes"))

(* Lists *)
myList = {1, 2, 3, 4}     (* {1, 2, 3, 4} *)
myList[1]                 (* 1 - note list indexes start at 1, not 0 *)
Map(Double, myList)       (* {2, 4, 6, 8} - functional style list map function *)
Double /@ myList          (* {2, 4, 6, 8} - Abbreviated syntax for above *)
Fold(Plus, 0, myList)     (* 10 (0+1+2+3+4) *)
FoldList(Plus, 0, myList) (* {0, 1, 3, 6, 10} - fold storing intermediate results *)
Append(myList, 5)         (* {1, 2, 3, 4, 5} - note myList is not updated *)
Prepend(myList, 5)        (* {5, 1, 2, 3, 4} - add "myList = " if you want it to be *)
Join(myList, {3, 4})      (* {1, 2, 3, 4, 3, 4} *)
myList[2] = 5             (* {1, 5, 3, 4} - this does update myList *)

(* Associations, aka Dictionaries/Hashes *)
myHash = {"Green" -> 2, "Red" -> 1}   (* Create an association *)
myHash["Green"]                       (* 2, use it *)
myHash["Green"] := 5                  (* 5, update it *)
myHash["Puce"]  := 3.5                (* 3.5, extend it *)
KeyDropFrom(myHash, "Green")          (* Wipes out key Green *)
Keys(myHash)                          (* {Red, Puce} *)
Values(myHash)                        (* {1, 3.5} *)
```
