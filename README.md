# What Determines Apartment Rent? A hedonic pricing study of the Lithuanian rental market

This repository is the complete, reproducible project behind a slide deck analyzing **2,662 rental
listings scraped from [aruodas.lt](https://www.aruodas.lt)**, Lithuania's largest real-estate portal, across
6 cities plus smaller towns. It was built as an Empirical Finance course project. This document describes the
data, the pipeline, the model, the results and the deck.

> **Scope note.** An earlier draft of this project also explored a separate question: comparing rental
> property returns against the S&P 500 over 3–5 year holding periods, including Lithuanian tax rules and a
> downside-hedging scenario. That thread was dropped, and it is not part of this repository.

---

## 1. What's in this repository

```
.
├── data/
│   ├── raw/alldataaruodas.txt      Raw scrape: pasted text dump of aruodas.lt listing pages
│   └── processed/listings.xlsx     The cleaned dataset (2,662 rows), the single source of truth
├── results/
│   ├── analysis_results.json       Numeric output of scripts/analysis.py (every coefficient, SE, p-value, diagnostic)
│   └── decomposition_results.json  Numeric output of scripts/decomposition.py
├── scripts/
│   ├── build_listings.py           Parses the raw text into data/processed/listings.xlsx
│   ├── analysis.py                 Main hedonic regression + logit + Vilnius-district robustness model
│   └── decomposition.py            Extra analysis: sequential R² decomposition, city-gap decomposition, € effects
├── pyproject.toml                  Project metadata and Python dependencies (uv)
├── uv.lock                         Locked dependency set, committed
└── slides/
    ├── deck.typ                    The deck source (Typst, 21 slides, 16:9, no packages)
    ├── deck.pdf                    The built deck (21 pages)
    ├── make_charts.py              Renders the 7 "visual evidence" charts for the main deck
    ├── decomposition_charts.py     Renders the 2 decomposition charts (sequential R², city-gap)
    └── assets/                     Chart images plus the VU facets and mark used on the title slides
```

**Everything regenerates from `data/raw/alldataaruodas.txt` alone.** Nothing here is hand-edited data. Every
number on every slide traces back through a script to that raw text file.

---

## 2. The data pipeline

1. **`data/raw/alldataaruodas.txt`**: a manual copy-paste of aruodas.lt rental listing pages (not an API scrape or
   OCR of screenshots, because both were tried earlier in this project and were unreliable; plain copy-pasted text
   turned out to be the most faithful source).
2. **`scripts/build_listings.py`** parses that text into `data/processed/listings.xlsx`: 2,662 listings with columns for city,
   street, price, any recorded price change, deposit, rooms, area, floor / total floors, year built,
   heating type, and listing type.
3. **`scripts/analysis.py`** cleans that further for regression: drops 22 listings with implausible build years
   (before 1800) or rents outside €100–5,000, leaving **N = 2,640**. This is the sample every statistic in
   the main deck is built on.

---

## 3. The methodology, in plain terms

**Hedonic regression** means: treat an apartment as a bundle of priced attributes (size, rooms, floor, age,
heating, location) and estimate how much each attribute is worth by regressing total rent on all of them at
once. It is a *descriptive* technique, not inherently causal or non-causal. This study's results are correlational, not causal. See §6 for the interpretation notes.

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
| Decomposition | How much does each *block* of variables actually contribute? | Location, added last, still adds **15.3 R² points**: more than age, floor, and heating *combined* (which add 2.7 + 5.6 = 8.3 points) |
| Secondary outcome: price cuts | What predicts a listing getting marked down? | Pseudo R² = 0.013: almost nothing does, except floor position (lower floors are discounted far more often) |

---

## 4. How to rebuild everything from scratch

```bash
# 0. Create the environment (uv 0.10+, Python 3.12+)
uv sync                             # builds .venv from uv.lock, exact versions

# 1. Rebuild the dataset from the raw scrape
uv run python scripts/build_listings.py     # → data/processed/listings.xlsx

# 2. Run the regressions
uv run python scripts/analysis.py           # → results/analysis_results.json, prints full regression summaries
uv run python scripts/decomposition.py      # → results/decomposition_results.json

# 3. Render chart images
uv run python slides/make_charts.py        # → slides/assets/hist_price.png, scatter_area_rooms.png, fit.png, resid.png,
                                     #   coefplot.png, bars_city_district.png, pricecut_floor.png
uv run python slides/decomposition_charts.py   # → slides/assets/seq_r2.png, city_gap_decomp.png

# 4. Build the deck (needs Typst 0.15 or newer, nothing else)
typst compile slides/deck.typ       # → slides/deck.pdf
```

`slides/deck.pdf` is the built artifact. Equations are typeset by Typst itself, so there are no equation images to
rebuild, and the page count, margins and type are fixed by `slides/deck.typ` alone.

Python dependencies are uv-managed: `pyproject.toml` declares them, `uv.lock` pins the resolution, and
`uv sync` builds `.venv`. Every script resolves its paths from its own location, so `uv run python ...` works
from any directory. The deck needs no Python packages and no npm packages.

---

## 5. Deck contents: `slides/deck.pdf` (21 slides)

`slides/deck.typ` compiles to a 21-page PDF, styled after the Vilnius University wildcat theme: burgundy
titles, a gold rule, and a monochrome figure style. Equations are typeset by Typst, so the deck contains no
equation images.

| # | Section | Slide | Contents |
|---|---|---|---|
| 1 | None | Title | Title, author names and contact addresses, and the sample description: November 2026, cross-sectional. |
| 2 | 1 · Question and approach | Question, evidence, gap | The research question, three Lithuanian studies (Raslanas et al. 2006; Rudokas et al. 2019; Laurinavičius et al. 2022), the gap and the contribution. States that the estimates are descriptive correlations. |
| 3 | 2 · The sample | 2,662 listings, 6 cities plus smaller towns | Mean rent €699, mean area 49.5 m², mean year built 1988. The city table covers all 2,662 listings and the heating table covers the 2,640 regression listings. |
| 4 | 3 · Model | Model | The regression equation, the definitions of floor ratio and age, OLS with HC1 standard errors, and the reference categories Centrinis heating and Kaunas. |
| 5 | 3 · Model | Why model rent in logs? | Rent histograms in levels and in logs. The log transform is close to symmetric, which is why coefficients read as percentage effects. |
| 6 | 4 · Results | Main regression | Coefficients, robust standard errors and p-values. Main estimates are +0.9%/m², +15%/room and a Vilnius premium of +15% over Kaunas. R² is 0.638 with N = 2,640. Floor ratio is not significant for rent level (p = 0.226). |
| 7 | 4 · Results | Rent vs. size and room count | Scatter plots of log rent against area and against room count, with fitted lines. |
| 8 | 4 · Results | Robustness checks | Five alternatives: area in logs, street-clustered standard errors, a price sample trimmed to the 1st and 99th percentiles, duplicate ads dropped, and the 177 influential rows dropped. Also names the two findings that can overturn the result. |
| 9 | 4 · Results | Coefficients, visually | The main coefficients as point estimates with 95% confidence intervals. |
| 10 | 5 · Diagnostics | Is the model well specified? | Breusch-Pagan (χ² = 148.5, p < 0.001), variance inflation factors (all at most 2.61), and 177 influential listings by Cook's distance. |
| 11 | 5 · Diagnostics | How well does the model fit? | Predicted against actual log rent with the 45 degree line, showing the R² of 0.638 from the main model. |
| 12 | 5 · Diagnostics | Residual diagnostics | Residuals against fitted values and a normal Q-Q plot. The heteroskedasticity and the heavy right tail motivate the HC1 standard errors. |
| 13 | 6 · Extension | Zooming in: Vilnius by district | Vilnius-only model with district fixed effects. R² rises from 0.649 to 0.762 on the same 1,393 listings. Percentage effects are exact and measured against Antakalnis. |
| 14 | 6 · Extension | Location effects, visually | City effects and Vilnius-district effects as bar charts. |
| 15 | 7 · Decomposition | Where does the fit come from? | Sequential R² by block: size and layout 40.3 points, building age and floor +2.7, heating +5.6, location +15.3. |
| 16 | 7 · Decomposition | Location adds more than age, floor and heating | The decomposition stated as a result: added last, location still contributes 15.3 R² points against 8.3 for the other blocks. |
| 17 | 7 · Decomposition | Is the city gap real, or just composition? | Raw and adjusted city gaps against Kaunas. Vilnius shows +17.9% raw and +15.5% adjusted. Šiauliai and Panevėžys lose about a fifth of their discount to composition. |
| 18 | 8 · Secondary outcome | Who gets a price cut? | Logit on a price cut, which occurs in 24.9% of listings. Floor ratio is the strongest predictor (p < 0.001), building age is marginally significant (p = 0.041), and pseudo R² is 0.013. |
| 19 | 8 · Secondary outcome | Price cuts by floor position | Price-cut rate by floor-ratio quintile. |
| 20 | 9 · Limitations and takeaways | What this is worth, and what it is not | Takeaways and limitations: no causal identification, omitted variables, single snapshot. |
| 21 | None | Thank you | Closing slide with the repository link. |

### Short build

`typst compile slides/deck.typ slides/deck-short.pdf --input short=true` builds an 8-page cut from the same
source. It keeps slides 1, 2, 6, 13, 16, 18, 20 and 21 and drops the rest at render time. No content is
duplicated.

**References cited on slide 2.** Raslanas, S., Šteinbergas, T., and Tupenaite, L. (2006). Research on the prices of flats in the South East London and Vilnius. *International Journal of Strategic Property Management* 10(1), 51–63. doi:10.3846/1648715X.2006.9637544. Rudokas, K., Landauskas, M., Viliūnienė, O., and Gražulevičiūtė-Vileniškė, I. (2019). Hedonic analysis of housing prices and development in Kaunas: heritage aspect. *Environmental Research, Engineering and Management* 75(2), 15–27. doi:10.5755/j01.erem.75.2.22823. Laurinavičius, A., Laurinavičius, A., and Laurinavičius, A. (2022). Macroeconomic variables influencing housing prices in Vilnius. *International Journal of Strategic Property Management* 26(1), 24–34. doi:10.3846/ijspm.2021.15961.

---

## 6. How to read the results

**Causal status.** The design is a single cross-section, so no coefficient identifies a causal effect. The
Vilnius premium can be location value or unobserved quality that correlates with location. Causal claims
would need panel data with unit fixed effects, an experiment, a regression discontinuity, an instrument, or a
policy shock with a control group. None of these is available in a single scrape.

**Hedonic terminology.** The word shares its Greek root with the everyday sense of pleasure, but in
economics it is a neutral term for decomposing a price into attribute prices.

**R².** A value of 0.638 means the model explains 64 percent of the variation in log rent in this sample. It
is a reasonable value for a cross-sectional model without renovation or condition data. Within Vilnius,
district fixed effects raise it to 0.762.

**The decomposition.** The sequential decomposition is the main analytical result. Location, added last,
contributes 15.3 R² points, more than building age, floor position and heating together, which contribute 8.3.

---

## 7. Honest caveats about this repository

- The deck is a Typst source (`slides/deck.typ`) that rebuilds deterministically to `deck.pdf` on any machine
  with Typst 0.15 or newer. All 21 pages were rendered to images and checked for layout overflow. There is
  no PowerPoint export, so the PDF is the deck.
- The dataset is a **single scrape** (November 2026) of **currently-live listings**, not a random sample of
  the rental market, and not a time series. Units that rent instantly never appear.
- `data/raw/alldataaruodas.txt` was manually copy-pasted from aruodas.lt, not scraped via an API. This was a
  deliberate choice after two earlier approaches (browser screenshot automation + OCR) both proved unreliable
  on this data.
