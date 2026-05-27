# Customer Insights Dashboard

Interactive dashboard exploring US grocery/CPG customer behavior across
visit frequency, basket composition, and lifetime spend tiers. Built on the
**Acquire Valued Shoppers Challenge** dataset (~350M transactions across
311K customers, 2012–2013) with a Python data layer that produces an
RFM-scored customer table, and a single self-contained HTML dashboard
rendered with Plotly.

🔗 **[View Live Dashboard](https://thenewbeehives-4ofus.github.io/customer-insights-dashboard/)**

## Key Findings

- **10% of customers generate half the revenue.** The top 5% (494 customers
  out of 9,881) account for **42% of revenue**; the top 10% account for **50%**;
  the bottom 50% combined contribute just **15%**.
- **What separates Top customers from Bottom isn't basket size — it's visit
  frequency.** Average order value stays remarkably flat at **$55–65 across
  every value tier**. Top-frequency-quartile customers visit 155 times on
  average; bottom-quartile customers visit 22.
- **February is the seasonal peak.** Monthly revenue climbed from $3.3M
  (March 2012) to **$6.1M in February 2013 — 1.40× the monthly average**.
  Super Bowl, Valentine's Day, and post-tax-refund spending compound into
  a clear late-winter lift.

## How to Reproduce

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Download the raw dataset (~2.4 GB compressed, Kaggle competition data)
#    See data/README.md for the download steps and required Kaggle auth.

# 3. Build the customer + monthly CSVs (chunked stream over ~350M rows; ~4 min)
python src/data_preparation.py

# 4. Sanity-check the outputs
python validate_results.py

# 5. Build the HTML dashboard
python src/build_dashboard.py
```

`src/data_preparation.py` writes [data/customers.csv](data/customers.csv)
(9,881 rows, one per sampled customer) and [data/monthly.csv](data/monthly.csv)
(13 monthly aggregates, March 2012 through March 2013). `src/build_dashboard.py`
writes [docs/index.html](docs/index.html) — a single self-contained page with
three interactive Plotly charts. All three are committed so the dashboard
is reproducible end-to-end from the raw Kaggle download.

## Technical Approach

**Chunked streaming** ([src/data_preparation.py](src/data_preparation.py))
The raw `transactions.csv.gz` is ~2.4 GB compressed / ~22 GB uncompressed,
350M rows. Reading it whole would not fit in memory; the script streams it
in 2M-row chunks and applies the filter inside each chunk.

**Customer sampling**
Deterministic modulus sampling on the customer ID: customers with `id % 31 == 0`
are kept. This yields a uniform random sample of ~10,000 customers across
the entire transactions file without requiring a preliminary index scan.
Reproducible without needing a seeded RNG.

**Data hygiene**
Drops returns and zero-amount rows (`purchasequantity <= 0` or `purchaseamount <= 0`).
Caps the analysis window at **2013-03-31** — the dataset truncates each
customer's transactions at their assigned competition offer date, and the
active-customer count cliffs from 9,491 (March 2013) to 6,387 (April 2013).
Past that cutoff the monthly aggregates aren't comparable.

**Order definition**
One "order" is the line-items for a single customer at a single chain on a
single date. ~10.5M transactions roll up to ~835K orders across 9,881 customers.

**Feature engineering**
For every customer: total spend, order count, average order value, days
since last purchase (vs 2013-03-31 snapshot), customer tenure, RFM quintile
scores (1–5) for Recency, Frequency, Monetary using rank-based bucketing
so ties land in the same quintile.

**Value-tier segmentation**
Customers are bucketed by M-score (lifetime-spend quintile):

| Tier | M-score | Customers | Avg lifetime spend |
|---|---|---|---|
| Top 20% | 5 | 1,977 | $17,480 |
| Upper 20% | 4 | 1,976 | $4,872 |
| Middle 20% | 3 | 1,976 | $3,301 |
| Lower 20% | 2 | 1,976 | $2,019 |
| Bottom 20% | 1 | 1,976 | $804 |

A recency-based segmentation was considered and cut — AVS is by construction
a curated set of high-engagement customers, so a "Lapsed vs Active" view
produces 99% in one bucket and tells no story. M-score quintiles surface
the real spread.

**Dashboard rendering** ([src/build_dashboard.py](src/build_dashboard.py))
Reads the CSVs, constructs three Plotly figures (Lorenz-style concentration
curve, frequency-vs-AOV scatter colored by value tier, dual-axis monthly
trend with linear OLS trend line), and embeds them in an HTML/CSS wrapper
with a three-part narrative. The result is a single ~500KB HTML file that
needs no server — Plotly's runtime loads from CDN, GitHub Pages serves
the page from `/docs`.

## Project Structure

```
data/                       Raw dataset (untracked) + derived customers.csv / monthly.csv
src/data_preparation.py     Stream-filter, dedupe-to-orders, score RFM, aggregate
src/build_dashboard.py      Render Plotly figures + HTML wrapper into docs/index.html
validate_results.py         Sanity checks on the prepared CSVs
dashboard/                  Narrative arc and design-decisions notes
docs/index.html             The published HTML dashboard (GitHub Pages serves this)
report/                     Static walkthrough for viewers reading the repo on GitHub
```

## Design Decisions

The dashboard is built around a 3-part narrative arc (Concentration →
Diagnosis → Opportunity), with chart-type, color, and annotation choices
documented so each can be defended in a sentence. Full notes:

- [dashboard/narrative_arc.md](dashboard/narrative_arc.md) — the question
  the dashboard answers and how each view builds the argument
- [dashboard/design_decisions.md](dashboard/design_decisions.md) — chart-type,
  color, annotation, and interactivity rationale

## License

MIT
