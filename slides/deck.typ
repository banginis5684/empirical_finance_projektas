// Rental Price Hedonics: Typst deck.
// Style follows the VU wildcat theme used in Replication-Crisis-Finance/slides.typ:
// 16 by 9, burgundy titles with a gold rule, facets on the opening and closing slides.
// The deck needs no packages. Build with: typst compile deck.typ

#let vu = rgb("#7D2035")
#let vu-dark = rgb("#4B1320")
#let vu-70 = rgb("#AF667B")
#let vu-40 = rgb("#CDB2B9")
#let vu-20 = rgb("#E6D9DD")
#let vu-10 = rgb("#F2ECEE")
#let gold = rgb("#FFD100")
#let ink = rgb("#1A1A1A")
#let grey = rgb("#6E6E6E")
#let hair = rgb("#D9D9D9")

#let sans = ("TeX Gyre Adventor", "Inter", "DejaVu Sans")
#let display = ("TeX Gyre Heros", "Inter", "DejaVu Sans")

#set page(
  width: 16cm,
  height: 9cm,
  margin: (top: 1.85cm, bottom: 0.75cm, x: 0.95cm),
)
#set text(font: sans, size: 9.5pt, fill: ink)
#set par(leading: 0.56em, justify: false)
#set list(
  marker: text(fill: vu, size: 0.85em)[•],
  indent: 0.5em,
  body-indent: 0.4em,
  spacing: 0.42em,
)
#set math.equation(numbering: none, block: true)
#show math.equation.where(block: true): it => align(center, it)

// Build toggle: `typst compile deck.typ --input short=true deck-short.pdf`
// keeps only the slides a 10-minute talk needs; the default build is all 20.
#let short = sys.inputs.at("short", default: "false") == "true"
#let SHORT_KEEP = (
  "Rent as a bundle of characteristics",
  "Main regression",
  "Zooming in: Vilnius by district",
  "Location adds more than age, floor and heating",
  "Who gets a price cut?",
  "What this is worth, and what it is not",
)

// One content slide: section kicker, burgundy title, gold rule, page number.
#let slide(sec, head, body) = {
  if short and head not in SHORT_KEEP { return none }
  page(
    header: block(width: 100%)[
      #text(font: display, size: 7.2pt, fill: vu-70, tracking: 0.12em)[#upper(sec)]
      #v(-1pt)
      #text(font: display, size: 14.5pt, fill: vu)[#head]
      #v(-2pt)
      #line(length: 1.15cm, stroke: 1.4pt + gold)
    ],
    footer: align(right, text(size: 7pt, fill: grey)[
      #context [#(counter(page).get().first()) / #(counter(page).final().first())]
    ]),
    body,
  )
}

// Small grey aside used under tables and figures.
#let note(body) = block(above: 0.55em, text(size: 7.6pt, fill: grey, body))

// Section sub-head inside a slide body.
#let head2(body) = block(above: 0.7em, below: 0.25em, text(font: display, size: 10pt, weight: "bold", fill: vu-dark)[#body])

