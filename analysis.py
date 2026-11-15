"""
analysis.py - hedonic pricing regression on the aruodas.lt rental listings
(listings.xlsx), plus a secondary logit on price cuts. Produces the numbers
used in the slide deck.
"""
import json

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor

df = pd.read_excel("listings.xlsx")

# ---- cleaning ----------------------------------------------------------
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

n0 = len(df)
reg = df.copy()
reg = reg[(reg["year_built"] >= 1800) & (reg["year_built"] <= 2026)]
reg = reg[(reg["price_eur"] >= 100) & (reg["price_eur"] <= 5000)]
reg = reg.dropna(subset=["price_eur", "area_m2", "rooms", "floor", "floor_total", "year_built", "city_grp", "heat_grp"])
reg = reg[reg["rooms"] <= 6]
reg["age"] = 2026 - reg["year_built"]
reg["log_price"] = np.log(reg["price_eur"])
reg["floor_ratio"] = reg["floor"] / reg["floor_total"]
n1 = len(reg)

# ---- main hedonic regression (OLS, robust SE) ---------------------------
formula = "log_price ~ area_m2 + rooms + age + floor_ratio + C(heat_grp) + C(city_grp)"
model = smf.ols(formula, data=reg).fit(cov_type="HC1")

# ---- diagnostics ---------------------------------------------------------
bp = het_breuschpagan(model.resid, model.model.exog)
bp_stat, bp_pvalue = bp[0], bp[1]

X_vif = reg[["area_m2", "rooms", "age", "floor_ratio"]].assign(const=1)
vif = {col: variance_inflation_factor(X_vif.values, i) for i, col in enumerate(X_vif.columns) if col != "const"}

cooks = model.get_influence().cooks_distance[0]
n_influential = int((cooks > 4 / len(reg)).sum())

# ---- secondary logit: predictors of a price cut --------------------------
reg["price_cut"] = (reg["price_change_dir"] == "sumazejo").astype(int)
logit_formula = "price_cut ~ area_m2 + rooms + age + floor_ratio + C(heat_grp) + C(city_grp)"
logit_model = smf.logit(logit_formula, data=reg).fit(disp=0)

# ---- Vilnius-only district fixed effects (robustness/extension) ----------
vil = reg[reg["city_grp"] == "Vilnius"].copy()
vil["district"] = vil["location"].str.split(",").str[1].str.strip()
dist_counts = vil["district"].value_counts()
vil["district_grp"] = np.where(vil["district"].isin(dist_counts[dist_counts >= 15].index), vil["district"], "Other")
vil_formula = "log_price ~ area_m2 + rooms + age + floor_ratio + C(heat_grp) + C(district_grp)"
vil_model = smf.ols(vil_formula, data=vil).fit(cov_type="HC1")

# ---- package results for the slides --------------------------------------
def coef_table(res, round_coef=4):
    out = []
    for name in res.params.index:
        out.append({
            "name": name,
            "coef": round(res.params[name], round_coef),
            "se": round(res.bse[name], round_coef),
            "t": round(res.tvalues[name], 2),
            "p": round(res.pvalues[name], 4),
        })
    return out

results = {
    "n_total": n0,
    "n_regression": n1,
    "n_dropped": n0 - n1,
    "main_model": {
        "formula": formula,
        "n": int(model.nobs),
        "r2": round(model.rsquared, 4),
        "r2_adj": round(model.rsquared_adj, 4),
        "f_stat": round(model.fvalue, 2),
        "f_pvalue": float(model.f_pvalue),
        "coefs": coef_table(model),
    },
    "diagnostics": {
        "breusch_pagan_stat": round(bp_stat, 2),
        "breusch_pagan_p": round(bp_pvalue, 4),
        "vif": {k: round(v, 2) for k, v in vif.items()},
        "n_influential_cooks": n_influential,
        "cooks_threshold": round(4 / len(reg), 5),
    },
    "logit_model": {
        "formula": logit_formula,
        "n": int(logit_model.nobs),
        "pseudo_r2": round(logit_model.prsquared, 4),
        "pct_price_cuts": round(reg["price_cut"].mean() * 100, 1),
        "coefs": coef_table(logit_model),
    },
    "vilnius_model": {
        "formula": vil_formula,
        "n": int(vil_model.nobs),
        "r2": round(vil_model.rsquared, 4),
        "r2_adj": round(vil_model.rsquared_adj, 4),
        "coefs": coef_table(vil_model),
    },
    "city_counts": df["city_grp"].value_counts().to_dict(),
    "heat_counts": reg["heat_grp"].value_counts().to_dict(),
}

with open("analysis_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(model.summary())
print()
print("Breusch-Pagan:", bp_stat, bp_pvalue)
print("VIF:", vif)
print("Influential (Cook's D):", n_influential, "/", len(reg))
print()
print(logit_model.summary())
print()
print(vil_model.summary())
