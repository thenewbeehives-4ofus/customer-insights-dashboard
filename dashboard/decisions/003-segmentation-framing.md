# ADR-003 — Segmentation framing: M-score value tiers

**Status:** Accepted, 2026-05-27
**Supersedes:** initial framing as recency-based retention segments
(Active / At Risk / Lapsed / New)

## Context

The dataset chosen in [ADR-001](001-dataset-choice.md) is the Acquire
Valued Shoppers Challenge — by construction a curated set of "valued
shoppers" who had enough purchase history to qualify for the original
competition's offer-prediction task. This shapes the customer base in two
ways that matter for segmentation:

- **Almost no one is truly lapsed.** Every customer has a dense recent
  purchase history. With the natural recency cutoffs (Active ≤90 days,
  At Risk 91–180 days, Lapsed >180 days), 99.7% of customers fall into a
  single bucket.
- **Almost no one is a one-time buyer.** The lowest-frequency customers
  in the sample still placed 22 orders on average; the median is 72.

A recency-based segmentation answers the question "where should retention
focus?" Cleanly stating that question requires variation between
customers along the recency axis — variation that this dataset doesn't
provide. Forcing the recency framing onto AVS produced a chart where one
segment held 99% of the points and the narrative read as either trivial
("most customers are active") or misleading ("the 11 one-time buyers are
the leverage point").

The actual variation in this customer base lives along the **frequency**
and **monetary** axes:

- Order count ranges from 1 to 479 (median 72; P99 270).
- Lifetime spend ranges from \$80 to \$130K+ (median \$2,800; P99 ~\$25K).
- Average order value clusters tightly at \$55–65 across the entire base —
  it doesn't discriminate.

A segmentation strategy that surfaces real spread has to bucket on F or
M, not R.

## Decision

Bucket customers by **M-score** (quintile of lifetime spend).

- M5 = Top 20% by lifetime spend, M1 = Bottom 20%.
- Quintiles computed by rank-based bucketing so ties land in the same bin.
- The label column in `data/customers.csv` is `value_tier` ∈
  {Top 20%, Upper 20%, Middle 20%, Lower 20%, Bottom 20%}.
- R-score and F-score are still computed and stored alongside, just not
  used as the primary segmentation.

The narrative arc shifts from *"where should retention focus?"* to
*"where does the value come from, and what would move the needle?"* —
which is the question this dataset actually answers cleanly.

## Consequences

### What this enabled

- **Surfaces a real spread.** Top tier averages \$17,480 in lifetime spend
  vs \$804 for the bottom tier — a 21.7× gap. Every chart in the
  dashboard has visible structure as a result.
- **Connects to a defensible recommendation.** The diagnosis (frequency
  is the lever, not basket size — AOV is flat at \$55–65 across every
  tier) flows naturally from the segmentation choice and has a clear
  business implication.
- **Honest to the data.** The dashboard explains a real pattern in real
  numbers, not a manufactured retention story that the data doesn't
  support.

### What this cost

- **Loses the conventional RFM narrative shape.** RFM segmentation usually
  produces "Active / At Risk / Lapsed / New" cohorts — a familiar
  language for retention conversations. Switching to value tiers requires
  the viewer to read a few more sentences before the framing lands.
- **No "win back lapsed customers" recommendation falls out.** The action
  this dashboard recommends is "lift Middle-tier customers' visit
  frequency before the February peak," which is conceptually different
  and may be less recognizable to a recruiter scanning a portfolio.
- **The recency scores are computed but never visualized.** R-score lives
  in the customer CSV for completeness; nothing in the dashboard uses
  it. That's defensible but it's clutter.

### What might have changed our mind

- A different dataset (the UCI Online Retail II, for instance) supports
  the recency-based framing cleanly. The framing chosen here is a
  consequence of the dataset chosen in ADR-001, not an independent
  preference.
- If a stakeholder explicitly asked "where are customers leaking out?"
  the question would need recency variation we don't have; a different
  dataset would be required to answer it.
- A frequency-based segmentation (F-score quintiles) was considered as an
  alternative and showed a similar spread (Heavy 155 orders vs Light 22).
  We chose M because the dollar-denominated tiers communicate to
  non-technical viewers more directly than "order-count quintile" does.
