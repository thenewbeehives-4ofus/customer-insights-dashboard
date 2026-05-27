# Design Decisions

Every choice on the dashboard is here. The goal: nothing on the page that
can't be defended in a sentence.

## Chart Types

| View | Chart | Why this one |
|---|---|---|
| Overview — segment mix | Horizontal bar | Four segments, ordered by recency. Bar (not pie) so the viewer can compare lengths instead of decoding angles, and so the segment labels are readable at a glance. |
| Overview — KPI strip | Four big-number tiles | Total customers, total revenue, avg lifetime value, % Lapsed. Big numbers up top frame the rest of the page. |
| Segment drill-down | Scatter (avg order value × order count, colored by segment) | Shows two metrics at once. The Active cluster separates visually from everything else, which makes the diagnosis ("Lapsed = low frequency, low value") immediate. |
| Time trends | Line with Tableau-fitted trend line + dual-axis bar for new customers | Continuity matters more than per-period magnitude — a line lets the viewer see the November spikes as a recurring pattern, not a one-off. The trend line confirms the year-over-year direction is flat-to-down. |
| Geographic view | Filled map sized by revenue, colored by AOV | UK is 91% of customers, which a bar chart would visually hide. A map makes the geographic concentration the obvious feature. |

Bar over pie everywhere — too many segments and small differences for a pie
to be legible.

## Color

- **Single categorical palette for segments across every view** — Active blue,
  New green, At Risk amber, Lapsed red. Consistency is the point: the viewer
  learns "red = Lapsed" once and the rule holds for the rest of the dashboard.
- **Red for the At Risk and Lapsed segments** — the segments the dashboard
  is asking the business to act on. Saturated red on the bar that takes up
  40% of the chart space pulls the eye exactly where the narrative wants it.
- **Sequential blue for monetary values** on the geographic view — higher
  revenue = darker. Diverging palettes were ruled out: there's no neutral
  midpoint that makes sense for revenue.
- **Neutral gray for the new-customer overlay** on the time-trends view —
  the line for revenue is the headline series; new-customers is context.

## Annotations

Three annotations, each doing a different job. No labels that just restate
an axis.

1. **Headline KPI annotation on the Overview bar chart:**
   > "40.8% of customers haven't purchased in 6+ months."
   Sets the stakes. The number is the reason the dashboard exists.

2. **Outlier annotation on the segment scatter:**
   > "1,623 one-time buyers generate 1/12 the lifetime value of repeat customers."
   Points at the cohort the diagnosis turns on. Without this annotation the
   scatter is just a colored cloud.

3. **Trend annotation on the time-series view:**
   > "Both years peaked in November (~£1.17M, 1.65× avg). October is the
   > re-engagement window."
   Closes the loop — explains the spikes and tells the reader when to act.

## Interactivity

- **Segment dropdown filter** at the top of the dashboard — applies to every
  view. Cross-filtering enabled so clicking a segment bar in the Overview
  filters the scatter and the time series.
- **Date-range slider** for the time-series view, scoped to that view so it
  doesn't truncate the segment counts.
- **Tooltips** include the absolute number AND the period-over-period change.
  A 5% drop month-over-month is more interesting than "this month was £600K."
- No filter-for-filter's-sake. A country filter was considered and cut: the
  UK dominates so heavily that filtering away from it makes most of the
  views look broken rather than informative.
