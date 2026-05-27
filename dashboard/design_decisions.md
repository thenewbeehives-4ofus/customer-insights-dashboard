# Design Decisions

Every choice on the dashboard is here. The goal: nothing on the page that
can't be defended in a sentence.

## Chart Types

| View | Chart | Why this one |
|---|---|---|
| Part 1 — concentration | Lorenz-style cumulative curve | A bar chart of "top 10% share" is one number; a Lorenz curve shows the whole shape. The visual gap between the actual curve and the dashed even-distribution reference line communicates "concentration" more strongly than any single statistic. Marker dots at 5%, 10%, and 20% anchor the curve to specific findings. |
| Part 2 — diagnosis | Scatter (order count × avg order value, colored by value tier) | Two metrics matter here, and the relationship between them is the whole insight. Log scale on both axes so the wide order-count range (1–500) doesn't visually crush the lower tiers. The horizontal-band shape is what the chart is asking the viewer to see — AOV stays flat while order count varies. |
| Part 3 — time trends | Dual-axis line + bars with linear trend line | Revenue as a line (continuity matters more than per-period magnitude); new-customer acquisition as gray bars on the secondary axis (context, not headline). Linear trend confirms the underlying direction is upward, with the February peak as a seasonal spike on top of the trend. |

A recency-based segmentation ("Active vs Lapsed vs At Risk") was considered
and cut. The Acquire Valued Shoppers dataset is by construction a curated set
of "valued shoppers" — every customer has dense purchase history and almost
none are truly lapsed. A recency view would have 99% of customers in one bin
and tell no story. Value-tier (M-score) segmentation surfaces a real spread.

## Color

- **Sequential blue palette across value tiers** — Bottom 20% in pale blue,
  Top 20% in deep navy. Sequential (not categorical) because the tiers have
  natural order: M1 < M2 < ... < M5. The viewer reads "darker = more valuable"
  without needing the legend.
- **Same blue across all three charts** (`#08519c` headline accent, lighter
  shades for tiers). Visual cohesion — the dashboard reads as one document,
  not three loosely-related charts.
- **Neutral gray for the new-customer overlay** on the time-trends view —
  revenue is the headline series; new-customer acquisition is context that
  shouldn't fight for attention.
- **Dashed gray line for the even-distribution reference** on the Pareto
  curve so it reads as analytic context rather than another data series.

## Annotations

Three annotations, each doing a different job. No labels that just restate
an axis.

1. **Concentration annotation on the Pareto curve:**
   > "10% of customers = half the revenue. Top 5% generate 42%; top 20% generate 61%."
   Sets the stakes. The number is the reason the dashboard exists.

2. **Frequency-lever annotation on the scatter:**
   > "AOV stays flat at $55–65 across all tiers. Heavy quartile: 155 orders avg. Light: 22."
   Points at the visual pattern (the horizontal band) and labels it. Without
   this annotation the scatter is just a colored cloud — with it, the viewer
   sees the structural finding immediately.

3. **Seasonal-peak annotation on the time-series:**
   > "February 2013: $6.1M (1.40× monthly average). Super Bowl + Valentine's + tax-refund window."
   Closes the loop — explains the spike and gives the reader the *when* of the
   recommendation in the takeaway block.

## Interactivity

The dashboard runs entirely in the browser as a single static HTML file —
no server, no widgets framework, no callbacks. Interactivity comes from
Plotly's built-ins, which is enough for this story:

- **Per-point hover tooltips** on every chart, with formatted numbers ($ for
  currency, comma separators for counts).
- **Legend toggling** on the scatter — click a tier color to hide that cohort
  and re-fit the visible series. Useful for isolating "what does the Top 20%
  look like alone?"
- **Rangeslider on the time-series view** lets viewers narrow into any
  date window. Scoped to that view only so it doesn't truncate counts on
  the other charts.
- **Box-zoom and double-click reset** on every chart. Standard Plotly.

A frequency-vs-value cross-filter was considered and cut: it would require
a JS framework (Dash/Streamlit) and an always-on server, which adds operational
complexity for marginal storytelling gain. The three views answer their own
questions; cross-filtering would mostly illustrate that the tiers behave
differently, which the colored scatter already makes obvious.
