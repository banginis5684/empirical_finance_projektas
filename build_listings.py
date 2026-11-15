"""
build_listings.py - parse alldataaruodas.txt (clean text copy-pasted
directly from the aruodas.lt page DOM - no OCR involved) into listings.xlsx.

The page repeats a fixed field order per listing card:
    [badges...]
    Location                   (e.g. "Vilnius, Pašilaičiai")
    Street                     (e.g. "Girulių g.")
    Prieš ...                  (posted date - the one reliable per-card anchor)
    (blank, blank)
    N k.                       (rooms)
    (blank)
    NN m²                      (area)
    (blank)
    N/N aukšt.                 (floor/floor_total)
    (blank)
    NNNN m.                    (year built)
    (blank)
    <heating text>
    [ Kaina padidėjusi/sumažėjusi N% ]   (optional)
    NNN €                      (price)
    NNN € užstatas  |  Be užstato su zent.lt apsauga   (deposit or none)
    [amenity/badge lines...]

A "Daugiau butų projekte:" marker after a card introduces a bundle of
extra unit variants for the same project (same location/street), each:
    <repeated title line>
    (blank)
    N kamb.
    (blank)
    NN,NN m²
    (blank)
    N/N aukšt.
    <status text, e.g. "Įrengtas">
    NNN €
until "Projekto vystytojas" / the next real card / end of file.
"""

import re
from pathlib import Path

import pandas as pd

SRC = Path(r"S:\Projects\click_read\alldataaruodas.txt")
OUT = Path(r"S:\Projects\click_read\listings.xlsx")

POSTED_RE = re.compile(r"^Prieš\s+(.+)$")
ROOMS_RE = re.compile(r"^(\d+)\s*k\.$")
AREA_RE = re.compile(r"^(\d+(?:[.,]\d+)?)\s*m[²2]$")
FLOOR_RE = re.compile(r"^(\d+)\s*/\s*(\d+)\s*aukšt\.?$", re.IGNORECASE)
YEAR_RE = re.compile(r"^(\d{4})\s*m\.?$")
PRICE_RE = re.compile(r"^([\d\s]+(?:[.,]\d+)?)\s*€")
DEPOSIT_RE = re.compile(r"^([\d\s]+(?:[.,]\d+)?)\s*€\s*u[žz]statas$", re.IGNORECASE)
NO_DEPOSIT_RE = re.compile(r"^Be u[žz]statos?\b", re.IGNORECASE)
PRICE_CHANGE_RE = re.compile(r"^\s*Kaina\s+(padid[eė]jusi|sumaž[eė]jusi)\s+([\d,.]+)\s*%$", re.IGNORECASE)

SUB_ROOMS_RE = re.compile(r"^(\d+)\s*kamb\.$")
TITLE_RE = re.compile(r"^(.+), (.+), \d+ kambari[ųo] buto nuomo?a?$")
BUNDLE_MARKER_RE = re.compile(r"^Daugiau but[ųu] projekte:?", re.IGNORECASE)
BUNDLE_END_RE = re.compile(r"^(Projekto vystytojas|Daugiau variant)", re.IGNORECASE)


def to_num(s):
    return s.replace(" ", "").replace(",", ".")


