const pptxgen = require("pptxgenjs");
const { applyTheme } = require("./apply_theme.js");

const THEME = {
  name: "Monochrome",
  headFontFace: "Calibri",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "000000", lt1: "FFFFFF", dk2: "404040", lt2: "F2F2F2",
    accent1: "595959", accent2: "808080", accent3: "A6A6A6",
    accent4: "D9D9D9", accent5: "262626", accent6: "BFBFBF",
    hlink: "000000", folHlink: "000000",
  },
};

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5 in
const C = pres.SchemeColor;

const W = 13.333, H = 7.5;
const MX = 0.6; // left/right margin
const CW = W - 2 * MX;

function kicker(slide, text) {
  slide.addText(text.toUpperCase(), {
    x: MX, y: 0.45, w: CW, h: 0.3, fontFace: THEME.bodyFontFace, fontSize: 11,
    color: "595959", charSpacing: 2, isTextBox: true, margin: 0,
  });
}
function title(slide, text, y = 0.75) {
  slide.addText(text, {
    x: MX, y, w: CW, h: 0.7, fontFace: THEME.headFontFace, fontSize: 30, bold: true,
    color: "000000", isTextBox: true, margin: 0,
  });
}
function rule(slide, y) {
  slide.addShape(pres.ShapeType.line, { x: MX, y, w: CW, h: 0, line: { color: "D9D9D9", width: 0.75 } });
}
function bullets(slide, items, opts) {
  const arr = items.map((t, i) => ({
    text: t, options: { bullet: { code: "2022" }, breakLine: i < items.length - 1 },
  }));
  slide.addText(arr, {
    fontFace: THEME.bodyFontFace, fontSize: 14, color: "000000",
    isTextBox: true, margin: 0, lineSpacingMultiple: 1.25, paraSpaceAfter: 6,
    ...opts,
  });
}
function note(slide, text, opts) {
  slide.addText(text, {
    fontFace: THEME.bodyFontFace, fontSize: 11, italic: false, color: "595959",
    isTextBox: true, margin: 0, ...opts,
  });
}
function sectionHead(slide, text, x, y, w) {
  slide.addText(text, {
    x, y, w, h: 0.35, fontFace: THEME.headFontFace, fontSize: 15, bold: true,
    color: "000000", isTextBox: true, margin: 0,
  });
}

function table(slide, rows, opts) {
  const styled = rows.map((row, ri) => row.map((cell, ci) => ({
    text: String(cell),
    options: {
      fontFace: THEME.bodyFontFace,
      fontSize: opts.fontSize || 12,
      bold: ri === 0,
      color: ri === 0 ? "000000" : "000000",
      fill: { color: ri === 0 ? "F2F2F2" : "FFFFFF" },
      align: ci === 0 ? "left" : "right",
      valign: "middle",
      border: [
        { type: "solid", color: "D9D9D9", pt: 0.75 },
        { type: "none" }, { type: "none" }, { type: "none" },
      ],
    },
  })));
  slide.addTable(styled, {
    x: opts.x, y: opts.y, w: opts.w, colW: opts.colW,
    rowH: opts.rowH || 0.32, autoPage: false,
  });
}

function figure(slide, path, aspect, y, maxW, maxH, caption) {
  let w = maxW, h = maxW / aspect;
  if (h > maxH) { h = maxH; w = maxH * aspect; }
  const x = (W - w) / 2;
  slide.addImage({ path, x, y, w, h });
  if (caption) {
    slide.addText(caption, {
      x: MX, y: y + h + 0.18, w: CW, h: 0.4, fontFace: THEME.bodyFontFace, fontSize: 12.5,
      color: "595959", align: "center", isTextBox: true, margin: 0,
    });
  }
  return y + h;
}

function footer(slide, n, total) {
  slide.addText(`${n} / ${total}`, {
    x: W - 1.2, y: H - 0.5, w: 0.9, h: 0.3, fontFace: THEME.bodyFontFace,
    fontSize: 10, color: "A6A6A6", align: "right", isTextBox: true, margin: 0,
  });
}

const TOTAL = 20;

