# ADR-001 — Dataset choice: Acquire Valued Shoppers Challenge

**Status:** Accepted, 2026-05-27
**Supersedes:** initial scaffolding which targeted the UCI Online Retail II dataset

## Context

The project's purpose is to demonstrate a customer-analytics dashboard
built end-to-end from real transactional data. That requires a dataset
with:

- **Real prices** (for RFM's Monetary score)
- **Real customer IDs that persist across orders** (for the customer-level
  aggregation step)
- **Real calendar dates** (for the seasonality / time-trend view)
- **Enough volume and breadth** that the customer-level patterns are
  statistically meaningful, not toy-data artifacts
- **Public availability** so reviewers can verify the source

A first pass used the **UCI Online Retail II** dataset (UK-based online
retailer, 2009–2011, ~1M transactions). It satisfied every requirement
above and produced a clean RFM-based retention narrative. But the
currency is GBP, which feels off for a portfolio targeting US-market
retail/healthcare roles.

The available alternatives, evaluated explicitly:

| Dataset | US? | Has prices? | Has dates? | Has customer IDs? | Verdict |
|---|---|---|---|---|---|
| **UCI Online Retail II** | No (UK) | ✓ | ✓ | ✓ | Initial choice; currency mismatch |
| **Tableau Superstore** | ✓ | ✓ | ✓ | ✓ | Synthetic; the most overused portfolio dataset on Kaggle |
| **Instacart Market Basket Analysis** | ✓ | ✗ | ✗ (anonymized) | ✓ | No prices, no calendar dates |
| **Olist Brazilian E-Commerce** | No (Brazil) | ✓ (BRL) | ✓ | ✓ | Just swaps GBP for BRL |
| **Acquire Valued Shoppers Challenge** | ✓ | ✓ | ✓ | ✓ | The only US-currency public dataset that has all four properties |

## Decision

Use the **Acquire Valued Shoppers Challenge** dataset.

- Source: <https://www.kaggle.com/c/acquire-valued-shoppers-challenge/data>
- Scale: ~350M transactions across 311K customers, March 2012 – July 2013
- Behind Kaggle's competition-data wall (requires sign-in + rules accept)
- The repo samples ~10K customers via deterministic modulus filtering on
  the customer ID, then chunks-and-streams the 22GB raw file. See
  [`src/data_preparation.py`](../../src/data_preparation.py).

## Consequences

### What this enabled

- Real USD currency throughout the dashboard.
- Genuinely large transactional volume — single-customer aggregates draw
  from medians of 72 orders, not 5.
- Differentiates the project from every Superstore-based portfolio piece.

### What this cost

- **The dataset is curated.** AVS hand-picked "valued shoppers" who had
  enough purchase history to make their offer-prediction task feasible.
  That means almost no customers have truly lapsed and there are almost
  no one-time buyers (11 out of 9,881 in the sample). A churn/retention
  narrative doesn't survive contact with the data. See [ADR-003](003-segmentation-framing.md).
- **Per-customer truncation.** AVS truncates each customer's transactions
  at their assigned offer date. The monthly active-customer count cliffs
  between March 2013 (9,491) and April 2013 (6,387). The analysis caps
  at 2013-03-31 to avoid those artifacts.
- **Heavy to download and process.** 2.4 GB compressed / 22 GB
  uncompressed. The script streams in 2M-row chunks (~4 min on a laptop).
  A casual contributor can't `git clone` and run — they must accept the
  Kaggle competition rules and download the raw file separately. The
  `data/README.md` documents both routes (browser, Kaggle CLI).

### What might have changed our mind

- If the goal had been "demonstrate a clean RFM-recency segmentation,"
  UCI Online Retail II is the better dataset — its long-tail customer
  base actually produces lapsed/at-risk cohorts. The pivot away from it
  was driven by the currency concern, not an analytical limitation.
- If a US dataset of similar shape to Online Retail II ever becomes
  publicly available, we'd swap to it; AVS won here on the absence of
  better alternatives, not on standalone merits.
