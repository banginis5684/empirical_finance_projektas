# What Determines Apartment Rent? A hedonic pricing study of the Lithuanian rental market

This repository is the complete, reproducible project behind a slide deck analyzing **2,662 rental
listings scraped from [aruodas.lt](https://www.aruodas.lt)**, Lithuania's largest real-estate portal, across
6 cities plus smaller towns. It was built as an Empirical Finance course project. This document explains what was done, why,
and, most importantly, **what every slide in the deck means**, so that someone who didn't build the
analysis can still present it confidently or review it critically.

> **Scope note.** An earlier draft of this project also explored a separate question: comparing rental
> property returns against the S&P 500 over 3–5 year holding periods, including Lithuanian tax rules and a
> downside-hedging scenario. That thread was deliberately **dropped** to keep the final project tightly
> focused on the regression / hedonic-pricing work, which is the part that's actually rigorous, empirical,
> and defensible under scrutiny. It is not included in this repository.

---

## 1. What's in this repository

```
.
├── alldataaruodas.txt              Raw scrape: pasted text dump of aruodas.lt listing pages
├── build_listings.py               Parses the raw text into a clean tabular dataset
├── listings.xlsx                   The cleaned dataset (2,662 rows), the single source of truth
├── analysis.py                     Main hedonic regression + logit + Vilnius-district robustness model
├── analysis_results.json           Numeric output of analysis.py (every coefficient, SE, p-value, diagnostic)
├── decomposition.py                Extra analysis: sequential R² decomposition, city-gap decomposition, € effects
├── decomposition_results.json      Numeric output of decomposition.py
├── pyproject.toml                  Project metadata and Python dependencies (uv)
├── uv.lock                        Locked dependency set, committed
└── slides/
    ├── deck.typ                    The deck source (Typst, 21 slides, 16:9, no packages)
    ├── deck.pdf                    The built deck: this is the artifact to present
    ├── make_charts.py              Renders the 7 "visual evidence" charts for the main deck
    ├── decomposition_charts.py     Renders the 2 decomposition charts (sequential R², city-gap)
    └── assets/                     Chart images plus the VU facets and mark used on the title slides
```

**Everything regenerates from `alldataaruodas.txt` alone.** Nothing here is hand-edited data. Every
number on every slide traces back through a script to that raw text file.

---

## 2. The data pipeline

1. **`alldataaruodas.txt`**: a manual copy-paste of aruodas.lt rental listing pages (not an API scrape or
   OCR of screenshots, because both were tried earlier in this project and were unreliable; plain copy-pasted text
   turned out to be the most faithful source).
2. **`build_listings.py`** parses that text into `listings.xlsx`: 2,662 listings with columns for city,
   street, price, any recorded price change, deposit, rooms, area, floor / total floors, year built,
   heating type, and listing type.
3. **`analysis.py`** cleans that further for regression: drops 22 listings with implausible build years
   (before 1800) or rents outside €100–5,000, leaving **N = 2,640**. This is the sample every statistic in
   the main deck is built on.

---

## 3. The methodology, in plain terms

**Hedonic regression** means: treat an apartment as a bundle of priced attributes (size, rooms, floor, age,
heating, location) and estimate how much each attribute is worth by regressing total rent on all of them at
once. It is a *descriptive* technique, not inherently causal or non-causal. See §5 for why this particular
study's results are correlational, not causal.

**The model** (log-linear, so coefficients read as approximate % effects):

```
ln(Price_i) = β₀ + β₁·Area_i + β₂·Rooms_i + β₃·Age_i + β₄·FloorRatio_i
              + Σ γ_k·Heating_ik + Σ δ_j·City_ij + ε_i
```

- `FloorRatio_i = Floor_i / TotalFloors_i`, relative height in the building (0 = ground floor, 1 = top floor)
- Reference (omitted) categories: **Centrinis heating**, **Kaunas** city
- Estimated by OLS with **HC1 heteroskedasticity-robust standard errors**, because a Breusch–Pagan test
  (χ² = 148.5, p < 0.001) confirms the residual variance isn't constant, as expected for rent levels, and the
  reason classical OLS standard errors would be wrong here.

**Headline result:** R² = 0.638 (adj. 0.636), N = 2,640. Four analyses build on this:

| Analysis | What it adds | Key number |
|---|---|---|
| Diagnostics | Is the model trustworthy? | VIF all ≤ 2.61 (no multicollinearity problem); 177/2,640 (6.7%) influential points by Cook's distance, consistent with luxury-unit outliers, not data errors |
| Vilnius-district extension | Does location matter *within* a city, not just between cities? | Swapping the city dummy for Vilnius-district fixed effects raises R² from 0.649 to **0.762** on the same 1,393 listings |
| Decomposition (new) | How much does each *block* of variables actually contribute? | Location, added last, still adds **15.3 R² points**: more than age, floor, and heating *combined* (which add 2.7 + 5.6 = 8.3 points) |
| Secondary outcome: price cuts | What predicts a listing getting marked down? | Pseudo R² = 0.013: almost nothing does, except floor position (lower floors are discounted far more often) |

---

## 4. How to rebuild everything from scratch

```bash
# 0. Create the environment (uv 0.10+, Python 3.12+)
uv sync                             # builds .venv from uv.lock, exact versions

# 1. Rebuild the dataset from the raw scrape
uv run python build_listings.py     # → listings.xlsx

# 2. Run the regressions
uv run python analysis.py           # → analysis_results.json, prints full regression summaries
uv run python decomposition.py      # → decomposition_results.json

# 3. Render chart images (run from inside slides/)
cd slides
uv run python make_charts.py        # → assets/hist_price.png, scatter_area_rooms.png, fit.png, resid.png,
                                     #   coefplot.png, bars_city_district.png, pricecut_floor.png
uv run python decomposition_charts.py   # → assets/seq_r2.png, city_gap_decomp.png

# 4. Build the deck (needs Typst 0.15 or newer, nothing else)
typst compile deck.typ              # → deck.pdf
```

`deck.pdf` is the presentation. Equations are typeset by Typst itself, so there are no equation images to
rebuild, and the page count, margins and type are fixed by `slides/deck.typ` alone.

Python dependencies are uv-managed: `pyproject.toml` declares them, `uv.lock` pins the resolution, and
`uv sync` builds `.venv`. `uv run python ...` works from the repo root and from `slides/`. The deck needs no
Python packages and no npm packages.

---

## 5. Slide-by-slide guide: `slides/deck.pdf` (main deck, 21 slides)

`slides/deck.typ` compiles to that 21-page PDF, styled after the Vilnius University wildcat theme: burgundy
titles, a gold rule, and a monochrome figure style. The PDF is the presentation artifact. Open it in any
viewer, or present straight from it. A second build keeps only the slides a short talk needs:
`typst compile deck.typ deck-short.pdf --input short=true` gives an 8-page `deck-short.pdf` from the same
source.

| # | Section | Slide | What it means / how to present it |
|---|---|---|---|
| 1 | None | Title | A hedonic pricing analysis of 2,662 listings. Say this is cross-sectional (one scrape, one point in time), not a time series. |
| 2 | 1 · Question and approach | Question, evidence, gap | States the research question, the three Lithuanian studies it builds on (Raslanas et al. 2006; Rudokas et al. 2019; Laurinavičius et al. 2022), the gap, and the contribution. Say explicitly that these are descriptive correlations, not causal effects. |
| 3 | 2 · The sample | 2,662 listings, 6 cities plus smaller towns | Headline stats (mean rent €699, mean area 49.5 m², mean year built 1988) plus the city/heating breakdown. The city table uses all 2,662 listings and the heating table the 2,640 of the regression sample. Mention the N drops from 2,662 to 2,640 (22 implausible rows removed). |
| 4 | 3 · Model | Model | The regression equation, rendered properly (not as plain-text underscores). Walk through each term once. This is the one slide worth slowing down on, since everything else refers back to it. |
| 5 | 3 · Model | Why model rent in logs? | Justifies the log transform: raw rents are right-skewed (a few very expensive units pull the tail), logs are close to symmetric. This is *why* coefficients are read as % effects, not € effects. |
| 6 | 4 · Results | Main regression | The core results table. **Three numbers to memorize:** +0.9%/m², +15%/room, Vilnius +15% vs. Kaunas. Floor ratio is *not* significant here (p = 0.226), although it becomes very significant later (slide 18/19) for a different outcome (price cuts, not price level). |
| 7 | 4 · Results | Rent vs. size and room count | The two strongest raw bivariate relationships, visually. A sanity check that the regression's two biggest coefficients are not spurious. |
| 8 | 4 · Results | Robustness checks | Five alternative choices: area in logs, street-clustered standard errors, a price sample trimmed to the 1st and 99th percentiles, duplicate ads dropped, and the 177 influential rows dropped. Also names the two findings that can overturn the result: measured renovation quality, and a gap between asking and signed rents. |
| 9 | 4 · Results | Coefficients, visually | Same table as slide 6, as a dot-and-whisker (95% CI) plot. It is easier to scan which effects are precisely estimated (narrow CI) vs. noisy (floor ratio, Elektra heating, both straddle zero). |
| 10 | 5 · Diagnostics | Is the model well specified? | Three checks: heteroskedasticity (why HC1 SEs are used), multicollinearity (VIF: area/rooms correlate but not dangerously), influential points (177 high-leverage listings, explained as luxury-unit outliers). |
| 11 | 5 · Diagnostics | How well does the model fit? | Predicted vs. actual scatter. Points hugging the 45° line = good fit; the R² = 0.638 number from slide 6 made visual. |
| 12 | 5 · Diagnostics | Residual diagnostics | Residuals-vs-fitted + Q-Q plot. It shows the mild heteroskedasticity and right-tail non-normality the Breusch–Pagan test flagged. This is "showing your work" for why HC1 SEs were the right call. |
| 13 | 6 · Extension | Zooming in: Vilnius by district | Swap city dummies for Vilnius-district fixed effects → R² rises from 0.649 to 0.762 on the same listings. **Paupys (+55%)** and **Senamiestis/Old Town (+40%)** are the standout premium districts; **Naujoji Vilnia (−14%)** the standout discount. Message: location keeps paying off at finer resolution. |
| 14 | 6 · Extension | Location effects, visually | City effects and Vilnius-district effects side by side as bar charts, a visual summary of slides 6 and 12's location coefficients. |
| 15 | 7 · Decomposition | Where does the fit come from? | **This is the most important new analytical result in the deck.** A sequential/nested R² breakdown: Size & layout alone → 40.3 points of R²; + age/floor → 42.9 (+2.7); + heating → 48.5 (+5.6); + location → 63.8 (+15.3). Location is the single biggest contributor after raw size. |
| 16 | 7 · Decomposition | Location adds more than age, floor and heating | States the headline plainly: added last, location still adds 15.3 points, more than age + floor + heating's combined 8.3. Also ties in the district result (R² 0.649 → 0.762). |
| 17 | 7 · Decomposition | Is the city gap real, or just composition? | A subtler point: is Vilnius more expensive because it's *actually* a better location, or just because Vilnius listings happen to be bigger/newer? Answer: for Vilnius, almost entirely genuine location (raw +17.9% gap vs. Kaunas, adjusted +15.5%, so composition explains only ~2 points). For Šiauliai/Panevėžys, roughly a fifth of their discount is just smaller/older stock, not a "location penalty" as such. |
| 18 | 8 · Secondary outcome | Who gets a price cut? | Switches from predicting *rent level* to predicting *whether a listing gets marked down* (24.9% of listings do, logit model). Pseudo R² is tiny (0.013). Almost nothing in the hedonic model predicts discounting, **except floor ratio**, which is strongly significant here even though it wasn't for rent level. |
| 19 | 8 · Secondary outcome | Price cuts by floor position | Visual version of slide 18's one real finding: ground/low floors get discounted far more often than top floors. |
| 20 | 9 · Limitations and takeaways | What this is worth, and what it is not | **Read this slide out loud, don't rush it.** Takeaways: location adds more than age, floor and heating combined; an extra room ≈ +€105/month; discounting is basically unpredictable except by floor. Limitations: not causal (§ below), omitted variables (renovation quality, exact micro-location, furnishings, all priced by the market and none observed here), single snapshot (no panel structure, so no time-on-market or landlord fixed effects possible). |
| 21 | None | Thank you | Closing slide. |

### If you only have 10 minutes

`deck-short.pdf` is exactly that cut: the title, framing, main regression, Vilnius districts, the
decomposition headline, price cuts, limitations, and the closing, 8 pages, about 9 minutes at a normal pace.
Build it with `typst compile deck.typ deck-short.pdf --input short=true`; no content is duplicated, the
short build just drops pages.

In the full deck the same path is slides **1, 2, 6, 13, 15 (or 16), 18, 20**: title, framing, main results,
the district extension, the decomposition headline, the price-cut finding, and limitations.

**Lithuanian references cited on slide 2.** Raslanas, S., Šteinbergas, T., and Tupenaite, L. (2006). Research on the prices of flats in the South East London and Vilnius. *International Journal of Strategic Property Management* 10(1), 51–63. doi:10.3846/1648715X.2006.9637544. Rudokas, K., Landauskas, M., Viliūnienė, O., and Gražulevičiūtė-Vileniškė, I. (2019). Hedonic analysis of housing prices and development in Kaunas: heritage aspect. *Environmental Research, Engineering and Management* 75(2), 15–27. doi:10.5755/j01.erem.75.2.22823. Laurinavičius, A., Laurinavičius, A., and Laurinavičius, A. (2022). Macroeconomic variables influencing housing prices in Vilnius. *International Journal of Strategic Property Management* 26(1), 24–34. doi:10.3846/ijspm.2021.15961.

---

## 6. Anticipated questions, and how to answer them

**"Why aren't these results causal?"**
Because nothing in a cross-sectional snapshot varies independently of everything else. The Vilnius premium
could be genuine location value, or it could be that Vilnius listings in this sample happen to have better
unobserved quality (finishes, views, condition) that correlates with being in the capital. Getting to
causality would need: panel data (the same unit observed repeatedly, to use fixed effects), a randomized
experiment, a sharp discontinuity (RDD), an instrument (IV), or a policy shock with a control group (DiD),
none of which this single-snapshot dataset has.

**"Doesn't 'hedonic' mean something about pleasure?"**
Same Greek root (*hēdonē*), but in economics it's a neutral technical term for "decompose a price into
attribute-level prices". It carries no value judgment about whether the result is good or accurate.

**"Is a 64% R² good?"**
It's a reasonable result for a cross-sectional hedonic model with no renovation/condition data, but frame it
as "size, rooms, age, heating and location jointly explain 64% of rent variation" rather than claiming
precision it doesn't have. Mention the within-Vilnius 76% result as evidence that finer location data
would likely close more of that gap.

**"What's the single most interesting finding?"**
Slide 14/15: location alone explains more of the model's fit than building age, floor position, and heating
type *combined*. That's the one number worth leading with if someone only remembers one thing.

---

## 7. Honest caveats about this repository

- The deck is a Typst source (`slides/deck.typ`) that rebuilds deterministically to `deck.pdf` on any machine
  with Typst 0.15 or newer. All 20 pages were rendered to images and checked for layout overflow before
  hand-off. There is no PowerPoint export: the PDF is the deck.
- The dataset is a **single scrape** (November 2026) of **currently-live listings**, not a random sample of
  the rental market, and not a time series. Units that rent instantly never appear.
- `alldataaruodas.txt` was manually copy-pasted from aruodas.lt, not scraped via an API. This was a
  deliberate choice after two earlier approaches (browser screenshot automation + OCR) both proved unreliable
  on this data.