// ---------------------------------------------------------------- Slide 1
{
  const s = pres.addSlide();
  s.background = { color: "FFFFFF" };
  s.addText("EMPIRICAL FINANCE · COURSE PROJECT", {
    x: MX, y: 2.55, w: CW, h: 0.3, fontFace: THEME.bodyFontFace, fontSize: 12,
    color: "595959", charSpacing: 2, isTextBox: true, margin: 0,
  });
  s.addText("What Determines Apartment Rent?", {
    x: MX, y: 2.9, w: CW, h: 1.1, fontFace: THEME.headFontFace, fontSize: 40, bold: true,
    color: "000000", isTextBox: true, margin: 0,
  });
  s.addText(
    "A hedonic pricing analysis of 2,662 rental listings scraped from aruodas.lt, Lithuania's largest real-estate portal.",
    { x: MX, y: 4.0, w: 9.6, h: 0.8, fontFace: THEME.bodyFontFace, fontSize: 16, color: "404040", isTextBox: true, margin: 0 }
  );
  rule(s, 4.9);
  note(s, "Data collected November 2026 · 7 cities · cross-sectional, single snapshot", { x: MX, y: 5.05, w: CW, h: 0.3 });
  footer(s, 1, TOTAL);
}

// ---------------------------------------------------------------- Slide 2
{
  const s = pres.addSlide();
  kicker(s, "1 · Question and approach");
  title(s, "Rent as a bundle of characteristics");
  rule(s, 1.55);
  s.addText(
    "A rental unit is a bundle of attributes — size, rooms, floor, age, heating, location — that the market " +
    "prices as a whole. Hedonic regression recovers an implicit price for each attribute by regressing the " +
    "observed rent on the bundle.",
    { x: MX, y: 1.8, w: 10.6, h: 1.1, fontFace: THEME.bodyFontFace, fontSize: 15, color: "000000", isTextBox: true, margin: 0 }
  );
  sectionHead(s, "What this is, and is not", MX, 3.1, CW);
  bullets(s, [
    "This is a cross-sectional, observational dataset: one scrape, one point in time, no randomisation and no repeated observations per unit.",
    "The results below are descriptive correlations, not causal effects. On the ladder of research designs, this sits near the bottom rung.",
    "The question we can answer: which characteristics move with rent, and by how much, after holding the others fixed.",
  ], { x: MX, y: 3.55, w: 10.8, h: 2.4 });
  footer(s, 2, TOTAL);
}

// ---------------------------------------------------------------- Slide 3
{
  const s = pres.addSlide();
  kicker(s, "2 · The sample");
  title(s, "2,662 listings, 7 cities");
  rule(s, 1.55);

  const stats = [
    ["2,662", "listings"], ["€699", "mean rent"], ["49.5 m²", "mean area"], ["1988", "mean year built"],
  ];
  stats.forEach((st, i) => {
    const x = MX + i * 2.8;
    s.addText(st[0], { x, y: 1.75, w: 2.6, h: 0.55, fontFace: THEME.headFontFace, fontSize: 28, bold: true, color: "000000", isTextBox: true, margin: 0 });
    s.addText(st[1].toUpperCase(), { x, y: 2.32, w: 2.6, h: 0.3, fontFace: THEME.bodyFontFace, fontSize: 10.5, color: "595959", charSpacing: 1, isTextBox: true, margin: 0 });
  });

  sectionHead(s, "By city", MX, 2.95, 5.6);
  table(s, [
    ["City", "N"], ["Vilnius", "1,401"], ["Kaunas", "437"], ["Klaipėda", "302"],
    ["Other", "265"], ["Šiauliai", "103"], ["Palanga", "101"], ["Panevėžys", "53"],
  ], { x: MX, y: 3.35, w: 5.6, colW: [3.9, 1.7], rowH: 0.33 });

  sectionHead(s, "Primary heating", 7.1, 2.95, 5.6);
  table(s, [
    ["Type", "N"], ["Centrinis (district)", "1,257"], ["Centrinis kolektorinis", "823"],
    ["Dujinis (gas)", "316"], ["Elektra (electric)", "152"], ["Other", "92"],
  ], { x: 7.1, y: 3.35, w: 5.6, colW: [3.9, 1.7], rowH: 0.33 });

  note(s,
    "22 listings dropped for the regression sample: implausible build years (<1800) or rents outside €100–5,000, leaving N = 2,640.",
    { x: MX, y: 6.95, w: CW, h: 0.3 });
  footer(s, 3, TOTAL);
}

