# minimatic

An experiment on language design and system integration.
VM + DB + Server + Prelude


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

4. Everything is integrated (built-in knowledge)  
   - The vast python ecosystem is available as computable expressions.


## A bit of syntax

Function Application:

- f(x) - standard call
- f @ x - prefix application
- x // f - postfix application
- f /@ list - map over list

Pattern Matching:

- expr //. {pattern :> replacement} # replace patterns
- x_     # matches anything, binds to x
- x___   # matches sequence, binds to x
- pattern /; condition  # conditional pattern
- :>  # delayed replacement
- ->  # immediate replacement

Control:

- if(condition, then, else)   # conditional
- while(condition, body)      # loop
- expr1; expr2; expr3         # sequence


# Core language functions

## Arithmetic & Logic

- add(a, b)           # +
- sub(a, b)           # -
- mul(a, b)           # *
- div(a, b)           # /
- mod(a, b)           # %
- eq(a, b)            # ==
- lt(a, b)            # <
- gt(a, b)            # >
- and(a, b)           # logical and
- or(a, b)            # logical or
- not(a)              # logical not

## Control Flow

- if(condition, then_expr, else_expr)
- while(condition, body)
- seq(expr1, expr2, ...)              # sequential execution

## Data Structures

- list(item1, item2, ...)
- get(collection, index)
- set(collection, index, value)
- len(collection)
- append(collection, item)

## Variables & Scope

- let(name, value, body)              # local binding
- def(name, params, body)             # function definition
- call(function, args...)

## I/O & Conversion

- print(value)
- input()
- str(value)
- num(value)
- type(value)

## Iteration

- map(function, collection)
- filter(function, collection)
- reduce(function, collection, initial)