def main():
    raw_lines = SRC.read_text(encoding="utf-8").splitlines()
    lines = [l.strip() for l in raw_lines]
    n = len(lines)

    # index of every non-blank line, in order, for easy "previous non-blank" lookups
    nonblank_idx = [i for i, l in enumerate(lines) if l]
    pos_in_nonblank = {idx: k for k, idx in enumerate(nonblank_idx)}

    records = []
    i = 0
    while i < n:
        m = POSTED_RE.match(lines[i])
        if not m:
            i += 1
            continue

        posted_ago = m.group(1).strip(" .,")

        # street/location are the two non-blank lines right before this one
        k = pos_in_nonblank.get(i)
        street = lines[nonblank_idx[k - 1]] if k is not None and k >= 1 else ""
        location = lines[nonblank_idx[k - 2]] if k is not None and k >= 2 else ""

        # walk forward through the fixed field block
        j = i + 1
        rooms = area_m2 = floor = floor_total = year_built = heating = ""
        price = deposit = price_change_dir = price_change_pct = ""

        def next_nonblank(idx):
            while idx < n and not lines[idx]:
                idx += 1
            return idx

        j = next_nonblank(j)
        rm = ROOMS_RE.match(lines[j]) if j < n else None
        if rm:
            rooms = rm.group(1)
            j = next_nonblank(j + 1)
            am = AREA_RE.match(lines[j]) if j < n else None
            if am:
                area_m2 = to_num(am.group(1))
                j = next_nonblank(j + 1)
                fm = FLOOR_RE.match(lines[j]) if j < n else None
                if fm:
                    floor, floor_total = fm.group(1), fm.group(2)
                    j = next_nonblank(j + 1)
                    ym = YEAR_RE.match(lines[j]) if j < n else None
                    if ym:
                        year_built = ym.group(1)
                        j = next_nonblank(j + 1)
                        # some buildings also show a renovation year right
                        # after the construction year (e.g. "1937 m." then
                        # "2022 m." + "renovacija") - skip both, keep the
                        # original construction year.
                        if j < n and YEAR_RE.match(lines[j]):
                            j += 1
                            if j < n and lines[j].strip().lower() == "renovacija":
                                j += 1
                            j = next_nonblank(j)
                        if j < n and not POSTED_RE.match(lines[j]) and not PRICE_RE.match(lines[j]) \
                                and not PRICE_CHANGE_RE.match(lines[j]):
                            heating = lines[j]
                            j = next_nonblank(j + 1)

        # optional price-change line, then price, then deposit
        if j < n:
            pcm = PRICE_CHANGE_RE.match(lines[j])
            if pcm:
                price_change_dir = "padidejo" if "padid" in pcm.group(1).lower() else "sumazejo"
                price_change_pct = pcm.group(2).replace(",", ".")
                j = next_nonblank(j + 1)
        if j < n:
            pm = PRICE_RE.match(lines[j])
            if pm:
                price = to_num(pm.group(1))
                j = next_nonblank(j + 1)
        if j < n:
            dm = DEPOSIT_RE.match(lines[j])
            if dm:
                deposit = to_num(dm.group(1))
                j += 1
            elif NO_DEPOSIT_RE.match(lines[j]):
                j += 1

        records.append({
            "listing_type": "standalone",
            "location": location,
            "street": street,
            "price_eur": price,
            "price_change_dir": price_change_dir,
            "price_change_pct": price_change_pct,
            "deposit_eur": deposit,
            "posted_ago": posted_ago,
            "rooms": rooms,
            "area_m2": area_m2,
            "floor": floor,
            "floor_total": floor_total,
            "year_built": year_built,
            "heating": heating,
            "source": f"line{i + 1}",
        })
        main_record = records[-1]

        # scan ahead (without consuming the main loop's position) for a
        # "Daugiau butų projekte:" bundle before the next real card
        scan = j
        bundle_found = False
        while scan < n:
            if POSTED_RE.match(lines[scan]):
                break
            if BUNDLE_MARKER_RE.match(lines[scan]):
                bundle_found = True
                scan += 1
                break
            scan += 1

        if bundle_found:
            main_record["listing_type"] = "project_main"
            while scan < n:
                line = lines[scan]
                if not line:
                    scan += 1
                    continue
                if POSTED_RE.match(line) or BUNDLE_END_RE.match(line):
                    break
                if TITLE_RE.match(line) or line == street or (location and line.startswith(location.split(",")[0])):
                    # repeated title/location line for this sub-unit - skip to its fields
                    scan += 1
                    scan = next_nonblank(scan)
                    srm = SUB_ROOMS_RE.match(lines[scan]) if scan < n else None
                    if not srm:
                        scan += 1
                        continue
                    sub_rooms = srm.group(1)
                    scan = next_nonblank(scan + 1)
                    sam = AREA_RE.match(lines[scan]) if scan < n else None
                    sub_area = to_num(sam.group(1)) if sam else ""
                    if sam:
                        scan = next_nonblank(scan + 1)
                    sfm = FLOOR_RE.match(lines[scan]) if scan < n else None
                    sub_floor = sfm.group(1) if sfm else ""
                    sub_floor_total = sfm.group(2) if sfm else ""
                    if sfm:
                        scan = next_nonblank(scan + 1)
                    # optional status line (e.g. "Įrengtas") before price
                    if scan < n and not PRICE_RE.match(lines[scan]):
                        scan = next_nonblank(scan + 1)
                    sub_price = ""
                    if scan < n:
                        spm = PRICE_RE.match(lines[scan])
                        if spm:
                            sub_price = to_num(spm.group(1))
                            scan += 1
                    records.append({
                        "listing_type": "project_unit",
                        "location": location,
                        "street": street,
                        "price_eur": sub_price,
                        "price_change_dir": "",
                        "price_change_pct": "",
                        "deposit_eur": "",
                        "posted_ago": posted_ago,
                        "rooms": sub_rooms,
                        "area_m2": sub_area,
                        "floor": sub_floor,
                        "floor_total": sub_floor_total,
                        "year_built": year_built,
                        "heating": heating,
                        "source": f"line{i + 1}+bundle",
                    })
                    continue
                scan += 1
            j = scan

        i = j if j > i else i + 1

    columns = [
        "listing_type", "location", "street", "price_eur", "price_change_dir", "price_change_pct",
        "deposit_eur", "posted_ago", "rooms", "area_m2", "floor", "floor_total",
        "year_built", "heating", "source",
    ]
    df = pd.DataFrame(records, columns=columns)
    df.to_excel(OUT, index=False)
    print(f"total records: {len(df)}")
    print(df["listing_type"].value_counts())
    print("rows with blank street:", (df["street"] == "").sum())
    print("rows with blank price:", (df["price_eur"] == "").sum())


if __name__ == "__main__":
    main()
