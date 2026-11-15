"""
make_charts.py - all-monochrome figures for the "visual material" slides.
Rebuilds the same models as ../analysis.py (kept self-contained here) and
renders each figure as a plain black-on-white PNG, matching the deck's
no-color, LaTeX-typeface style.
"""
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy import stats

plt.rcParams.update({
    "font.family": "serif",
    "mathtext.fontset": "cm",
    "text.color": "black", "axes.edgecolor": "black", "axes.labelcolor": "black",
    "xtick.color": "black", "ytick.color": "black",
    "axes.facecolor": "white", "figure.facecolor": "white",
    "axes.grid": True, "grid.color": "#dddddd", "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False,
    "font.size": 12,
})
GRAY = "#555555"
BLACK = "black"
DPI = 220

# ---- data + models (mirrors ../analysis.py) ------------------------------
df = pd.read_excel("../listings.xlsx")
df["city"] = df["location"].str.split(",").str[0].str.strip()
top_cities = {"Vilnius", "Kaunas", "Klaipėda", "Šiauliai", "Palanga", "Panevėžys"}
df["city_grp"] = np.where(df["city"].isin(top_cities), df["city"], "Other")

def primary_heating(h):
    if pd.isna(h) or not str(h).strip():
        return "Unknown"
    first = str(h).split(",")[0].strip()
    buckets = {"Centrinis": "Centrinis", "Centrinis kolektorinis": "Centrinis kolektorinis",
               "Dujinis": "Dujinis", "Elektra": "Elektra"}
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
reg["price_cut"] = (reg["price_change_dir"] == "sumazejo").astype(int)

formula = "log_price ~ area_m2 + rooms + age + floor_ratio + C(heat_grp) + C(city_grp)"
model = smf.ols(formula, data=reg).fit(cov_type="HC1")

vil = reg[reg["city_grp"] == "Vilnius"].copy()
vil["district"] = vil["location"].str.split(",").str[1].str.strip()
dist_counts = vil["district"].value_counts()
vil["district_grp"] = np.where(vil["district"].isin(dist_counts[dist_counts >= 15].index), vil["district"], "Other")
vil_model = smf.ols("log_price ~ area_m2 + rooms + age + floor_ratio + C(heat_grp) + C(district_grp)", data=vil).fit(cov_type="HC1")


def savefig(fig, name, pad=0.15):
    fig.savefig(f"assets/{name}.png", dpi=DPI, bbox_inches="tight", pad_inches=pad, facecolor="white")
    plt.close(fig)


# 1 --------------------------------------------------------------- hist_price
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
axes[0].hist(reg["price_eur"], bins=40, color="white", edgecolor=BLACK, linewidth=0.8)
axes[0].set_title("Rent, levels (€/month)")
axes[0].set_xlabel("Price (€)"); axes[0].set_ylabel("Listings")
axes[1].hist(reg["log_price"], bins=40, color="white", edgecolor=BLACK, linewidth=0.8)
axes[1].set_title(r"Rent, logs: $\ln(\mathrm{Price})$")
axes[1].set_xlabel(r"$\ln(\mathrm{Price})$"); axes[1].set_ylabel("Listings")
fig.tight_layout()
savefig(fig, "hist_price")

# 2 --------------------------------------------------------------- scatter area/rooms
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
ax = axes[0]
ax.scatter(reg["area_m2"], reg["log_price"], s=10, alpha=0.25, color=BLACK, linewidths=0)
xs = np.linspace(reg["area_m2"].min(), reg["area_m2"].max(), 50)
b = np.polyfit(reg["area_m2"], reg["log_price"], 1)
ax.plot(xs, np.polyval(b, xs), color=BLACK, linewidth=2)
ax.set_xlabel("Area (m²)"); ax.set_ylabel(r"$\ln(\mathrm{Price})$"); ax.set_title("Rent vs. area")

