(* E-Commerce API *)

(* 1. DSL PRIMITIVES
   Hold converts these into data structures (ASTs) that are 
   interpreted by high-level builtins rather than executed immediately *)
SetAttributes[Endpoint, Hold]
SetAttributes[Transaction, Hold]
SetAttributes[Validate, Hold]
SetAttributes[Pipeline, Hold]

(* 2. HIGH-LEVEL BUILTINS
   These have lowest specificity—user definitions always win when specific:
   - Database[operation, table, args]  →  ACID operations
   - HTTPError[code, message]          →  HTTP response generation  
   - Render[component, layout]         →  HTML/JSON rendering
   - StartServer[config, routes]       →  HTTP server bootstrap
   - Cache[key, expr, ttl]             →  Memoization layer
*)

(* ROUTE DEFINITIONS (Specificity-Ordered) *)

(* Specificity Tier 1: Concrete literal paths (exact match) *)
Endpoint[GET["/health"]] :=
  JSON[{"status" -> "healthy", "timestamp" -> Now}]

Endpoint[GET["/api/v1/products/featured"]] :=
  Cache["featured", 
    Database["query", "products", <|"featured" -> True|>], 
    300
  ]

(* Specificity Tier 2: Type-constrained parameters *)
Endpoint[GET["/api/v1/users", id_Integer]] :=
  JSON[Database["select", "users", id]]

Endpoint[GET["/api/v1/orders", id_Integer, "items"]] :=
  JSON[
    Database["join", 
      {"orders", "order_items"}, 
      <|"orders.id" -> id|>
    ]
  ]

(* Specificity Tier 3: Generic string patterns *)
Endpoint[GET["/api/v1/products", category_String]] :=
  JSON[
    Database["query", "products", <|"category" -> category|>]
  ]

(* Specificity Tier 4: Wildcard catch-all (lowest priority) *)
Endpoint[GET[path_]] :=
  HTTPError[404, "No endpoint matches: " <> path]

(* COMPLEX HANDLERS WITH HOLD *)

(* Transaction blocks hold their contents as an AST.
   The Transaction builtin interprets this at runtime,
   handling rollback, retries, and connection pooling. *)
createOrderHandler = Endpoint[
  POST["/api/v1/orders"],

  (* Validate holds the schema check unevaluated until request time *)
  Validate[Body, Schema[{"user_id" -> Integer, "items" -> List}]],

  (* Pipeline composes operations; Hold prevents premature execution *)
  Pipeline[
    (* Eval forces evaluation of dbConfig now, injecting the value *)
    Eval[dbConfig],

    (* These remain quoted—the Transaction builtin evaluates them *)
    ValidateInventory[Body["items"]],
    CalculateTotals[Body],
    Database["insert", "orders", Body],
    PublishEvent["order.created", Body]
  ]
]

(* CONFIGURATION INJECTION *)

(* Evaluate at DSL-definition time, not request time *)
dbConfig = {
  "pool_size" -> 20,
  "timeout" -> 30,
  "isolation" -> "serializable"
}

stripeKeys = { "secret" -> Environment["STRIPE_SECRET"] }

(* Eval splices evaluated data into the held expression *)
paymentEndpoint = Endpoint[
  POST["/api/v1/payments"],
  Validate[Body, Schema[{"amount" -> Number, "token" -> String}]],

  Transaction[
    Eval[stripeKeys],  (* Injects the evaluated association *)
    ChargeStripe[Body["token"], Body["amount"]],
    Database["insert", "payments", Body],
    (* Conditional logic held as data until runtime *)
    If[Amount > 1000, Require[ManualReview], Approve]
  ]
]

(* SERVER COMPOSITION *)

(* Without Hold, these would execute immediately and fail.
   With Hold, StartServer receives a structured specification. *)