// ---------------------------------------------------------------- Slide 4
{
  const s = pres.addSlide();
  kicker(s, "3 · Model");
  title(s, "Model");
  rule(s, 1.55);
  s.addText(
    "Rent is regressed in logs, so each coefficient reads as an approximate percentage effect:",
    { x: MX, y: 1.75, w: CW, h: 0.4, fontFace: THEME.bodyFontFace, fontSize: 14.5, color: "000000", isTextBox: true, margin: 0 }
  );
  s.addImage({ path: "assets/eq_main.png", x: 0.9, y: 2.3, w: 11.5, h: 11.5 * (215 / 3665) });
  figure(s, "assets/eq_vars.png", 3.0789, 3.15, 11.0, 2.6);
  note(s, "Estimated by OLS with HC1 heteroskedasticity-robust standard errors (justified on the diagnostics slide).",
    { x: MX, y: 5.95, w: CW, h: 0.3 });
  footer(s, 4, TOTAL);
}

// ---------------------------------------------------------------- Slide 5
{
  const s = pres.addSlide();
  kicker(s, "3 · Model");
  title(s, "Why model rent in logs?");
  rule(s, 1.55);
  figure(s, "assets/hist_price.png", 2.6737, 1.8, 11.4, 4.3,
    "Raw rents are right-skewed; the log transform used throughout is close to symmetric.");
  footer(s, 5, TOTAL);
}

// ---------------------------------------------------------------- Slide 6
{
  const s = pres.addSlide();
  kicker(s, "4 · Results");
  title(s, "Main regression");
  rule(s, 1.55);
  table(s, [
    ["Variable", "Coef.", "Robust SE", "p"],
    ["Area (m²)", "0.0091", "0.0008", "<0.001"],
    ["Rooms", "0.1406", "0.0193", "<0.001"],
    ["Age (years)", "−0.0009", "0.0002", "<0.001"],
    ["Floor ratio", "0.0247", "0.0204", "0.226"],
    ["Heating: Centrinis kolektorinis", "0.1893", "0.0140", "<0.001"],
    ["Heating: Dujinis", "0.0884", "0.0227", "<0.001"],
    ["Heating: Elektra", "0.0616", "0.0322", "0.056"],
    ["City: Vilnius", "0.1439", "0.0178", "<0.001"],
    ["City: Klaipėda", "−0.1630", "0.0221", "<0.001"],
    ["City: Šiauliai", "−0.3243", "0.0315", "<0.001"],
    ["City: Panevėžys", "−0.3975", "0.0473", "<0.001"],
  ], { x: MX, y: 1.8, w: 7.3, colW: [3.9, 1.1, 1.3, 1.0], rowH: 0.3, fontSize: 11.5 });
  note(s, "R² = 0.638, adj. R² = 0.636, F(14, 2625) = 245.3, N = 2,640. Reference: Centrinis heating, Kaunas.",
    { x: MX, y: 5.75, w: 7.3, h: 0.5 });

  bullets(s, [
    "Each extra m² adds about 0.9% to rent, holding room count fixed.",
    "One more room adds about 14%, even at the same total area — layout, not just size, is priced.",
    "Vilnius commands a 14% premium over Kaunas; Šiauliai and Panevėžys rent for 30–40% less.",
  ], { x: 7.9, y: 1.85, w: 4.8, h: 3.2 });
  footer(s, 6, TOTAL);
}

// ---------------------------------------------------------------- Slide 7
{
  const s = pres.addSlide();
  kicker(s, "4 · Results");
  title(s, "Rent vs. size and room count");
  rule(s, 1.55);
  figure(s, "assets/scatter_area_rooms.png", 2.6392, 1.8, 11.4, 4.3,
    "The two strongest bivariate relationships the main model estimates jointly.");
  footer(s, 7, TOTAL);
}

// ---------------------------------------------------------------- Slide 8
{
  const s = pres.addSlide();
  kicker(s, "4 · Results");
  title(s, "Coefficients, visually");
  rule(s, 1.55);
  figure(s, "assets/coefplot.png", 1.1447, 1.8, 6.6, 4.3,
    "Same estimates as the results table, shown as point estimates with 95% confidence intervals.");
  footer(s, 8, TOTAL);
}

