# Tableau Dashboard

Interactive dashboard built on the customer + monthly CSVs produced by
[../src/data_preparation.py](../src/data_preparation.py).

🔗 [View Interactive Dashboard on Tableau Public](#) *(link pending)*

## Files

- [narrative_arc.md](narrative_arc.md) — the question the dashboard answers
  and how each view builds the argument
- [design_decisions.md](design_decisions.md) — chart-type, color,
  annotation, and interactivity rationale
- [screenshots/](screenshots/) — static images of each view for offline browsing

## Dashboard structure

Four views, assembled onto a single dashboard with a segment dropdown and a
date-range slider:

1. **Overview** — KPI strip + segment bar chart with the headline annotation
2. **Segment drill-down** — scatter (avg order value × order count) colored by segment
3. **Time trends** — monthly revenue line with Tableau trend line, overlaid with new-customer acquisition
4. **Geographic view** — filled map of revenue by country

The dashboard is built directly from `data/customers.csv` (one row per
customer) and `data/monthly.csv` (one row per month). Both files live in
the repo so the workbook is reproducible.
