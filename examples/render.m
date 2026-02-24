(* ============================================
   HTML DSL DEFINITIONS
   ============================================ *)

(* Hold prevents automatic evaluation of HTML structures *)
SetAttributes[HTML, Hold]
SetAttributes[Page, Hold]
SetAttributes[Component, Hold]
SetAttributes[For, Hold]  (* Loop construct - holds body *)
SetAttributes[Slot, Hold]  (* Template injection point *)

(* ============================================
   DATA MODEL (Evaluated Context)
   ============================================ *)

(* Eval forces immediate evaluation - these are spliced in *)
userData = <|
  "name" -> "Alice Chen",
  "role" -> "Engineer",
  "metrics" -> {
    <|"metric" -> "Latency", "value" -> 45, "unit" -> "ms"|>,
    <|"metric" -> "Throughput", "value" -> 1200, "unit" -> "req/s"|>,
    <|"metric" -> "Errors", "value" -> 0.02, "unit" -> "%"|>
  },
  "alerts" -> {"Database backup pending", "SSL cert expires in 3 days"}
|>

(* ============================================
   TEMPLATE DEFINITION (Held AST)
   ============================================ *)

dashboard = Page[
  Title["System Dashboard"],
  
  (* Eval injects the evaluated association, not the symbol *)
  Eval[userData],
  
  Header[
    H1[Slot["name"]],
    Badge[Slot["role"], Color -> "blue"]
  ],
  
  (* For holds its body; evaluates once per item at render time *)
  For[Slot["metrics"], 
    Component[MetricCard,
      Title[Row["metric"]],
      Value[Row["value"], Unit[Row["unit"]]]
    ]
  ],
  
  (* Conditional held as data until context available *)
  If[Length[Slot["alerts"]] > 0,
    Section[
      Style -> "warning",
      For[Slot["alerts"], Alert[Row[]]]
    ],
    Nothing
  ]
]

(* ============================================
   SPECIFICITY-ORDERED RENDERING RULES
   ============================================ *)

(* Specificity Tier 1: Concrete atomic elements *)
Render[Page[title_, data_, content__]] :=
  Jinja[
    "<!DOCTYPE html><html><head><title>{{ title }}</title></head><body>{{ content }}</body></html>",
    <|"title" -> title, "content" -> Render[Column[content], data]|>
  ]

Render[H1[text_]] :=
  Jinja["<h1 class='page-title'>{{ text }}</h1>", <|"text" -> text|>]

Render[Badge[text_, Color -> color_]] :=
  Jinja["<span class='badge badge-{{ color }}'>{{ text }}</span>", 
    <|"text" -> text, "color" -> color|>]

(* Specificity Tier 2: Container types with data binding *)
Render[Column[items__], context_] :=
  Jinja[
    "<div class='column'>{{ items }}</div>",
    <|"items" -> StringJoin[Map[Render[#, context] &, {items}]|>
  ]

(* Specificity Tier 3: Loops (higher specificity than generic For) *)
Render[For[list_Symbol, body_], context_] /; Head[list] === Slot :=
  With[
    (* Resolve slot reference from context *)
    resolved = context[list[[1]]],  (* list is Slot["metrics"] -> "metrics" *)
    
    (* Map over resolved data, rendering body for each *)
    Jinja[
      "{{% for item in {} %}}{{ body }}{{% endfor %}}",
      <|"items" -> resolved, "body" -> Render[body, Associate[context, "item"]]|>
    ]
  ]

(* Specificity Tier 4: Slot resolution (most specific pattern) *)
Render[Slot[name_String], context_] :=
  context[name]  (* Direct lookup, no Jinja wrapper *)

(* Specificity Tier 5: Component abstraction *)
Render[Component[type_, props__], context_] :=
  Render[ExpandComponent[type, props], context]  (* Macro expansion *)

(* Specificity Tier 6: Generic fallbacks (lowest) *)
Render[expr_] := ToString[expr]  (* Catch-all *)
Render[expr_, context_] := Render[expr]  (* No context available *)

(* ============================================
   JINJA BUILTIN (High-Level Implementation)
   ============================================ *)

(* Jinja template rendering - assumes Python integration *)
Jinja[template_String, vars_Association] := Builtin[
  "python.jinja2",
  template,
  vars
]

(* ============================================
   EVALUATION TRACE
   ============================================ *)

(* Step 1: Define (everything held) *)
(* dashboard is held AST with structure preserved *)

(* Step 2: Trigger Render (Step 8 specificity matching) *)
Render[dashboard]

(* Step 3: Specificity resolution order *)
(* 
   1. Page matches Page[...] (concrete head) -> fires
   2. Eval[userData] evaluated during Page processing
   3. Header contains H1 and Badge -> specific rules fire
   4. For[Slot["metrics"], ...] matches For[list_Symbol, body] 
      (more specific than generic For[_,_])
   5. Slot["metrics"] resolves to userData["metrics"]
   6. Component[MetricCard, ...] expands via Component rule
   7. If[Length[...] > 0, ...] evaluated (not held - no Hold attribute)
      Since Length[{"Database...", "SSL..."}] = 2 > 0, Section renders
*)

(* ============================================
   OUTPUT (Python/Jinja generates)
   ============================================ *)

(* Final evaluated result after specificity-ordered rewrite: *)

"<!DOCTYPE html>
<html>
<head><title>System Dashboard</title></head>
<body>
  <div class='column'>
    <h1 class='page-title'>Alice Chen</h1>
    <span class='badge badge-blue'>Engineer</span>
    
    <div class='metric-card'>
      <div class='title'>Latency</div>
      <div class='value'>45<span class='unit'>ms</span></div>
    </div>
    <div class='metric-card'>
      <div class='title'>Throughput</div>
      <div class='value'>1200<span class='unit'>req/s</span></div>
    </div>
    <div class='metric-card'>
      <div class='title'>Errors</div>
      <div class='value'>0.02<span class='unit'>%</span></div>
    </div>
    
    <div class='section warning'>
      <div class='alert'>Database backup pending</div>
      <div class='alert'>SSL cert expires in 3 days</div>
    </div>
  </div>
</body>
</html>"