ax = axes[1]
means = reg.groupby("rooms")["log_price"].mean()
cnt = reg.groupby("rooms")["log_price"].count()
ax.scatter(reg["rooms"] + np.random.default_rng(0).uniform(-0.12, 0.12, len(reg)), reg["log_price"],
           s=10, alpha=0.18, color=BLACK, linewidths=0)
ax.plot(means.index, means.values, color=BLACK, linewidth=2, marker="o", markersize=5)
ax.set_xlabel("Rooms"); ax.set_ylabel(r"$\ln(\mathrm{Price})$"); ax.set_title("Rent vs. room count")
ax.set_xticks(sorted(reg["rooms"].unique()))
fig.tight_layout()
savefig(fig, "scatter_area_rooms")

# 3 --------------------------------------------------------------- fit
fig, ax = plt.subplots(figsize=(6.6, 6.0))
fitted = model.fittedvalues
actual = reg["log_price"]
ax.scatter(fitted, actual, s=10, alpha=0.3, color=BLACK, linewidths=0)
lims = [min(fitted.min(), actual.min()), max(fitted.max(), actual.max())]
ax.plot(lims, lims, color=BLACK, linewidth=1.4, linestyle="--")
ax.set_xlabel(r"Predicted $\ln(\mathrm{Price})$"); ax.set_ylabel(r"Actual $\ln(\mathrm{Price})$")
ax.set_title(f"Model fit  ($R^2 = {model.rsquared:.3f}$)")
ax.set_xlim(lims); ax.set_ylim(lims)
fig.tight_layout()
savefig(fig, "fit")

# 4 --------------------------------------------------------------- residual diagnostics
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
ax = axes[0]
ax.scatter(model.fittedvalues, model.resid, s=10, alpha=0.25, color=BLACK, linewidths=0)
ax.axhline(0, color=BLACK, linewidth=1.2)
ax.set_xlabel(r"Fitted $\ln(\mathrm{Price})$"); ax.set_ylabel("Residual"); ax.set_title("Residuals vs. fitted")

ax = axes[1]
osm, osr = stats.probplot(model.resid, dist="norm", fit=False)
ax.scatter(osm, osr, s=10, alpha=0.3, color=BLACK, linewidths=0)
lo, hi = min(osm.min(), osr.min()), max(osm.max(), osr.max())
sd = model.resid.std()
ax.plot([lo, hi], [lo * sd, hi * sd], color=BLACK, linewidth=1.4, linestyle="--")
ax.set_xlabel("Theoretical quantile"); ax.set_ylabel("Residual quantile"); ax.set_title("Normal Q–Q plot")
fig.tight_layout()
savefig(fig, "resid")

# 5 --------------------------------------------------------------- coefficient plot
names_map = [
    ("area_m2", "Area (m²)"), ("rooms", "Rooms"), ("age", "Age"), ("floor_ratio", "Floor ratio"),
    ("C(heat_grp)[T.Centrinis kolektorinis]", "Heat: Centr. kolekt."),
    ("C(heat_grp)[T.Dujinis]", "Heat: Dujinis"),
    ("C(heat_grp)[T.Elektra]", "Heat: Elektra"),
    ("C(heat_grp)[T.Other]", "Heat: Other"),
    ("C(city_grp)[T.Vilnius]", "City: Vilnius"),
    ("C(city_grp)[T.Klaipėda]", "City: Klaipėda"),
    ("C(city_grp)[T.Palanga]", "City: Palanga"),
    ("C(city_grp)[T.Šiauliai]", "City: Šiauliai"),
    ("C(city_grp)[T.Panevėžys]", "City: Panevėžys"),
    ("C(city_grp)[T.Other]", "City: Other"),
]
ci = model.conf_int()
rows = []
for key, label in names_map:
    rows.append((label, model.params[key], ci.loc[key, 0], ci.loc[key, 1]))