// Table: burgundy header, zebra rows, first column left, numbers right.
#let vtable(columns, headers, rows, size: 8.2pt) = table(
  columns: columns,
  inset: (x: 5pt, y: 2.6pt),
  stroke: none,
  fill: (x, y) => if y == 0 { vu } else if calc.odd(y) { vu-10 } else { white },
  align: (x, y) => if x == 0 { left } else { right },
  table.header(..headers.map(h => text(fill: white, weight: "bold", size: size)[#h])),
  ..rows.map(r => r.map(c => text(size: size)[#c])).flatten(),
)

// Figure: image scaled to one dimension, optional caption underneath.
#let fig(path, width: 11cm, height: none, caption: none) = {
  align(center, if height == none { image(path, width: width) } else { image(path, height: height) })
  if caption != none { note(align(center, caption)) }
}

// KPI value with a small uppercase label.
#let stat(value, label) = block[
  #text(font: display, size: 20pt, weight: "bold", fill: vu)[#value]
  #v(0.05em)
  #text(size: 7pt, fill: grey, tracking: 0.08em)[#upper(label)]
]

// ---------------------------------------------------------------- Slide 1
#page(
  margin: 0pt,
  background: image("assets/facets.svg", width: 100%, height: 100%),
)[
  #place(top + left, dx: 0.4cm, dy: 0.25cm, image("assets/vu-logo-white.png", width: 1.9cm))
  #place(bottom + left, dx: 0.95cm, dy: -0.8cm)[
    #block(width: 12.2cm)[
      #text(font: display, size: 7.5pt, fill: gold, tracking: 0.14em)[EMPIRICAL FINANCE · COURSE PROJECT]
      #v(0.3cm)
      #text(font: display, size: 24pt, fill: white, weight: "bold")[What Determines Apartment Rent?]
      #v(0.3cm)
      #text(size: 9.5pt, fill: vu-20)[A hedonic pricing analysis of 2,662 rental listings from aruodas.lt, Lithuania's largest real-estate portal.]
      #v(0.45cm)
      #text(size: 8.5pt, fill: white)[Data collected November 2026 · 6 cities plus smaller towns · cross-sectional, single snapshot]
    ]
  ]
]

// ---------------------------------------------------------------- Slide 2
#slide("1 · Question and approach", "Rent as a bundle of characteristics")[
  A rental unit is a bundle of attributes (size, rooms, floor, age, heating, location) that the market prices as a whole.
  Hedonic regression recovers an implicit price for each attribute by regressing the observed rent on the bundle.

  #head2[What this is, and is not]
  - This is a cross-sectional, observational dataset: one scrape, one point in time, no randomisation and no repeated observations per unit.
  - The results below are descriptive correlations, not causal effects. On the ladder of research designs, this sits near the bottom rung.
  - The question we can answer: which characteristics move with rent, and by how much, after holding the others fixed.
]

// ---------------------------------------------------------------- Slide 3
#slide("2 · The sample", "2,662 listings, 6 cities plus smaller towns")[
  #grid(
    columns: (1fr, 1fr, 1fr, 1fr),
    column-gutter: 0.5cm,
    stat("2,662", "listings"),
    stat("€699", "mean rent"),
    stat("49.5 m²", "mean area"),
    stat("1988", "mean year built"),
  )

  #grid(
    columns: (1fr, 1fr),
    column-gutter: 0.9cm,
    [
      #head2[By city (full sample)]
      #vtable(
        (1.5fr, 0.8fr),
        ("City", "N"),
        (
          ("Vilnius", "1,401"), ("Kaunas", "437"), ("Klaipėda", "302"),
          ("Other", "265"), ("Šiauliai", "103"), ("Palanga", "101"), ("Panevėžys", "53"),
        ),
      )
    ],
    [
      #head2[Primary heating (regression sample)]
      #vtable(
        (1.5fr, 0.8fr),
        ("Type", "N"),
        (
          ("Centrinis (district)", "1,257"), ("Centrinis kolektorinis", "823"),
          ("Dujinis (gas)", "316"), ("Elektra (electric)", "152"), ("Other", "92"),
        ),
      )
    ],
  )

  #note[22 listings dropped for the regression sample: implausible build years (before 1800) or rents outside €100–5,000, leaving N = 2,640.]
]

// ---------------------------------------------------------------- Slide 4
#slide("3 · Model", "Model")[
  Rent is regressed in logs, so each coefficient reads as an approximate percentage effect:

  $ ln("Price"_i) = beta_0 + beta_1 "Area"_i + beta_2 "Rooms"_i + beta_3 "Age"_i + beta_4 "FloorRatio"_i
      + sum_(k) gamma_k "Heat"_(i k) + sum_(j) delta_j "City"_(i j) + epsilon_i $

  $ "FloorRatio"_i = "Floor"_i / "TotalFloors"_i, quad "Age"_i = 2026 - "YearBuilt"_i $

  #note[Estimated by OLS with HC1 heteroskedasticity-robust standard errors, justified on the diagnostics slide. Reference categories: Centrinis heating and Kaunas city. Coefficients are log points: $beta times 100$ approximates the percentage effect, $exp(beta) - 1$ is exact.]
]

