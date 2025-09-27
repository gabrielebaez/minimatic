# minimatic

An experiment on language design and system integration.
VM + DB + Server + Prelude

Core ideas:

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


Prelude (integrated symbols and functions):
- Data manipulation & Analysis
    - Data Import
    - Dataset representation
    - Data Exploration/Transformation
    - Data Export
- Visualization & graphics
- Machine learning
    - Regression
    - Classification
    - Clustering
    - Forecasting
    - NLP
    - CV
    - LLMs
- Images
- Sound & video
- Knowledge representation
- UIs
- Cloud deployment & parallel execution


The Kernel:
- Symbols (data)
  - Env variables
  - variables/data tructures
  - Containers
- Functions (behaviour)
- Services (functions with interfaces)
  - Interfaces: ways to expose functions
    - rest
    - gRPC
    - ...
- Kernels can connect together to form a pool and share resources/deploy services.