rows = rows[::-1]
fig, ax = plt.subplots(figsize=(7.5, 6.6))
ys = np.arange(len(rows))
for y, (label, coef, lo, hi) in zip(ys, rows):
    ax.plot([lo, hi], [y, y], color=GRAY, linewidth=1.6, solid_capstyle="round")
    ax.plot(coef, y, "o", color=BLACK, markersize=6)
ax.axvline(0, color=BLACK, linewidth=1, linestyle="--")
ax.set_yticks(ys); ax.set_yticklabels([r[0] for r in rows])
ax.set_xlabel(r"Coefficient on $\ln(\mathrm{Price})$ (95% CI)")
ax.set_title("Main model: coefficients")
fig.tight_layout()
savefig(fig, "coefplot")

# 6 --------------------------------------------------------------- city & district effects
city_order = ["Vilnius", "Klaipėda", "Palanga", "Panevėžys", "Šiauliai", "Other"]
city_eff = [model.params[f"C(city_grp)[T.{c}]"] * 100 for c in city_order]

dist_rows = [("Paupys", 0.4393), ("Senamiestis", 0.3391), ("Užupis", 0.2929), ("Žvėrynas", 0.1112),
             ("Šnipėčai" if False else "Šnipėškės", 0.1060), ("Naujamiestis", 0.1697),
             ("Baltupiai", -0.0581), ("Pašilaičiai", -0.1294), ("Pilaitė", -0.1068),
             ("Karoliniškės", -0.1401), ("Naujoji Vilnia", -0.1485)]
dist_rows = sorted(dist_rows, key=lambda r: r[1])
dist_labels = [r[0] for r in dist_rows]
dist_eff = [r[1] * 100 for r in dist_rows]

fig, axes = plt.subplots(1, 2, figsize=(12, 5.2))
ax = axes[0]
colors = [BLACK if v >= 0 else "white" for v in city_eff]
edge = [BLACK] * len(city_eff)
ax.barh(city_order, city_eff, color=colors, edgecolor=edge, linewidth=1.1)
ax.axvline(0, color=BLACK, linewidth=1)
ax.set_xlabel("% effect vs. Kaunas"); ax.set_title("City effect on rent")
ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%+.0f%%"))

ax = axes[1]
colors = [BLACK if v >= 0 else "white" for v in dist_eff]
ax.barh(dist_labels, dist_eff, color=colors, edgecolor=BLACK, linewidth=1.1)
ax.axvline(0, color=BLACK, linewidth=1)
ax.set_xlabel("% effect vs. Vilnius baseline"); ax.set_title("Vilnius district effect on rent")
ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%+.0f%%"))
fig.tight_layout()
savefig(fig, "bars_city_district")

# 7 --------------------------------------------------------------- price cuts by floor ratio
reg["floor_bin"] = pd.qcut(reg["floor_ratio"], 5, duplicates="drop")
bin_labels = [f"{i+1}" + (" (lowest)" if i == 0 else " (highest)" if i == reg["floor_bin"].nunique() - 1 else "")
              for i in range(reg["floor_bin"].nunique())]
reg["floor_bin"] = reg["floor_bin"].cat.rename_categories(bin_labels)
cut_rate = reg.groupby("floor_bin", observed=True)["price_cut"].mean() * 100
fig, ax = plt.subplots(figsize=(7.5, 4.6))
ax.bar(cut_rate.index.astype(str), cut_rate.values, color="white", edgecolor=BLACK, linewidth=1.2)
ax.axhline(reg["price_cut"].mean() * 100, color=BLACK, linewidth=1.2, linestyle="--")
ax.set_xlabel(f"Floor-ratio group, {len(bin_labels)} equal-sized bins (relative height in building)")
ax.set_ylabel("% of listings with a price cut")
ax.set_title("Price cuts are rarer higher up the building")
ax.text(len(bin_labels) - 1, reg["price_cut"].mean() * 100 + 1, "sample average", ha="right", fontsize=10, color=GRAY)
fig.tight_layout()
savefig(fig, "pricecut_floor")

print("all charts written")