// ---------------------------------------------------------------- Slide 5
#slide("3 · Model", "Why model rent in logs?")[
  #fig("assets/hist_price.png", width: 13cm,
    caption: [Raw rents are right-skewed; the log transform used throughout is close to symmetric.])
]

// ---------------------------------------------------------------- Slide 6
#slide("4 · Results", "Main regression")[
  #grid(
    columns: (64%, 1fr),
    column-gutter: 0.7cm,
    [
      #vtable(
        (2.3fr, 0.75fr, 0.85fr, 0.55fr),
        ("Variable", "Coef.", "Robust SE", "p"),
        (
          ("Area (m²)", "0.0091", "0.0008", "<0.001"),
          ("Rooms", "0.1406", "0.0193", "<0.001"),
          ("Age (years)", "−0.0009", "0.0002", "<0.001"),
          ("Floor ratio", "0.0247", "0.0204", "0.226"),
          ("Heating: Centrinis kolektorinis", "0.1893", "0.0140", "<0.001"),
          ("Heating: Dujinis", "0.0884", "0.0227", "<0.001"),
          ("Heating: Elektra", "0.0616", "0.0322", "0.056"),
          ("City: Vilnius", "0.1439", "0.0178", "<0.001"),
          ("City: Klaipėda", "−0.1630", "0.0221", "<0.001"),
          ("City: Šiauliai", "−0.3243", "0.0315", "<0.001"),
          ("City: Panevėžys", "−0.3975", "0.0473", "<0.001"),
        ),
        size: 7.3pt,
      )
      #note[R² = 0.638, adj. R² = 0.636, F(14, 2625) = 245.3, N = 2,640. Reference: Centrinis heating, Kaunas.]
    ],
    [
      - Each extra m² adds about 0.9% to rent, holding room count fixed.
      - One more room adds about 15%, even at the same total area. Layout, not just size, is priced.
      - Vilnius commands a 15% premium over Kaunas; Šiauliai and Panevėžys rent for 28–33% less.
    ],
  )
]

// ---------------------------------------------------------------- Slide 7
#slide("4 · Results", "Rent vs. size and room count")[
  #fig("assets/scatter_area_rooms.png", width: 13cm,
    caption: [The two strongest bivariate relationships the main model estimates jointly.])
]

// ---------------------------------------------------------------- Slide 8
#slide("4 · Results", "Coefficients, visually")[
  #fig("assets/coefplot.png", height: 5.3cm,
    caption: [Same estimates as the results table, shown as point estimates with 95% confidence intervals.])
]

// ---------------------------------------------------------------- Slide 9
#slide("5 · Diagnostics", "Is the model well specified?")[
  #grid(
    columns: (1fr, 1fr),
    column-gutter: 0.9cm,
    [
      #head2[Heteroskedasticity]
      Breusch–Pagan: $chi^2 = 148.5$, $p < 0.001$.
      #note[Residual variance is not constant, as expected for rent levels. This is why HC1 robust standard errors are used throughout rather than the classical OLS SEs.]
    ],
    [
      #head2[Multicollinearity]
      #vtable(
        (1.5fr, 0.8fr),
        ("Variable", "VIF"),
        (("Area", "2.61"), ("Rooms", "2.61"), ("Age", "1.01"), ("Floor ratio", "1.01")),
      )
      #note[All below the conventional concern threshold of 5–10; area and rooms move together, as expected, but not severely.]
    ],
  )

  #head2[Influential observations]
  177 of 2,640 listings (6.7%) exceed the Cook's distance rule of thumb $4 \/ n$. Consistent with heavy-tailed rents at the top of the market (penthouses and other high-end units) rather than data errors.
]

