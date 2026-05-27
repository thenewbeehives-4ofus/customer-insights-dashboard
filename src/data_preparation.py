"""Prepare the Acquire Valued Shoppers Challenge dataset for the dashboard.

The full transactions file is ~22 GB and ~350M rows, so this script:
  1. Streams data/transactions.csv.gz in chunks.
  2. Keeps customers whose ID mod SAMPLE_MODULUS == 0 — deterministic, no
     preliminary index scan needed. With ~311K customers in the file and a
     modulus of 31 the sample lands at ~10K customers, representative of the
     full customer base rather than the trainHistory offer recipients.
  3. Drops returns / non-positive amounts, defines one order = (customer, chain, date).
  4. Builds RFM-scored customer-level aggregates and monthly revenue aggregates.

Outputs:
  data/customers.csv   one row per customer with R/F/M scores and a segment label
  data/monthly.csv     one row per calendar month with revenue + customer counts

Run from the repo root:
    python src/data_preparation.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
TRANSACTIONS_PATH = REPO_ROOT / "data" / "transactions.csv.gz"
CUSTOMERS_OUT = REPO_ROOT / "data" / "customers.csv"
MONTHLY_OUT = REPO_ROOT / "data" / "monthly.csv"

# Modulus sampling on the customer ID. AVS has ~311,541 distinct customers
# in the transactions file; modulus 31 yields ~10K customers — enough to
# surface stable segment percentages and seasonality, small enough to keep
# the committed CSVs lightweight.
SAMPLE_MODULUS = 31

# Chunked read configuration.
CHUNKSIZE = 2_000_000

# Cap the analysis at the last month with complete customer coverage.
# AVS truncates each customer's transactions at their assigned offer date,
# so the file's last few months have shrinking active-customer counts that
# don't reflect business reality. Customer coverage cliffs between March
# and April 2013 (9491 → 6387 active customers), so we cut at month-end.
ANALYSIS_END_DATE = pd.Timestamp("2013-03-31")

# Value-tier labels mapped from M-score quintiles. Every customer in this
# dataset is a heavy shopper by construction (AVS hand-picked "valued
# shoppers"), so a recency-based "lapsed vs active" segmentation doesn't
# discriminate. Spend tier does — the top tier outspends the bottom by 20x+.
VALUE_TIER_LABELS = {
    5: "Top 20%",
    4: "Upper 20%",
    3: "Middle 20%",
    2: "Lower 20%",
    1: "Bottom 20%",
}


def stream_sampled_transactions() -> pd.DataFrame:
    if not TRANSACTIONS_PATH.exists():
        print(f"Missing {TRANSACTIONS_PATH}.  Download instructions: data/README.md")
        sys.exit(1)

    # Only the columns we need — saves memory.
    usecols = ["id", "chain", "date", "purchasequantity", "purchaseamount"]
    dtypes = {
        "id": "int64",
        "chain": "int32",
        "purchasequantity": "int32",
        "purchaseamount": "float32",
    }

    kept_chunks: list[pd.DataFrame] = []
    rows_seen = 0
    rows_kept = 0
    started = time.time()
    print(f"Streaming {TRANSACTIONS_PATH.name} in {CHUNKSIZE:,}-row chunks (modulus {SAMPLE_MODULUS}) ...")
    reader = pd.read_csv(
        TRANSACTIONS_PATH,
        usecols=usecols,
        dtype=dtypes,
        chunksize=CHUNKSIZE,
        compression="gzip",
    )
    for i, chunk in enumerate(reader, start=1):
        rows_seen += len(chunk)
        # Filter on modulus + positivity. Modulus sampling on the customer ID
        # gives a uniform random sample of customers across the entire file —
        # no preliminary scan required.
        keep = (
            (chunk["id"] % SAMPLE_MODULUS == 0)
            & (chunk["purchasequantity"] > 0)
            & (chunk["purchaseamount"] > 0)
        )
        sub = chunk.loc[keep].copy()
        if not sub.empty:
            kept_chunks.append(sub)
            rows_kept += len(sub)
        if i % 10 == 0:
            elapsed = time.time() - started
            print(
                f"  chunk {i}: {rows_seen:,} rows scanned, "
                f"{rows_kept:,} kept ({elapsed:.0f}s elapsed)"
            )

    if not kept_chunks:
        print("No matching rows found — modulus filter produced an empty result.")
        sys.exit(1)

    df = pd.concat(kept_chunks, ignore_index=True)
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
    df["purchaseamount"] = df["purchaseamount"].astype(float)
    pre_cap = len(df)
    df = df[df["date"] <= ANALYSIS_END_DATE].copy()
    dropped = pre_cap - len(df)
    print(
        f"Done: {rows_seen:,} rows scanned, {pre_cap:,} kept, "
        f"{dropped:,} dropped past {ANALYSIS_END_DATE.date()} "
        f"({(time.time() - started):.0f}s total)"
    )
    return df


def build_customer_features(df: pd.DataFrame, snapshot_date: pd.Timestamp) -> pd.DataFrame:
    """Aggregate transactions to one row per customer with RFM + segment label.

    An *order* is defined as one customer's transactions on a single date at a
    single chain. Returns and zero-amount rows have already been dropped upstream.
    """
    orders = (
        df.groupby(["id", "chain", "date"], sort=False)["purchaseamount"]
        .sum()
        .reset_index(name="order_total")
    )

    customer_orders = (
        orders.groupby("id")
        .agg(
            total_spend=("order_total", "sum"),
            order_count=("order_total", "count"),
            avg_order_value=("order_total", "mean"),
            first_purchase_date=("date", "min"),
            last_purchase_date=("date", "max"),
        )
        .reset_index()
        .rename(columns={"id": "CustomerID"})
    )
    customer_orders["total_spend"] = customer_orders["total_spend"].round(2)
    customer_orders["avg_order_value"] = customer_orders["avg_order_value"].round(2)
    customer_orders["days_since_last_purchase"] = (
        snapshot_date - customer_orders["last_purchase_date"]
    ).dt.days
    customer_orders["customer_tenure_days"] = (
        snapshot_date - customer_orders["first_purchase_date"]
    ).dt.days

    customer_orders["r_score"] = _quintile(customer_orders["days_since_last_purchase"], ascending=False)
    customer_orders["f_score"] = _quintile(customer_orders["order_count"], ascending=True)
    customer_orders["m_score"] = _quintile(customer_orders["total_spend"], ascending=True)
    customer_orders["rfm_score"] = (
        customer_orders["r_score"] + customer_orders["f_score"] + customer_orders["m_score"]
    )
    customer_orders["value_tier"] = customer_orders["m_score"].map(VALUE_TIER_LABELS)
    return customer_orders


def _quintile(series: pd.Series, ascending: bool) -> pd.Series:
    """Return integer quintile scores 1..5. Ties get the same bucket."""
    ranked = series.rank(method="average", ascending=ascending, pct=True)
    bins = np.clip(np.ceil(ranked * 5), 1, 5)
    return bins.astype(int)


def build_monthly_aggregates(df: pd.DataFrame, customers: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()
    orders_per_month = (
        df.groupby(["id", "chain", "date", "month"], sort=False)["purchaseamount"]
        .sum()
        .reset_index(name="order_total")
    )
    monthly = (
        orders_per_month.groupby("month")
        .agg(
            revenue=("order_total", "sum"),
            transactions=("order_total", "count"),
            active_customers=("id", "nunique"),
        )
        .reset_index()
    )
    monthly["revenue"] = monthly["revenue"].round(2)
    monthly["avg_order_value"] = (monthly["revenue"] / monthly["transactions"]).round(2)

    new_customers = (
        customers.assign(first_month=customers["first_purchase_date"].dt.to_period("M").dt.to_timestamp())
        .groupby("first_month").size().rename("new_customers").reset_index()
    )
    monthly = monthly.merge(new_customers, left_on="month", right_on="first_month", how="left").drop(columns="first_month")
    monthly["new_customers"] = monthly["new_customers"].fillna(0).astype(int)
    return monthly


def summarize(customers: pd.DataFrame, monthly: pd.DataFrame) -> None:
    print("\n=== Customer counts by value tier ===")
    tier_summary = (
        customers.groupby("m_score").agg(
            customers=("CustomerID", "count"),
            mean_spend=("total_spend", "mean"),
            mean_orders=("order_count", "mean"),
            mean_aov=("avg_order_value", "mean"),
            sum_spend=("total_spend", "sum"),
        ).sort_index(ascending=False)
    )
    print(tier_summary.round(2).to_string())

    print("\n=== Spend concentration (Pareto) ===")
    sorted_spend = customers["total_spend"].sort_values(ascending=False).reset_index(drop=True)
    total = sorted_spend.sum()
    cumshare = sorted_spend.cumsum() / total * 100
    for pct in [5, 10, 20, 50]:
        n = int(len(sorted_spend) * pct / 100)
        print(f"  Top {pct:>3d}% ({n:>5,} customers) -> {cumshare.iloc[n - 1]:5.1f}% of revenue")

    print("\n=== Monthly revenue snapshot ===")
    avg_rev = monthly["revenue"].mean()
    peak = monthly.loc[monthly["revenue"].idxmax()]
    first_m = monthly.iloc[0]
    last_m = monthly.iloc[-1]
    print(f"  Avg monthly revenue:  ${avg_rev:,.2f}")
    print(f"  First month:          {first_m['month'].strftime('%Y-%m')}  ${first_m['revenue']:,.2f}")
    print(f"  Last month:           {last_m['month'].strftime('%Y-%m')}  ${last_m['revenue']:,.2f}")
    print(f"  Peak month:           {peak['month'].strftime('%Y-%m')}  ${peak['revenue']:,.2f}  ({peak['revenue']/avg_rev:.2f}x avg)")
    print(f"  Growth factor:        {last_m['revenue'] / first_m['revenue']:.2f}x")


def main() -> int:
    df = stream_sampled_transactions()
    print(f"  rows after cleaning: {len(df):,}")
    print(f"  unique customers:    {df['id'].nunique():,}")

    snapshot_date = ANALYSIS_END_DATE
    print(f"  snapshot date: {snapshot_date.date()}")

    customers = build_customer_features(df, snapshot_date)
    monthly = build_monthly_aggregates(df, customers)

    CUSTOMERS_OUT.parent.mkdir(parents=True, exist_ok=True)
    customers.to_csv(CUSTOMERS_OUT, index=False)
    monthly.to_csv(MONTHLY_OUT, index=False)
    print(f"\nWrote {CUSTOMERS_OUT.relative_to(REPO_ROOT)}  ({len(customers):,} rows)")
    print(f"Wrote {MONTHLY_OUT.relative_to(REPO_ROOT)}  ({len(monthly):,} rows)")

    summarize(customers, monthly)
    return 0


if __name__ == "__main__":
    sys.exit(main())
