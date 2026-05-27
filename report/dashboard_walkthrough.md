# Dashboard Walkthrough

A static, prose walkthrough of the dashboard for viewers reading the repo on
GitHub. The interactive version lives at
**[https://thenewbeehives-4ofus.github.io/customer-insights-dashboard/](https://thenewbeehives-4ofus.github.io/customer-insights-dashboard/)**.

## 1. The Concentration — cumulative revenue by customer rank

The first view is a Lorenz-style cumulative curve. The X-axis is "top N% of
customers ranked by lifetime spend"; the Y-axis is "cumulative share of
revenue those customers account for." A dashed reference line marks what
an even distribution would look like (45° diagonal); the actual curve sits
dramatically above it.

Three marker dots anchor the shape:

- **Top 5%** of customers (494 of 9,881) → **42% of revenue**.
- **Top 10%** → **50%**. Half of all revenue comes from a tenth of customers.
- **Top 20%** → **61%**.

The annotation calls the headline number out so the viewer leaves with one
statistic, not a curve to interpret: **10% of customers generate half the
revenue.** This is the reason the dashboard exists. Everything downstream
is about understanding *what* makes those top customers different and *how*
to grow more of them.

## 2. The Diagnosis — frequency, not basket size

A scatter plot of order count vs average order value, with each point a
customer colored by value tier (M-score quintile, deepest blue = Top 20%).
Both axes are log-scaled so the wide order-count range (1 to 500+) doesn't
visually crush the lower tiers.

Two visual patterns stand out:

- The points form a **wide horizontal band** at $55–65 AOV. The Y-axis
  spread is tight. Average order value does not climb meaningfully as you
  move up tiers.
- The X-axis spread is **two orders of magnitude**. Within the band, Top-20%
  customers sit toward the right (155 orders on average); Bottom-20% sits
  toward the left (22 orders on average). The colored gradient inside the
  band tells you the spend gap is almost entirely a *visit-count* gap.

The annotation makes it explicit: **AOV stays flat at $55–65 across all
tiers. Heavy quartile: 155 orders. Light: 22.** What separates Top customers
from Bottom isn't bigger baskets — it's more visits. The retention dollar's
job is to buy more visits per customer, not bigger transactions per visit.

## 3. The Opportunity — the February peak

A dual-axis chart: revenue as a line with a dashed linear trend line; new-
customer acquisition as gray bars on the secondary axis. A rangeslider beneath
the chart lets a viewer narrow into any time window.

Two patterns stand out:

- **Monthly revenue rises** steadily from $3.3M (March 2012) to a peak of
  **$6.1M in February 2013** — 1.40× the monthly average. The trend line
  slopes gently upward; the business is growing.
- **The February peak** is the sharpest spike. Super Bowl, Valentine's Day,
  and post-tax-refund spending compound into a clear late-winter lift.
  November–January is the pre-peak ramp window.

The annotation flags February as the seasonal high and identifies the
November–January window as the natural campaign timing for retention
programs.

## Takeaway

One recommendation falls out of the three views: **target frequency
programs at Middle-tier (M3) customers in November–January, ahead of the
February peak.**

- It's the largest reachable cohort (~20% of the base, ~$6.5M in current
  spend).
- The visit-frequency lever has the highest theoretical ceiling because
  basket size is already where it needs to be — you're not asking customers
  to change *what* they buy, just to come more often.
- The timing is fixed by the business's own seasonality, not a marketing
  assumption.

If you can move a Middle-tier customer from 75 visits/year to 95, you've
moved them up a value tier without expanding their basket. That's where
the math works.