// ---------------------------------------------------------------- Slide 10
#slide("5 · Diagnostics", "How well does the model fit?")[
  #fig("assets/fit.png", height: 5.3cm,
    caption: [Predicted vs. actual log-rent; points on the dashed 45° line are predicted exactly.])
]

// ---------------------------------------------------------------- Slide 11
#slide("5 · Diagnostics", "Residual diagnostics")[
  #fig("assets/resid.png", width: 13cm,
    caption: [Mild heteroskedasticity and right-tail departure from normality, consistent with the Breusch–Pagan test.])
]

// ---------------------------------------------------------------- Slide 12
#slide("6 · Extension", "Zooming in: Vilnius by district")[
  Refitting within Vilnius alone and replacing the city dummy with district fixed effects raises R² from 0.649 to 0.762 on the same 1,393 listings.

  #grid(
    columns: (1fr, 1fr),
    column-gutter: 0.9cm,
    [
      #head2[Premium districts]
      #vtable(
        (1.7fr, 0.8fr, 0.6fr),
        ("District", "Effect", "p"),
        (
          ("Paupys", "+55.2%", "<0.001"), ("Senamiestis (Old Town)", "+40.4%", "<0.001"),
          ("Užupis", "+34.0%", "<0.001"), ("Naujamiestis", "+18.5%", "<0.001"),
        ),
      )
    ],
    [
      #head2[Discount districts]
      #vtable(
        (1.7fr, 0.8fr, 0.6fr),
        ("District", "Effect", "p"),
        (
          ("Naujoji Vilnia", "−13.8%", "<0.001"), ("Karoliniškės", "−13.1%", "0.009"),
          ("Pašilaičiai", "−12.1%", "<0.001"), ("Pilaitė", "−10.1%", "0.001"),
        ),
      )
    ],
  )

  #note[Area and room effects are essentially unchanged. The heating premiums halve and age matters about three times as much. Exact % effects, $exp(beta) - 1$, against Antakalnis.]
]

// ---------------------------------------------------------------- Slide 13
#slide("6 · Extension", "Location effects, visually")[
  #fig("assets/bars_city_district.png", width: 13cm,
    caption: [City effects (left) and Vilnius-district effects (right), from the two regressions.])
]

// ---------------------------------------------------------------- Slide 14
#slide("7 · Decomposition", "Where does the fit come from?")[
  R² = 0.638 is one number for four very different kinds of information. Adding the blocks one at a time, in the order a landlord would reason about a unit, shows what each is worth.

  #fig("assets/seq_r2.png", width: 8.0cm)
  #note[Each model nests the previous one; the marginal R² is the gain from adding that block.]
]

// ---------------------------------------------------------------- Slide 15
#slide("7 · Decomposition", "Location adds more than age, floor and heating")[
  - Size and room count alone explain 40.3 points of the 63.8-point R²: the bulk of the floor.
  - Building age and floor position add only 2.7 points more; heating type adds 5.6 points.
  - Added last, location still adds 15.3 points, more than age, floor and heating combined.
  - Within Vilnius, a district model reaches R² = 0.762, up from 0.649 without districts.

  #note(if short [
    Marginal R² from the sequential decomposition.
  ] else [
    Marginal R² from the sequential decomposition on the previous slide; district result from the Vilnius-only model.
  ])
]

// ---------------------------------------------------------------- Slide 16
#slide("7 · Decomposition", "Is the city gap real, or just composition?")[
  A city could rent for less simply because its units are smaller or older, not because location itself is cheaper. Comparing the raw rent gap to the gap after holding size, age and heating fixed separates the two.

  #grid(
    columns: (54%, 1fr),
    column-gutter: 0.7cm,
    [
      #fig("assets/city_gap_decomp.png", width: 7.6cm)
    ],
    [
      - Vilnius: most of its +18% raw premium is genuine location, not bigger units.
      - Šiauliai and Panevėžys: composition (smaller, older stock) explains roughly a fifth of their raw discount: the pure location penalty is smaller than it first looks.
    ],
  )
]