app = StartServer[
  Port[Eval[Environment["PORT"]]],  (* 8080 or similar injected *)

  Middleware[
    CORS[Origins -> {"https://shop.example.com"}],
    RateLimit[100, "1m"],
    Auth[JWT, Exempt["/health", "/api/v1/products/featured"]]
  ],

  (* Route table passed as held expressions *)
  createOrderHandler,
  paymentEndpoint,
  Endpoint[GET["/api/v1/users", _]],  (* Integer constraint applies *)
  Endpoint[GET["/api/v1/products", _]] (* String constraint applies *)
]

(* EVALUATION TRACE (Conceptual) *)

(* Request arrives: GET /api/v1/users/123 *)

(* Step 1: Pattern Collection *)
Candidates = {
  Endpoint[GET["/health"]],                            (* Specificity: Literal *)
  Endpoint[GET["/api/v1/users", id_Integer]],          (* Specificity: Typed *)
  Endpoint[GET["/api/v1/products", category_String]],  (* Specificity: Typed, wrong head *)
  Endpoint[GET[path_]]                                 (* Specificity: Wildcard *)
}

(* Step 2: Specificity Sorting *)
(* 1. Literal paths: No match ("/health" ≠ "/api/v1/users/123") *)
(* 2. Typed patterns: 
      - "/api/v1/users", id_Integer matches (123 is Integer)
      - "/api/v1/products", category_String rejected (head mismatch) *)
(* 3. Wildcard: Matches, but less specific than Integer constraint *)

(* Winner: Endpoint[GET["/api/v1/users", id_Integer]] *)
(* Binding: id -> 123 *)

(* Step 3: Rule Application *)
Result = JSON[Database["select", "users", 123]]

(* Step 4: Re-evaluation (Step 9 in procedure) *)
(* If Database[...] evaluates to <|"name" -> "Alice", ...|>, 
   then JSON applies to that result, producing the response *)

(* ============================================
   MACROS VIA HOLD (Advanced)
   ============================================ *)

(* Defining reusable patterns with Hold *)
SetAttributes[Authenticated, Hold]
SetAttributes[AuditLog, Hold]

(* Macro expansion happens via specificity: 
   More specific patterns trigger first, wrapping handlers *)

(* Audit logging wrapper - specific to Transaction endpoints *)
Endpoint[method_, AuditLog[body_]] /; 
  ContainsQ[body, Transaction] :=
    Sequence[
      Log["AUDIT", method, Timestamp],
      Endpoint[method, body],  (* Original handler *)
      Log["AUDIT", method, "completed"]
    ]

(* Usage: AuditLog automatically wraps the Transaction *)
securedEndpoint = Endpoint[
  POST["/api/v1/admin/refund"],
  Authenticate[Admin],
  AuditLog[
    Transaction[
      Database["update", "orders", status -> "refunded"],
      Database["insert", "refunds", Data]
    ]
  ]
]

------------

(* Template DSL with Hold *)
SetAttributes[Report, Hold]
SetAttributes[Section, Hold]
SetAttributes[ForEach, Hold]

salesReport = Report[
  Title["Q3 Sales Summary"],

  (* Eval forces immediate lookup; rest remains quoted *)
  Eval[HeaderData["company_name"]],

  (* ForEach holds the body; evaluated once per row at render time *)
  ForEach[Row["sales"], 
    Section[
      H2[Row["region"]],
      Table[
        Row["transactions"],
        Columns[{"date", "amount", "status"}]
      ],
      (* Conditional logic held as AST until data available *)
      If[Row["total"] > 100000, Highlight[Alert], Nothing]
    ]
  ],

  Footer[GeneratedAt[Now]]
]

(* Specificity-based dispatch for different output formats *)
Render[Report[content_], "pdf"] :=
  Pipeline[
    Layout[content, Style -> Corporate],
    ChromePDF[Width -> 8.5 inch, Height -> 11 inch]
  ]

Render[Report[content_], "excel"] :=
  FlattenStructure[content, SheetPerSection]
