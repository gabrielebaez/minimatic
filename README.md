# minimatic

An experiment on language design and system integration.
VM + DB + Server + Prelude


ALERT: Currently in very alpha version, thigs will move around a lot.


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


## A bit of (future) syntax

Function Application:

- f(x) - standard call
- f @ x - prefix application
- x // f - postfix application
- f /@ list - map over list

Pattern Matching:

- _		pattern standing for anything (“blank”)
- __		pattern standing for any sequence (“double blank”)
- x_		pattern named x
- a|b    pattern matching a or b
- matchQ(expr,pattern)		test whether expr matches a pattern
- cases(list,pattern)		find cases of a pattern in a list
- lhs -> rhs		         rule for transforming lhs into rhs
- expr /. lhs -> rhs		   replace lhs by rhs in expr

Control:

- if(condition, then, else)   # conditional
- while(condition, body)      # loop
- expr1; expr2; expr3         # sequence
