"""
decomposition.py - extra insights for the hedonic deck: sequential R^2
decomposition by block, raw-vs-adjusted city rent gaps, and coefficients
translated into euro amounts. Reuses the same cleaning as analysis.py.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[1]

df = pd.read_excel(ROOT / "data" / "processed" / "listings.xlsx")

df["city"] = df["location"].str.split(",").str[0].str.strip()
top_cities = {"Vilnius", "Kaunas", "Klaipėda", "Šiauliai", "Palanga", "Panevėžys"}
df["city_grp"] = np.where(df["city"].isin(top_cities), df["city"], "Other")

def primary_heating(h):
    if pd.isna(h) or not str(h).strip():
        return "Unknown"
    first = str(h).split(",")[0].strip()
    buckets = {
        "Centrinis": "Centrinis", "Centrinis kolektorinis": "Centrinis kolektorinis",
        "Dujinis": "Dujinis", "Elektra": "Elektra",
    }
    return buckets.get(first, "Other")

df["heat_grp"] = df["heating"].apply(primary_heating)

reg = df.copy()
reg = reg[(reg["year_built"] >= 1800) & (reg["year_built"] <= 2026)]
reg = reg[(reg["price_eur"] >= 100) & (reg["price_eur"] <= 5000)]
reg = reg.dropna(subset=["price_eur", "area_m2", "rooms", "floor", "floor_total", "year_built", "city_grp", "heat_grp"])
reg = reg[reg["rooms"] <= 6]
reg["age"] = 2026 - reg["year_built"]
reg["log_price"] = np.log(reg["price_eur"])
reg["floor_ratio"] = reg["floor"] / reg["floor_total"]

MEAN_RENT = reg["price_eur"].mean()

# ---- 1. sequential R^2 decomposition, by block ---------------------------
blocks = [
    ("Size & layout", "log_price ~ area_m2 + rooms"),
    ("+ building age/floor", "log_price ~ area_m2 + rooms + age + floor_ratio"),
    ("+ heating", "log_price ~ area_m2 + rooms + age + floor_ratio + C(heat_grp)"),
    ("+ location (city)", "log_price ~ area_m2 + rooms + age + floor_ratio + C(heat_grp) + C(city_grp)"),
]
seq = []
prev_r2 = 0.0
for label, formula in blocks:
    m = smf.ols(formula, data=reg).fit()
    seq.append({
        "block": label,
        "r2_cumulative": round(m.rsquared, 4),
        "r2_marginal": round(m.rsquared - prev_r2, 4),
    })
    prev_r2 = m.rsquared

# ---- 2. raw vs. adjusted city gap -----------------------------------------
# raw: unconditional mean log_price gap vs Kaunas (the regression's omitted baseline)
raw_mean = reg.groupby("city_grp")["log_price"].mean()
baseline = raw_mean["Kaunas"]
main_formula = "log_price ~ area_m2 + rooms + age + floor_ratio + C(heat_grp) + C(city_grp)"
main_model = smf.ols(main_formula, data=reg).fit(cov_type="HC1")
adj_coefs = {
    "Vilnius": main_model.params.get("C(city_grp)[T.Vilnius]", 0.0),
    "Klaipėda": main_model.params.get("C(city_grp)[T.Klaipėda]", 0.0),
    "Palanga": main_model.params.get("C(city_grp)[T.Palanga]", 0.0),
    "Šiauliai": main_model.params.get("C(city_grp)[T.Šiauliai]", 0.0),
    "Panevėžys": main_model.params.get("C(city_grp)[T.Panevėžys]", 0.0),
}
city_gap = []
for city in ["Vilnius", "Klaipėda", "Palanga", "Šiauliai", "Panevėžys"]:
    raw_gap = raw_mean[city] - baseline
    adj_gap = adj_coefs[city]
    city_gap.append({
        "city": city,
        "raw_pct": round((np.exp(raw_gap) - 1) * 100, 1),
        "adjusted_pct": round((np.exp(adj_gap) - 1) * 100, 1),
        "composition_pct": round((np.exp(raw_gap) - 1) * 100 - (np.exp(adj_gap) - 1) * 100, 1),
    })

# ---- 3. coefficients translated to euros, at the sample mean rent ---------
coefs_for_euro = {
    "One extra room": main_model.params["rooms"],
    "+10 m²": main_model.params["area_m2"] * 10,
    "Vilnius vs. Kaunas": main_model.params.get("C(city_grp)[T.Vilnius]", 0.0),
    "Šiauliai vs. Kaunas": main_model.params.get("C(city_grp)[T.Šiauliai]", 0.0),
    "Centrinis kolektorinis vs. Centrinis": main_model.params.get("C(heat_grp)[T.Centrinis kolektorinis]", 0.0),
    "+10 years of age": main_model.params["age"] * 10,
}
euros = []
for label, coef in coefs_for_euro.items():
    euros.append({
        "effect": label,
        "pct": round((np.exp(coef) - 1) * 100, 1),
        "euro_at_mean": round(MEAN_RENT * (np.exp(coef) - 1), 0),
    })

results = {
    "mean_rent": round(MEAN_RENT, 0),
    "sequential_r2": seq,
    "city_gap_decomposition": city_gap,
    "euro_effects": euros,
}

with open(ROOT / "results" / "decomposition_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(json.dumps(results, indent=2, ensure_ascii=False))