// ---------------------------------------------------------------- Slide 9
{
  const s = pres.addSlide();
  kicker(s, "5 · Diagnostics");
  title(s, "Is the model well specified?");
  rule(s, 1.55);

  sectionHead(s, "Heteroskedasticity", MX, 1.8, 5.6);
  s.addText("Breusch–Pagan: χ² = 148.5, p < 0.001.", {
    x: MX, y: 2.2, w: 5.6, h: 0.35, fontFace: THEME.bodyFontFace, fontSize: 13.5, color: "000000", isTextBox: true, margin: 0,
  });
  note(s, "Residual variance is not constant — expected for rent levels. This is why HC1 robust standard errors are used throughout rather than the classical OLS SEs.",
    { x: MX, y: 2.6, w: 5.5, h: 1.1 });

  sectionHead(s, "Multicollinearity", 7.1, 1.8, 5.6);
  table(s, [
    ["Variable", "VIF"], ["Area", "2.61"], ["Rooms", "2.61"], ["Age", "1.01"], ["Floor ratio", "1.01"],
  ], { x: 7.1, y: 2.2, w: 5.6, colW: [3.9, 1.7], rowH: 0.3 });
  note(s, "All below the conventional concern threshold of 5–10; area and rooms move together, as expected, but not severely.",
    { x: 7.1, y: 4.1, w: 5.5, h: 0.6 });

  sectionHead(s, "Influential observations", MX, 5.1, CW);
  s.addText(
    "177 of 2,640 listings (6.7%) exceed the Cook's distance rule of thumb 4/n. Consistent with heavy-tailed rents " +
    "at the top of the market (penthouses, short lets priced as long-term) rather than data errors.",
    { x: MX, y: 5.5, w: 10.8, h: 0.8, fontFace: THEME.bodyFontFace, fontSize: 14, color: "000000", isTextBox: true, margin: 0 }
  );
  footer(s, 9, TOTAL);
}

// ---------------------------------------------------------------- Slide 10
{
  const s = pres.addSlide();
  kicker(s, "5 · Diagnostics");
  title(s, "How well does the model fit?");
  rule(s, 1.55);
  figure(s, "assets/fit.png", 1.1042, 1.8, 6.4, 4.3,
    "Predicted vs. actual log-rent; points on the dashed 45° line are predicted exactly.");
  footer(s, 10, TOTAL);
}

// ---------------------------------------------------------------- Slide 11
{
  const s = pres.addSlide();
  kicker(s, "5 · Diagnostics");
  title(s, "Residual diagnostics");
  rule(s, 1.55);
  figure(s, "assets/resid.png", 2.6633, 1.8, 11.4, 4.3,
    "Mild heteroskedasticity and right-tail departure from normality — consistent with the Breusch–Pagan test.");
  footer(s, 11, TOTAL);
}

// ---------------------------------------------------------------- Slide 12
{
  const s = pres.addSlide();
  kicker(s, "6 · Extension");
  title(s, "Zooming in: Vilnius by district");
  rule(s, 1.55);
  s.addText(
    "Refitting within Vilnius alone, replacing the city dummy with district fixed effects, raises fit from R² = 0.638 to " +
    "R² = 0.762 (N = 1,393) — location within a city matters as much as the city itself.",
    { x: MX, y: 1.75, w: CW, h: 0.65, fontFace: THEME.bodyFontFace, fontSize: 14, color: "000000", isTextBox: true, margin: 0 }
  );

  sectionHead(s, "Premium districts (vs. omitted baseline)", MX, 2.55, 5.6);
  table(s, [
    ["District", "Effect", "p"],
    ["Paupys", "+44.0%", "<0.001"],
    ["Senamiestis (Old Town)", "+33.9%", "<0.001"],
    ["Užupis", "+29.3%", "<0.001"],
    ["Naujamiestis", "+17.0%", "<0.001"],
  ], { x: MX, y: 2.95, w: 5.6, colW: [3.3, 1.3, 1.0], rowH: 0.33 });

  sectionHead(s, "Discount districts", 7.1, 2.55, 5.6);
  table(s, [
    ["District", "Effect", "p"],
    ["Naujoji Vilnia", "−14.9%", "<0.001"],
    ["Karoliniškės", "−14.0%", "0.009"],
    ["Pašilaičiai", "−12.9%", "<0.001"],
    ["Pilaitė", "−10.7%", "0.001"],
  ], { x: 7.1, y: 2.95, w: 5.6, colW: [3.3, 1.3, 1.0], rowH: 0.33 });

  note(s, "Area, rooms, age and heating coefficients are essentially unchanged from the city-level model once district is controlled for.",
    { x: MX, y: 4.85, w: CW, h: 0.4 });
  footer(s, 12, TOTAL);
}

