# PROJECT KNOWLEDGE BASE

**Generated:** 2026-11-16
**Commit:** 28b6572 (working tree: Typst deck conversion)
**Branch:** main

## OVERVIEW
Hedonic pricing study of 2,662 aruodas.lt rental listings (7 cities): Python (pandas/statsmodels) regression pipeline plus a 20-slide Typst deck styled on the VU wildcat theme. Everything regenerates from one hand-pasted text dump — no scraped or hand-edited data.

## STRUCTURE
```
./
├── alldataaruodas.txt      # raw copy-paste of listing pages; the only true input
├── build_listings.py       # parser: text -> listings.xlsx (regex field-block walk)
├── listings.xlsx           # clean dataset, 2,662 rows == single source of truth for analysis
├── analysis.py             # main OLS + logit + Vilnius-district extension -> analysis_results.json
├── decomposition.py        # sequential R^2, city-gap decomposition, EUR effects
├── pyproject.toml           # project metadata + dependencies (uv)
├── uv.lock                  # committed lockfile; `uv sync` builds .venv
└── slides/
    ├── deck.typ            # Typst deck source: 20 slides, 16x9 cm, no packages
    ├── deck.pdf            # built deck (typst compile deck.typ)
    ├── make_charts.py      # 7 main-deck figures (re-estimates models itself)
    ├── decomposition_charts.py  # 2 figures, reads ../decomposition_results.json only
    └── assets/             # chart PNGs + facets.svg + vu-logo-white.png
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Change dataset columns/parsing | `build_listings.py:44` | `SRC`/`OUT` are repo-relative (`Path(__file__).with_name(...)`); column list at line 244 |
| Change regression spec | `analysis.py:50` | `formula = "log_price ~ area_m2 + rooms + age + floor_ratio + C(heat_grp) + C(city_grp)"` |
| Change R^2 decomposition | `decomposition.py` | output shape at `results = {...}` |
| Restyle any figure | `slides/make_charts.py:13` | shared `plt.rcParams` block; `savefig` helper |
| Slide text/layout | `slides/deck.typ` | one `#slide(section, title)[...]` block per page, in order |
| Deck theme/palette | `slides/deck.typ:6-16` | `vu`, `vu-10..vu-70`, `gold`, `ink`, `grey` — mirrors the VU wildcat theme |
| Numbers quoted in prose | `analysis_results.json`, `decomposition_results.json` | prose must match JSON, not memory |
| Narrative/defense of method | `README.md` | slide-by-slide guide + anticipated Q&A |

## CODE MAP
No package index, no exports between modules: the pipeline is file-based.

| Symbol | Type | Location | Refs | Role |
|--------|------|----------|------|------|
| `main` | func | `build_listings.py:67` | — | Walks non-blank lines, anchors on `Prieš <date>` regex, parses fixed field block |
| `primary_heating` | func | `analysis.py:22`, `decomposition.py:18`, `slides/make_charts.py:36` | — | Buckets heating text to first comma token; **copied verbatim 3x** |
| `coef_table` | func | `analysis.py:73` | 3 | Rounds params/SE/t/p into the JSON the slides quote |
| `slide` / `fig` / `vtable` / `note` / `head2` / `stat` | Typst fns | `slides/deck.typ:38-90` | every page | Deck primitives: page frame with kicker + gold rule + page number, image+caption, zebra table, small aside |
| `savefig` | func | `slides/make_charts.py:66`, `slides/decomposition_charts.py:30` | ~10 | Writes `assets/<name>.png` at DPI 220 |

