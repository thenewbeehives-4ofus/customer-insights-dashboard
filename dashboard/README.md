# Dashboard

Interactive HTML dashboard built with Plotly from the customer + monthly CSVs
produced by [../src/data_preparation.py](../src/data_preparation.py).

🔗 [View Live Dashboard](https://thenewbeehives-4ofus.github.io/customer-insights-dashboard/)

## Files in this folder

- [narrative_arc.md](narrative_arc.md) — the question the dashboard answers and how each view builds the argument
- [design_decisions.md](design_decisions.md) — chart-type, color, annotation, and interactivity rationale

## Source code for the dashboard itself

The dashboard is generated programmatically from the CSVs:

| File | What it does |
|---|---|
| [`../src/build_dashboard.py`](../src/build_dashboard.py) | Reads the CSVs, builds three Plotly figures, writes [`../docs/index.html`](../docs/index.html) with an HTML/CSS wrapper around them. |
| [`../docs/index.html`](../docs/index.html) | The committed dashboard artifact. GitHub Pages serves this from `main` branch's `/docs` directory. |

To regenerate the dashboard:

```bash
python src/data_preparation.py   # rebuilds data/customers.csv and data/monthly.csv
python src/build_dashboard.py    # rebuilds docs/index.html
```

## Dashboard structure

Three views, each backed by one of the three story beats in [narrative_arc.md](narrative_arc.md):

1. **Cumulative Revenue by Customer Rank** — Lorenz-style curve with markers at the 5%, 10%, 20% points, annotated with the concentration finding (top 10% = 49.7% of revenue)
2. **Order Count × Average Order Value** — scatter colored by value tier (M-score quintile), annotated to call out the flat-AOV / varying-frequency pattern
3. **Monthly Revenue with New-Customer Acquisition** — dual-axis line + bars with a linear trend line and the February-peak annotation

Built-in interactivity (no widgets needed):

- Hover any chart for per-point tooltips with the underlying values.
- Click a tier in the legend on the scatter to hide/show that cohort.
- Drag the rangeslider beneath the monthly chart to zoom into any time window.
- Double-click axes to reset zoom; box-select to zoom into a region.