// ---------------------------------------------------------------- Slide 13
{
  const s = pres.addSlide();
  kicker(s, "6 · Extension");
  title(s, "Location effects, visually");
  rule(s, 1.55);
  figure(s, "assets/bars_city_district.png", 2.3268, 1.8, 11.4, 4.3,
    "City effects (left) and Vilnius-district effects (right), from the two regressions.");
  footer(s, 13, TOTAL);
}

// ---------------------------------------------------------------- Slide 14 (decomposition 1 of 3)
{
  const s = pres.addSlide();
  kicker(s, "7 · Decomposition");
  title(s, "Where does the fit come from?");
  rule(s, 1.55);
  s.addText(
    "R² = 0.638 is a single number for four very different kinds of information. Adding the blocks one at a time, " +
    "in the order a landlord would reason about a unit, shows how much each is actually worth.",
    { x: MX, y: 1.75, w: CW, h: 0.6, fontFace: THEME.bodyFontFace, fontSize: 14, color: "000000", isTextBox: true, margin: 0 }
  );
  figure(s, "assets/seq_r2.png", 1.907, 2.5, 9.4, 3.9);
  note(s, "Each model nests the previous one; the marginal R² is the gain from adding that block alone.",
    { x: MX, y: 6.55, w: CW, h: 0.3 });
  footer(s, 14, TOTAL);
}

// ---------------------------------------------------------------- Slide 15 (decomposition 2 of 3)
{
  const s = pres.addSlide();
  kicker(s, "7 · Decomposition");
  title(s, "Location adds more than everything else combined");
  rule(s, 1.55);
  bullets(s, [
    "Size and room count alone explain 40.3 points of the 63.8-point R² — the bulk of the floor.",
    "Building age and floor position add only 2.7 points more; heating type adds 5.6 points.",
    "Location — which city a listing is in — adds 15.3 points on its own, more than age, floor and heating combined.",
    "Fit rises further to 76.2% within Vilnius alone once city is replaced by district — location keeps paying off at finer resolution.",
  ], { x: MX, y: 1.85, w: 11.2, h: 3.0 });
  note(s, "Marginal R² from the sequential decomposition on the previous slide; district result from the Vilnius-only model.",
    { x: MX, y: 5.1, w: CW, h: 0.3 });
  footer(s, 15, TOTAL);
}

// ---------------------------------------------------------------- Slide 16 (decomposition 3 of 3)
{
  const s = pres.addSlide();
  kicker(s, "7 · Decomposition");
  title(s, "Is the city gap real, or just composition?");
  rule(s, 1.55);
  s.addText(
    "A city could rent for less simply because its units are smaller or older, not because location itself is cheaper. " +
    "Comparing the raw rent gap to the gap after holding size, age and heating fixed separates the two.",
    { x: MX, y: 1.75, w: CW, h: 0.65, fontFace: THEME.bodyFontFace, fontSize: 13.5, color: "000000", isTextBox: true, margin: 0 }
  );
  figure(s, "assets/city_gap_decomp.png", 1.7106, 2.5, 7.0, 3.0);
  bullets(s, [
    "Vilnius: most of its +18% raw premium is genuine location, not bigger units.",
    "Šiauliai & Panevėžys: composition (smaller, older stock) explains roughly a fifth of their raw discount — the pure location penalty is smaller than it first looks.",
  ], { x: MX, y: 5.65, w: CW, h: 1.2, fontSize: 12.5 });
  footer(s, 16, TOTAL);
}

