# Dashboard Narrative Arc

The dashboard answers one question: **where should retention effort focus?**

Each view sets up a question the next view answers. A viewer reading top to
bottom builds a coherent argument rather than browsing disconnected charts.

## Part 1 — The Problem (Overview)

> **Half of all customers haven't purchased in 90+ days.**
> The Lapsed segment alone is 40.8% — 2,398 customers who haven't ordered
> in six months.

The overview lays out the segment mix and a headline KPI strip. The Lapsed
bar is the visual anchor; the annotation calls out the 40.8% / 9.9% / 47.0% /
2.3% split so the viewer leaves the page with one number, not four.

## Part 2 — The Diagnosis (Segment drill-down)

> **Lapsed customers were overwhelmingly low-frequency buyers** —
> on average 2.6 orders before going silent.
> The bigger pattern: **28% of customers are one-time buyers**, and they
> generate **1/12 the lifetime value of repeat buyers** (£350 vs £4,036).

The scatter (avg order value × order frequency, colored by segment) shows that
the Active cluster sits in the high-frequency band; everyone else collapses to
the low-frequency floor. The annotation flags the one-time-buyer cohort as the
outlier shaping the whole picture: converting a first order to a second is
the leverage point.

## Part 3 — The Opportunity (Trends)

> **November is the natural re-engagement window.**
> Both 2010 and 2011 peaked in November at ~£1.17M (1.65× the monthly average).
> Meanwhile new-customer acquisition halved from ~270/month in 2010 to
> ~125/month in 2011 — retention matters more now than it did a year ago.

The time-series view overlays monthly revenue (line + Tableau-fitted trend)
with new-customer acquisition (secondary axis). The annotation marks the
two November peaks and points to the pre-November ramp as the campaign window.

## Takeaway

The three views compose into one recommendation: **re-engage one-time buyers
in October, before the November peak.** They are the largest reachable
cohort (1,623 customers), they are the ones whose lifetime value is being
left on the table, and the timing is fixed by the seasonality of the
business.
