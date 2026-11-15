"""Render the deck's two LaTeX equations as plain black-on-transparent PNGs
for embedding in the pptx (PowerPoint text boxes can't render LaTeX)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["mathtext.fontset"] = "cm"
plt.rcParams["font.family"] = "serif"

def render(tex, path, fontsize=22, width=12.5, height=1.1):
    fig = plt.figure(figsize=(width, height), dpi=300)
    fig.patch.set_alpha(0)
    fig.text(0.5, 0.5, tex, fontsize=fontsize, color="black", ha="center", va="center")
    fig.savefig(path, transparent=True, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)

render(
    r"$\ln(\mathrm{Price}_i) = \beta_0 + \beta_1\,\mathrm{Area}_i + \beta_2\,\mathrm{Rooms}_i "
    r"+ \beta_3\,\mathrm{Age}_i + \beta_4\,\mathrm{FloorRatio}_i + \sum_k \gamma_k\,\mathrm{Heating}_{ik} "
    r"+ \sum_j \delta_j\,\mathrm{City}_{ij} + \varepsilon_i$",
    "assets/eq_main.png", fontsize=20, width=13.0, height=1.0,
)

render(
    r"$\mathrm{Pr}(\mathrm{PriceCut}_i{=}1) = \Lambda\left(\beta_0 + \beta_1\,\mathrm{Area}_i + \cdots "
    r"+ \beta_4\,\mathrm{FloorRatio}_i + \mathrm{Heating} + \mathrm{City}\right)$",
    "assets/eq_logit.png", fontsize=20, width=11.5, height=0.9,
)

def render_multiline(lines, path, fontsize=18, width=12.5, line_h=0.62):
    height = line_h * len(lines) + 0.25
    fig = plt.figure(figsize=(width, height), dpi=300)
    fig.patch.set_alpha(0)
    n = len(lines)
    for i, tex in enumerate(lines):
        y = 1 - (i + 0.5) / n
        fig.text(0.5, y, tex, fontsize=fontsize, color="black", ha="center", va="center")
    fig.savefig(path, transparent=True, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)

render_multiline(
    [
        r"$\mathrm{Area}_i:\ \mathrm{m^2} \qquad \mathrm{Rooms}_i:\ \mathrm{room\ count} \qquad "
        r"\mathrm{Age}_i = 2026 - \mathrm{YearBuilt}_i$",
        r"$\mathrm{FloorRatio}_i = \dfrac{\mathrm{Floor}_i}{\mathrm{TotalFloors}_i} \quad "
        r"\mathrm{(relative\ height\ in\ the\ building)}$",
        r"$\mathrm{Heating}_{ik},\ \mathrm{City}_{ij}:\ \mathrm{dummy\ variables}$",
        r"$\mathrm{reference\ categories:\ Centrinis\ (heating),\ Kaunas\ (city)}$",
    ],
    "assets/eq_vars.png", fontsize=17, width=12.5, line_h=0.55,
)

print("done")
