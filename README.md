# What Determines Apartment Rent? — a hedonic pricing study of the Lithuanian rental market

This repository is the complete, reproducible project behind a slide deck analyzing **2,662 rental
listings scraped from [aruodas.lt](https://www.aruodas.lt)**, Lithuania's largest real-estate portal, across
7 cities. It was built as an Empirical Finance course project. This document explains what was done, why,
and — most importantly — **what every slide in the deck means**, so that someone who didn't build the
analysis can still present it confidently or review it critically.

> **Scope note.** An earlier draft of this project also explored a separate question — comparing rental
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
├── listings.xlsx                   The cleaned dataset (2,662 rows) — the single source of truth
├── analysis.py                     Main hedonic regression + logit + Vilnius-district robustness model
├── analysis_results.json           Numeric output of analysis.py (every coefficient, SE, p-value, diagnostic)
├── decomposition.py                Extra analysis: sequential R² decomposition, city-gap decomposition, € effects
├── decomposition_results.json      Numeric output of decomposition.py
└── slides/
    ├── deck.html                   The main deck as a self-contained, keyboard-navigable HTML slideshow
    ├── build_deck.js               Generates Rental_Price_Hedonics.pptx (pptxgenjs script)
    ├── render_equations.py         Renders every LaTeX equation image used in the pptx (matplotlib mathtext)
    ├── make_charts.py              Renders the 7 "visual evidence" charts for the main deck
    ├── decomposition_charts.py     Renders the 2 decomposition charts (sequential R², city-gap)
    ├── apply_theme.js              Small helper: writes the monochrome theme colors into a pptxgenjs-built .pptx
    ├── package.json / package-lock.json   Node dependency pin (pptxgenjs)
    ├── assets/*.png                All chart and equation images used by the deck
    └── Rental_Price_Hedonics.pptx  ⭐ The deck — 20 slides
```

**Everything regenerates from `alldataaruodas.txt` alone.** Nothing here is hand-edited data — every
number on every slide traces back through a script to that raw text file.

---

## 2. The data pipeline

1. **`alldataaruodas.txt`** — a manual copy-paste of aruodas.lt rental listing pages (not an API scrape or
   OCR of screenshots — both were tried earlier in this project and were unreliable; plain copy-pasted text
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
once. It is a *descriptive* technique, not inherently causal or non-causal — see §5 for why this particular
study's results are correlational, not causal.

**The model** (log-linear, so coefficients read as approximate % effects):

```
ln(Price_i) = β₀ + β₁·Area_i + β₂·Rooms_i + β₃·Age_i + β₄·FloorRatio_i
              + Σ γ_k·Heating_ik + Σ δ_j·City_ij + ε_i
```

- `FloorRatio_i = Floor_i / TotalFloors_i` — relative height in the building (0 = ground floor, 1 = top floor)
- Reference (omitted) categories: **Centrinis heating**, **Kaunas** city
- Estimated by OLS with **HC1 heteroskedasticity-robust standard errors**, because a Breusch–Pagan test
  (χ² = 148.5, p < 0.001) confirms the residual variance isn't constant — expected for rent levels, and the
  reason classical OLS standard errors would be wrong here.

**Headline result:** R² = 0.638 (adj. 0.636), N = 2,640. Four analyses build on this:

| Analysis | What it adds | Key number |
|---|---|---|
| Diagnostics | Is the model trustworthy? | VIF all ≤ 2.61 (no multicollinearity problem); 177/2,640 (6.7%) influential points by Cook's distance, consistent with luxury-unit outliers, not data errors |
| Vilnius-district extension | Does location matter *within* a city, not just between cities? | Swapping the city dummy for Vilnius-district fixed effects raises R² to **0.762** (N = 1,393) |
| Decomposition (new) | How much does each *block* of variables actually contribute? | Location alone adds **15.3 R² points** — more than age, floor, and heating *combined* (which add 2.7 + 5.6 = 8.3 points) |
| Secondary outcome: price cuts | What predicts a listing getting marked down? | Pseudo R² = 0.013 — almost nothing does, except floor position (lower floors are discounted far more often) |

---

## 4. How to rebuild everything from scratch

```bash
# 1. Rebuild the dataset from the raw scrape
python build_listings.py            # → listings.xlsx

# 2. Run the regressions
python analysis.py                  # → analysis_results.json, prints full regression summaries
python decomposition.py             # → decomposition_results.json

# 3. Render chart & equation images (run from inside slides/)
cd slides
python render_equations.py          # → assets/eq_main.png, eq_vars.png, eq_logit.png
python make_charts.py               # → assets/hist_price.png, scatter_area_rooms.png, fit.png, resid.png,
                                     #   coefplot.png, bars_city_district.png, pricecut_floor.png
python decomposition_charts.py      # → assets/seq_r2.png, city_gap_decomp.png

# 4. Build the PowerPoint deck (needs Node.js)
npm install                         # installs pptxgenjs into slides/node_modules
node build_deck.js                  # → Rental_Price_Hedonics.pptx
```

`deck.html` is static — just open it in a browser (it loads MathJax from a CDN for the LaTeX equations and
needs the `assets/` folder alongside it). Arrow keys / swipe to navigate.

Required Python packages: `pandas`, `numpy`, `statsmodels`, `matplotlib`, `scipy`, `openpyxl`, `Pillow`.

---

## 5. Slide-by-slide guide: `Rental_Price_Hedonics.pptx` (main deck, 20 slides)

`deck.html` and the `.pptx` contain the same 20 slides in the same order — pick whichever format suits the
room (HTML for a laptop/browser, `.pptx` for PowerPoint/Keynote).

| # | Section | Slide | What it means / how to present it |
|---|---|---|---|
| 1 | — | Title | A hedonic pricing analysis of 2,662 listings. Say this is cross-sectional (one scrape, one point in time), not a time series. |
| 2 | 1 · Question and approach | Rent as a bundle of characteristics | Defines hedonic regression. **Say explicitly**: these are descriptive correlations, not causal effects — flag this up front so it isn't a surprise on slide 19. |
| 3 | 2 · The sample | 2,662 listings, 7 cities | Headline stats (mean rent €699, mean area 49.5 m², mean year built 1988) plus the city/heating breakdown. Mention the N drops from 2,662 to 2,640 for regression (22 implausible rows removed). |
| 4 | 3 · Model | Model | The regression equation, rendered properly (not as plain-text underscores). Walk through each term once — this is the one slide worth slowing down on, since everything else refers back to it. |
| 5 | 3 · Model | Why model rent in logs? | Justifies the log transform: raw rents are right-skewed (a few very expensive units pull the tail), logs are close to symmetric — this is *why* coefficients are read as % effects, not € effects. |
| 6 | 4 · Results | Main regression | The core results table. **Three numbers to memorize:** +0.9%/m², +14%/room, Vilnius +14% vs. Kaunas. Floor ratio is *not* significant here (p = 0.226) — worth noting, since it becomes very significant later (slide 17/18) for a different outcome (price cuts, not price level). |
| 7 | 4 · Results | Rent vs. size and room count | The two strongest raw bivariate relationships, visually — a sanity check that the regression's two biggest coefficients aren't spurious. |
| 8 | 4 · Results | Coefficients, visually | Same table as slide 6, as a dot-and-whisker (95% CI) plot — easier to scan which effects are precisely estimated (narrow CI) vs. noisy (floor ratio, Elektra heating, both straddle zero). |
| 9 | 5 · Diagnostics | Is the model well specified? | Three checks: heteroskedasticity (why HC1 SEs are used), multicollinearity (VIF — area/rooms correlate but not dangerously), influential points (177 high-leverage listings, explained as luxury-unit outliers). |
| 10 | 5 · Diagnostics | How well does the model fit? | Predicted vs. actual scatter. Points hugging the 45° line = good fit; the R² = 0.638 number from slide 6 made visual. |
| 11 | 5 · Diagnostics | Residual diagnostics | Residuals-vs-fitted + Q-Q plot — shows the mild heteroskedasticity and right-tail non-normality the Breusch–Pagan test flagged. This is "showing your work" for why HC1 SEs were the right call. |
| 12 | 6 · Extension | Zooming in: Vilnius by district | Swap city dummies for Vilnius-district fixed effects → R² jumps to 0.762. **Paupys (+44%)** and **Senamiestis/Old Town (+34%)** are the standout premium districts; **Naujoji Vilnia (−15%)** the standout discount. Message: location matters *within* a city just as much as *between* cities. |
| 13 | 6 · Extension | Location effects, visually | City effects and Vilnius-district effects side by side as bar charts — a visual summary of slides 6 and 12's location coefficients. |
| 14 | 7 · Decomposition | Where does the fit come from? | **This is the most important new analytical result in the deck.** A sequential/nested R² breakdown: Size & layout alone → 40.3 points of R²; + age/floor → 42.9 (+2.7); + heating → 48.5 (+5.6); + location → 63.8 (+15.3). Location is the single biggest contributor after raw size. |
| 15 | 7 · Decomposition | Location adds more than everything else combined | States the headline plainly: location's 15.3-point contribution beats age + floor + heating's combined 8.3 points. Also ties in the Vilnius-district result (R² → 0.762) as evidence that location keeps paying off at finer resolution. |
| 16 | 7 · Decomposition | Is the city gap real, or just composition? | A subtler point: is Vilnius more expensive because it's *actually* a better location, or just because Vilnius listings happen to be bigger/newer? Answer: for Vilnius, almost entirely genuine location (raw +17.9% gap vs. Kaunas, adjusted +15.5% — composition explains only ~2 points). For Šiauliai/Panevėžys, roughly a fifth of their discount is just smaller/older stock, not a "location penalty" as such. |
| 17 | 8 · Secondary outcome | Who gets a price cut? | Switches from predicting *rent level* to predicting *whether a listing gets marked down* (24.9% of listings do, logit model). Pseudo R² is tiny (0.013) — almost nothing in the hedonic model predicts discounting, **except floor ratio**, which is strongly significant here even though it wasn't for rent level. |
| 18 | 8 · Secondary outcome | Price cuts by floor position | Visual version of slide 17's one real finding: ground/low floors get discounted far more often than top floors. |
| 19 | 9 · Limitations and takeaways | What this is worth, and what it is not | **Read this slide out loud, don't rush it.** Takeaways: location > everything else combined; an extra room ≈ +€105/month; discounting is basically unpredictable except by floor. Limitations: not causal (§ below), omitted variables (renovation quality, exact micro-location, furnishings — all priced by the market, none observed here), single snapshot (no panel structure, so no time-on-market or landlord fixed effects possible). |
| 20 | — | Thank you | Closing slide. |

### If you only have 10 minutes
Present slides **1, 2, 6, 12, 14 (or 15), 17, 19** — title, framing, main results, the district extension, the
decomposition headline, the price-cut finding, and limitations. That's the whole argument in 7 slides.

---

## 6. Anticipated questions, and how to answer them

**"Why aren't these results causal?"**
Because nothing in a cross-sectional snapshot varies independently of everything else. The Vilnius premium
could be genuine location value, or it could be that Vilnius listings in this sample happen to have better
unobserved quality (finishes, views, condition) that correlates with being in the capital. Getting to
causality would need: panel data (the same unit observed repeatedly, to use fixed effects), a randomized
experiment, a sharp discontinuity (RDD), an instrument (IV), or a policy shock with a control group (DiD) —
none of which this single-snapshot dataset has.

**"Doesn't 'hedonic' mean something about pleasure?"**
Same Greek root (*hēdonē*), but in economics it's a neutral technical term for "decompose a price into
attribute-level prices" — it carries no value judgment about whether the result is good or accurate.

**"Is a 64% R² good?"**
It's a reasonable result for a cross-sectional hedonic model with no renovation/condition data, but frame it
as "size, rooms, age, heating and location jointly explain 64% of rent variation" rather than claiming
precision it doesn't have — and mention the within-Vilnius 76% result as evidence that finer location data
would likely close more of that gap.

**"What's the single most interesting finding?"**
Slide 14/15: location alone explains more of the model's fit than building age, floor position, and heating
type *combined*. That's the one number worth leading with if someone only remembers one thing.

---

## 7. Honest caveats about this repository

- **No visual render QA was possible** on the machine this was built on (no LibreOffice available) — the
  `.pptx` files were validated for file-format correctness and checked for text-content accuracy, but never
  visually rendered and eyeballed before being handed off. Open both decks once yourself before presenting.
- The dataset is a **single scrape** (November 2026) of **currently-live listings** — not a random sample of
  the rental market, and not a time series. Units that rent instantly never appear.
- `alldataaruodas.txt` was manually copy-pasted from aruodas.lt, not scraped via an API — this was a
  deliberate choice after two earlier approaches (browser screenshot automation + OCR) both proved unreliable
  on this data.