// ---------------------------------------------------------------- Slide 17
#slide("8 · Secondary outcome", "Who gets a price cut?")[
  24.9% of listings show a price marked down from an earlier asking price. A logit on the same characteristics asks whether the same bundle predicts a cut:

  $ "Pr"("PriceCut"_i = 1) = Lambda(beta_0 + bold(beta)' bold(x)_i) $

  #grid(
    columns: (50%, 1fr),
    column-gutter: 0.8cm,
    [
      #vtable(
        (2.1fr, 0.8fr, 0.7fr),
        ("Variable", "Coef.", "p"),
        (
          ("Floor ratio", "−0.601", "<0.001"),
          ("Age", "−0.0037", "0.041"),
          ("Area", "−0.0039", "0.271"),
          ("Rooms", "0.048", "0.614"),
          ("City/heating dummies", "n/a", "> 0.07"),
        ),
        size: 7.6pt,
      )
      #note[Pseudo R² = 0.013, N = 2,640. Almost none of the discount variation is explained.]
    ],
    [
      - Units higher up a building are markedly less likely to be discounted, and ground-and-low-floor listings carry most of the cuts.
      - Otherwise, discounting looks close to orthogonal to what a hedonic model prices.
    ],
  )
]

// ---------------------------------------------------------------- Slide 18
#slide("8 · Secondary outcome", "Price cuts by floor position")[
  #fig("assets/pricecut_floor.png", width: 9.2cm,
    caption: [The one characteristic that robustly predicts a price cut: higher floors are discounted less often.])
]

// ---------------------------------------------------------------- Slide 19
#slide("9 · Limitations and takeaways", "What this is worth, and what it is not")[
  #set text(size: 8.7pt)
  #set par(leading: 0.5em)
  #set list(spacing: 0.32em)
  #grid(
    columns: (1fr, 1fr),
    column-gutter: 0.9cm,
    [
      #head2[Takeaways]
      - Size, room count, age, heating and, especially, location jointly explain 64% of rent variation (76% within Vilnius with districts).
      - Location adds more explanatory power than age, floor and heating combined. Most of the raw city gap survives after controlling for unit size and age.
      - An extra room is worth about €105/month at the sample mean, more than the floor-area line alone predicts: layout is priced on top of size.
      - Discounting behaviour is close to unpredictable from listing characteristics, except for floor position.
    ],
    [
      #head2[Limitations]
      - Not causal. No variation is experimentally or quasi-experimentally assigned; coefficients are conditional correlations.
      - Omitted variables. Renovation quality, exact micro-location, furnishing and photos are all priced by the market and unobserved here.
      - Single snapshot. One scrape of currently-live ads; no panel structure, so time-on-market and seller fixed effects are out of reach.
    ],
  )
]

// ---------------------------------------------------------------- Slide 20
#page(
  margin: 0pt,
  background: image("assets/facets.svg", width: 100%, height: 100%),
)[
  #place(top + left, dx: 0.4cm, dy: 0.25cm, image("assets/vu-logo-white.png", width: 1.7cm))
  #align(center + horizon)[
    #block(width: 12cm)[
      #text(font: display, size: 10pt, fill: gold, tracking: 0.14em)[EMPIRICAL FINANCE · COURSE PROJECT]
      #v(0.4cm)
      #text(font: display, size: 20pt, fill: white, weight: "bold")[What Determines Apartment Rent?]
      #v(0.35cm)
      #text(size: 9pt, fill: vu-20)[A hedonic pricing analysis of 2,662 aruodas.lt rental listings.]
      #v(0.45cm)
      #text(size: 9pt, fill: gold)[Questions and discussion are welcome.]
    ]
  ]
]