// ---------------------------------------------------------------- Slide 17
{
  const s = pres.addSlide();
  kicker(s, "8 · Secondary outcome");
  title(s, "Who gets a price cut?");
  rule(s, 1.55);
  s.addText(
    "24.9% of listings show a price marked down from an earlier asking price. Does the same set of characteristics predict a cut?",
    { x: MX, y: 1.75, w: CW, h: 0.5, fontFace: THEME.bodyFontFace, fontSize: 14, color: "000000", isTextBox: true, margin: 0 }
  );
  s.addImage({ path: "assets/eq_logit.png", x: 1.6, y: 2.3, w: 10.1, h: 10.1 * (117 / 2765) });

  table(s, [
    ["Variable", "Coef.", "p"],
    ["Floor ratio", "−0.601", "<0.001"],
    ["Age", "−0.0037", "0.041"],
    ["Area", "−0.0039", "0.271"],
    ["Rooms", "0.048", "0.614"],
    ["All city / heating dummies", "—", "all > 0.08"],
  ], { x: MX, y: 3.1, w: 5.6, colW: [3.3, 1.3, 1.0], rowH: 0.32 });
  note(s, "Pseudo R² = 0.013, N = 2,640. Almost none of the variation in discounting is explained by observed characteristics.",
    { x: MX, y: 5.15, w: 5.5, h: 0.6 });

  bullets(s, [
    "Units higher up a building are markedly less likely to be discounted — ground-and-low-floor listings carry most of the price cuts.",
    "Otherwise, discounting looks close to orthogonal to what a hedonic model prices — consistent with cuts tracking unobserved urgency rather than the unit itself.",
  ], { x: 7.1, y: 3.1, w: 5.6, h: 2.4 });
  footer(s, 17, TOTAL);
}

// ---------------------------------------------------------------- Slide 18
{
  const s = pres.addSlide();
  kicker(s, "8 · Secondary outcome");
  title(s, "Price cuts by floor position");
  rule(s, 1.55);
  figure(s, "assets/pricecut_floor.png", 1.6366, 1.8, 8.6, 4.3,
    "The one characteristic that robustly predicts a price cut: higher floors are discounted less often.");
  footer(s, 18, TOTAL);
}

// ---------------------------------------------------------------- Slide 19
{
  const s = pres.addSlide();
  kicker(s, "9 · Limitations and takeaways");
  title(s, "What this is worth, and what it is not");
  rule(s, 1.55);

  sectionHead(s, "Takeaways", MX, 1.8, 5.6);
  bullets(s, [
    "Size, room count, age, heating and — especially — location jointly explain 64% of rent variation (76% within Vilnius with districts).",
    "Location alone adds more explanatory power than age, floor and heating combined — and most of the raw city gap survives after controlling for unit size and age.",
    "An extra room is worth about €105/month at the sample mean — more than the floor-area line alone predicts: layout is priced on top of size.",
    "Discounting behaviour is close to unpredictable from listing characteristics, except for floor position.",
  ], { x: MX, y: 2.2, w: 5.5, h: 4.3, fontSize: 13 });

  sectionHead(s, "Limitations", 7.1, 1.8, 5.6);
  bullets(s, [
    "Not causal. No variation is experimentally or quasi-experimentally assigned; coefficients are conditional correlations.",
    "Omitted variables. Renovation quality, exact micro-location, furnishing and photos are all priced by the market and unobserved here.",
    "Single snapshot. One scrape of currently-live ads; no panel structure, so time-on-market and seller fixed effects are out of reach.",
  ], { x: 7.1, y: 2.2, w: 5.5, h: 3.5, fontSize: 13 });
  footer(s, 19, TOTAL);
}

// ---------------------------------------------------------------- Slide 20
{
  const s = pres.addSlide();
  s.background = { color: "FFFFFF" };
  s.addText("EMPIRICAL FINANCE · COURSE PROJECT", {
    x: MX, y: 2.95, w: CW, h: 0.3, fontFace: THEME.bodyFontFace, fontSize: 12,
    color: "595959", charSpacing: 2, isTextBox: true, margin: 0,
  });
  s.addText("Thank you", {
    x: MX, y: 3.3, w: CW, h: 1.1, fontFace: THEME.headFontFace, fontSize: 40, bold: true,
    color: "000000", isTextBox: true, margin: 0,
  });
  rule(s, 4.3);
  note(s, "What determines apartment rent? — a hedonic pricing analysis of 2,662 aruodas.lt listings.",
    { x: MX, y: 4.45, w: CW, h: 0.3 });
  footer(s, 20, TOTAL);
}

(async () => {
  await pres.writeFile({ fileName: "Rental_Price_Hedonics.pptx" });
  await applyTheme("Rental_Price_Hedonics.pptx", THEME);
  console.log("written");
})();
