# Architecture Decision Records

This folder documents the three architectural decisions that shape the
project. Each ADR follows the standard pattern: Context, Decision,
Consequences. Together they explain why the repo looks the way it does and
which paths were considered but not taken.

| # | Decision | Status |
|---|---|---|
| [001](001-dataset-choice.md) | Use the Acquire Valued Shoppers Challenge dataset instead of UCI Online Retail II | Accepted, 2026-05-27 |
| [002](002-visualization-stack.md) | Render the dashboard with Plotly + GitHub Pages instead of Tableau Public | Accepted, 2026-05-27 |
| [003](003-segmentation-framing.md) | Segment customers by M-score (lifetime-spend quintile) rather than recency | Accepted, 2026-05-27 |

## Why these are written down

The repo's current shape is the result of pivots, not a straight-line build.
Anyone reading the code will see the result; an ADR captures *why* each path
was chosen and what the alternatives looked like. That matters here because
the analytical framing (spend concentration + visit-frequency lever) is not
the only valid story this dataset could tell — it's the one that survived
contact with the data's actual characteristics.

## How these relate

The three decisions are linked, not independent:

- **ADR-001** chose the dataset, but the dataset's characteristics
  ("valued shoppers" — every customer is engaged) forced the framing decision.
- **ADR-003** chose the framing in response. A churn/recency narrative would
  have produced 99% of customers in one bucket and told no story; spend-tier
  segmentation surfaces a 21× spread between top and bottom.
- **ADR-002** chose the rendering stack, and is the most independent of the
  three — the dashboard could have been built in Tableau on top of the same
  CSVs without changing 001 or 003.

Read 001 → 003 → 002 to follow the chain.
