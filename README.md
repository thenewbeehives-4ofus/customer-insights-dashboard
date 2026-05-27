# Customer Insights Dashboard

Interactive Tableau dashboard exploring customer behavior across demographics
and purchase history. Built on the UCI **Online Retail II** dataset
(~1M transactions, 2009–2011) and a Python data layer that produces a
customer-level table with RFM scores and recency-based segments.

🔗 [View Interactive Dashboard on Tableau Public](#) *(link pending)*

## Key Findings

- **Half of the customer base has gone quiet.** 40.8% of customers are
  *Lapsed* (no purchase in 6+ months); another 9.9% are *At Risk* (90–180 days).
- **One-time buyers are the leverage point.** 28% of customers placed exactly
  one order. They generate **1/12 the lifetime value** of repeat buyers
  (£350 vs £4,036 on average).
- **November is the natural re-engagement window.** Both 2010 and 2011 peaked
  in November at ~£1.17M (1.65× the monthly average), while new-customer
  acquisition halved year-over-year (~270/month in 2010 → ~125/month in 2011).

## How to Reproduce

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Download the raw dataset (~46MB) — see data/README.md for the URL
#    and place online_retail_II.xlsx under data/

# 3. Build the customer + monthly CSVs
python src/data_preparation.py

# 4. Sanity-check the outputs
python validate_results.py
```

The script writes [data/customers.csv](data/customers.csv) (5,878 rows,
one per customer) and [data/monthly.csv](data/monthly.csv) (25 monthly
aggregates). Both are committed to this repo so the Tableau workbook is
reproducible without re-running the prep.

## Technical Approach

**Cleaning** ([src/data_preparation.py](src/data_preparation.py))
Drops cancelled invoices (`InvoiceNo` starting with `C`), non-positive
quantities and prices, and rows missing a `CustomerID`. ~24% of raw rows
are discarded; the remaining 805K line items feed the customer aggregates.

**Feature engineering**
For every customer: total spend, order count, average order value, days
since last purchase, customer tenure, and modal country. RFM quintile
scores (1–5) for Recency, Frequency, Monetary, using rank-based bucketing
so ties land in the same quintile.

**Segmentation**
Recency-driven labels measured against the dataset's snapshot date
(2011-12-09):

| Segment | Definition | Customers |
|---|---|---|
| New | first purchase in last 30 days, single order | 135 (2.3%) |
| Active | last purchase within 90 days | 2,762 (47.0%) |
| At Risk | last purchase 91–180 days ago | 583 (9.9%) |
| Lapsed | last purchase >180 days ago | 2,398 (40.8%) |

**Monthly aggregates** roll line items up to revenue, transaction count,
distinct active customers, and new-customer acquisition per calendar month.

## Project Structure

```
data/                    Raw dataset (untracked) + derived customers.csv / monthly.csv
src/data_preparation.py  Load, clean, score, segment, aggregate
validate_results.py      Sanity checks on the prepared CSVs
tableau/                 Narrative arc, design decisions, dashboard screenshots
report/                  Static walkthrough for viewers without Tableau access
```

## Design Decisions

The dashboard is built around a 3-part narrative arc (Overview → Segment
drill-down → Trends), with chart-type, color, and annotation choices
documented so each can be defended in a sentence. Full notes:

- [tableau/narrative_arc.md](tableau/narrative_arc.md) — the question the
  dashboard answers and how each view builds the argument
- [tableau/design_decisions.md](tableau/design_decisions.md) — chart-type,
  color, annotation, and interactivity rationale

## License

MIT