## CONVENTIONS
- Dependencies are uv-managed: `pyproject.toml` + committed `uv.lock` (`package = false`, so uv never builds the project). `uv sync`, then `uv run python ...` from the repo root or from `slides/`. Do not `pip install` into `.venv`; add packages with `uv add`.
- **cwd is part of the interface.** `analysis.py`/`decomposition.py` read `listings.xlsx` relative to the repo root; every `slides/*.py` reads `../listings.xlsx` or `../decomposition_results.json` and writes `assets/`. Run them from their own directory. `build_listings.py` is exempt: it resolves paths from `__file__`.
- **Cleaning block is duplicated on purpose** (self-contained renderers): `year_built 1800..2026`, `price_eur 100..5000`, `rooms <= 6`, `dropna`, `age = 2026 - year_built` appears in `analysis.py`, `decomposition.py`, `slides/make_charts.py`. Editing one means editing all three or results diverge silently.
- `age` uses a **hardcoded reference year 2026**; there is no "today" call anywhere.
- `price_change_dir` is stored ASCII-normalized: `"padidejo"` / `"sumazejo"` / `""`. The logit target is `== "sumazejo"` — do not reintroduce diacritics.
- Reference categories are implicit (statsmodels alphabetical): **Centrinis** heating, **Kaunas** city. Deck language treats coefficients as log points and says so on the Model slide; `decomposition.py` euro effects use `exp(beta) - 1`.
- All models use `cov_type="HC1"`; logit uses `.fit(disp=0)`.
- JSON outputs: `json.dump(..., indent=2, ensure_ascii=False)`.
- Figure style is monochrome by contract: serif + `mathtext.fontset="cm"`, black/gray `#555555`, grid `#dddddd`, DPI 220, no top/right spines. Charts carry no titles duplicated by the deck.
- Deck style: 16x9 cm pages, top margin 1.85 cm, body 9.5 pt, TeX Gyre Adventor/Heros with Inter/DejaVu fallbacks, burgundy `#7D2035` + gold `#FFD100`, pages numbered `n / 20`.
- Figures are sized by **one** dimension (`width:` for landscape, `height:` for portrait); Typst keeps the aspect ratio, so chart figsize changes need no deck edit.

## ANTI-PATTERNS (THIS PROJECT)
- **NEVER hand-edit** `listings.xlsx`, `analysis_results.json`, `decomposition_results.json`, `slides/assets/*.png`, or `slides/deck.pdf`; all are generated.
- Do not run `slides/*.py` from the repo root: image paths resolve to `assets/` and data to `../`.
- Do not add a second deck target (pptx/html) without a source of truth: the converted deck is `slides/deck.typ` only.
- Do not hardcode coefficients in chart scripts — read them from the fitted model or the JSON (`make_charts.py` district effects come from `vil_model.params`).
- Do not exceed the page body height (6.4 cm): Typst silently pushes the overflow onto a new page, so always check the compiled page count is 20.
- Do not phrase findings causally. README §6 is explicit: cross-sectional snapshot, no identification strategy.
- Do not re-introduce the equation PNGs: Typst typesets the math natively.

## COMMANDS
```bash
uv sync                             # .venv from uv.lock (uv 0.10+, Python 3.12+)

# dataset
uv run python build_listings.py     # -> listings.xlsx (2,662 rows)

# analysis, from repo root
uv run python analysis.py           # -> analysis_results.json + printed model summaries
uv run python decomposition.py      # -> decomposition_results.json

# figures + deck, from slides/
cd slides
uv run python make_charts.py        # -> 7 chart PNGs
uv run python decomposition_charts.py   # -> assets/seq_r2.png, city_gap_decomp.png
typst compile deck.typ              # -> deck.pdf (20 pages)

# page-level QA
typst compile deck.typ '{p}.png' --ppi 110   # one PNG per page, for visual checks
```
No tests, no CI. Typst 0.15+ is the only deck dependency.

## NOTES
- Sample: 2,662 parsed -> 2,640 in regressions (22 implausible build years/rents dropped). Charts re-run their own estimation, so they need `listings.xlsx`, not the JSONs — except `decomposition_charts.py`, which needs `decomposition.py` to have run first.
- `build_listings.py` emits three `listing_type` values: `standalone`, `project_main`, `project_unit` (bundle expansion after a `Daugiau butų projekte:` marker).
- Deck figures come from `slides/assets/`; the title and closing pages use `facets.svg` and `vu-logo-white.png` copied from the VU wildcat theme.
- Old deck targets (`deck.html`, `build_deck.js`, `apply_theme.js`, `package.json`, `render_equations.py`, `Rental_Price_Hedonics.pptx`) were removed in the Typst conversion; git history still has them.
- `price_cut` rate in the regression sample is 24.92% (deck says 24.9%); the logit's city/heating dummies all have p > 0.07 (lowest is "Other" at 0.0797).
