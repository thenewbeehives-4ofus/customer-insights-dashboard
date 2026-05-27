# Dashboard Walkthrough

A static walkthrough of the Tableau dashboard for viewers who can't open
Tableau Public. Screenshots in [../tableau/screenshots/](../tableau/screenshots/).

## 1. Overview — segment mix and headline KPIs

![Overview](../tableau/screenshots/overview_with_annotations.png)

Four KPIs across the top: total customers (5,878), total revenue (£16.7M),
average lifetime spend per customer, and the headline number — **40.8% of
customers are Lapsed**. Below the KPIs, a horizontal bar chart breaks the
customer base into the four recency-based segments: New (2.3%), Active
(47.0%), At Risk (9.9%), Lapsed (40.8%). The Lapsed bar is the dominant
visual element. The annotation states the stakes plainly: half the customer
base hasn't purchased in 90+ days.

## 2. Segment Drill-Down — the one-time-buyer pattern

![Segment Drill-Down](../tableau/screenshots/segment_drilldown.png)

A scatter plot of order count vs average order value, with each point a
customer colored by segment. Two clusters emerge immediately:

- A tight Active cluster sits in the high-frequency band — these are the
  customers who placed five or more orders.
- Everyone else collapses to a wall at `order count = 1`. That's the
  **1,623 one-time buyers** — 28% of the entire customer base.

The annotation makes the comparison explicit: repeat buyers average £4,036
in lifetime spend; one-time buyers average £350. That's an 11.5× gap, and
it's where retention investment pays off.

## 3. Trends — the November re-engagement window

![Trend](../tableau/screenshots/trend_with_trendline.png)

Monthly revenue (line, with Tableau-fitted trend line) overlaid with new-
customer acquisition (gray bars, secondary axis). Two patterns stand out:

- **November is the seasonal peak** in both years. Nov 2010 hit £1.17M;
  Nov 2011 hit £1.16M — both at 1.65× the monthly average.
- **New-customer acquisition has halved year-over-year.** 2010 averaged
  ~270 new customers per month; 2011 dropped to ~125. The trend line on
  revenue is flat-to-down, masked by the November spikes.

The annotation calls out the November pattern and the October re-engagement
window that precedes it.

## Takeaway

One recommendation falls out of the three views: **re-engage one-time
buyers in October, before the November peak.**

- It's the largest reachable cohort (1,623 customers).
- It's where the lifetime-value gap is widest (11.5× between the cohorts
  on each side of the second-order threshold).
- The timing is fixed by the business's own seasonality, not a marketing
  assumption.

With new-customer acquisition halving year-over-year, the cost of doing
nothing on the existing one-time-buyer cohort goes up every quarter.
