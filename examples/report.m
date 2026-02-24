(* BASE VOCABULARY: Abstract Document Model *)

Vocabulary DocumentModel[
  Hold       -> {Section, Paragraph, List, Item, Emphasis},
  Inline     -> {metadata},
  Private    -> {Normalize, ValidateStructure},
  Export     -> {Document, Section, Paragraph, List},
  
  Dispatch   -> {Normalize},  (* Stage 1: structural validation *)
  
  Rules[
    (* Flatten nested single-section documents *)
    Document[Section[content_]] :> Document[content],
    
    (* Specificity: numbered lists beat generic lists *)
    List[items__, Type -> "numbered"] :> 
      OrderedList[Map[Normalize, {items}]],
      
    List[items__] :> 
      UnorderedList[Map[Normalize, {items}]]
  ]
]

(* EXTENDED VOCABULARY: HTML Rendering *)

Vocabulary HTMLRenderer[
  Extends    -> DocumentModel,  (* Inherits Section, Paragraph... *)
  
  Hold       -> {Div, Span, Class, Id},  (* HTML-specific constructors *)
  Inline     -> {cssFramework},           (* Bootstrap, Tailwind, etc. *)
  
  Dispatch   -> {RenderHTML, CompileCSS}, (* New entry points *)
  
  Export     -> {RenderHTML, Div, Class},
  
  Rules[
    (* Specificity: Semantic sections beat generic Div *)
    Section[title_, content__] :>
      Div[
        Class["section", "mb-4"],
        H2[title],
        Div[Class["content"], Map[RenderHTML, {content}]]
      ],
      
    (* Specificity: Paragraph with Emphasis beats plain Paragraph *)
    Paragraph[text_, Emphasis[words_]] :>
      P[
        StringReplace[text, words -> Strong[words]]
      ],
      
    Paragraph[text_] :>
      P[text],
      
    (* Specificity: Styled lists beat base lists *)
    List[items__, Style -> striped] :>
      Div[
        Class["list-group", "list-group-striped"],
        Map[RenderHTML, {items}]
      ]
  ]
]

(* SPECIALIZED VOCABULARY: Dashboard Reports *)

Vocabulary DashboardReport[
  Extends    -> HTMLRenderer,
  
  Hold       -> {MetricCard, Chart, AlertPanel, TimeRange},
  Inline     -> {kpiData, chartLibrary},
  
  Dispatch   -> {RenderHTML, ExportPDF},  (* Adds ExportPDF entry point *)
  
  Defaults   -> <|"theme" -> "corporate", "timezone" -> "UTC"|>,
  
  Rules[
    (* Most specific: Live metric with trend data *)
    MetricCard[label_, value_, Trend[data_]] :>
      Div[
        Class["metric-card", "trending"],
        H3[label],
        Div[Class["value"], value],
        Sparkline[data]  (* Dashboard-specific component *)
      ],
      
    (* Medium: Static metric *)
    MetricCard[label_, value_] :>
      Div[
        Class["metric-card"],
        H3[label],
        Div[Class["value"], value]
      ],
      
    (* Chart with specific time range beats generic chart *)
    Chart[type_, data_, TimeRange[start_, end_]] :>
      canvas[
        Class["chart", type],
        Data -> Filter[data, Between[Timestamp, start, end]],
        Library -> Eval[chartLibrary]
      ],
      
    (* ExportPDF uses different specificity context than RenderHTML *)
    ExportPDF[doc_] :>
      Pipeline[
        RenderHTML[doc],  (* Reuses HTML rules *)
        Eval[cssFramework],  (* Inject print styles *)
        ChromePDF[Margin -> 0.5 inch]
      ]
  ]
]

(* USAGE: Three-Stage Pipeline *)

(* Stage 1: Definition (everything held) *)
report = Document[
  Section["Q3 Performance",
    MetricCard["Revenue", Eval[kpiData["revenue"]], Trend[kpiData["history"]]],
    Chart["line", kpiData["sales"], TimeRange["2024-07-01", "2024-09-30"]],
    List[
      Item["Target exceeded by 12%"],
      Item["New markets: APAC, LATAM"],
      Type -> "numbered"
    ]
  ]
]

(* Stage 2: Normalization (DocumentModel rules) *)
normalized = Normalize[report]

(* Stage 3: Rendering (HTMLRenderer + DashboardReport rules) *)
html = RenderHTML[normalized]  (* Specificity picks MetricCard with Trend *)

(* Stage 4: Alternative dispatch (PDF generation) *)
pdf = ExportPDF[normalized]  (* Different rule set, same source document *)

(*
    Implementation Semantics
    - Desugaring Process:
*)

Vocabulary Name[
  Hold     -> {A, B},
  Inline   -> {C},
  Dispatch -> {D},
  Extends  -> Parent,
  Rules    -> {rules...}
]
```

(* Expands to: *)

(* 1. Attribute assignment *)
Map[SetAttributes[#, Hold] &, {A, B}]
Map[SetAttributes[#, {Hold, Evaluated}] &, {C}]  (* Inline = Hold + Auto-Eval *)
Map[SetAttributes[#, Dispatch] &, {D}]

(* 2. Inheritance via specificity shadowing *)
MergeRules[Name, Parent]  (* Parent rules lower specificity unless local absent *)

(* 3. Scoped rules (active only when Dispatch symbol on stack) *)
WithRules[{rules...}, Symbol -> Name]  (* Rules tagged with vocabulary scope *)

(* 4. Visibility *)
SetVisibility[{A, B}, Private -> False]  (* Export = False means Private *)