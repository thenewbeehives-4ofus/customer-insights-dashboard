"""Prepare the Online Retail II dataset for Tableau.

Outputs two CSVs:
  - data/customers.csv   one row per customer with RFM scores and a segment label
  - data/monthly.csv     one row per calendar month with revenue + customer counts

Run from the repo root:
    python src/data_preparation.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = REPO_ROOT / "data" / "online_retail_II.xlsx"
CUSTOMERS_OUT = REPO_ROOT / "data" / "customers.csv"
MONTHLY_OUT = REPO_ROOT / "data" / "monthly.csv"

# Recency thresholds (in days) used to assign the four customer segments.
# Measured against the most recent date in the dataset, not today.
RECENCY_ACTIVE_DAYS = 90
RECENCY_AT_RISK_DAYS = 180
# A customer is "New" if their first purchase was within this window AND
# they have only ordered once (so we don't relabel an active customer as new).
NEW_CUSTOMER_DAYS = 30


def load_raw(path: Path) -> pd.DataFrame:
    """Load both sheets of the Online Retail II workbook and concatenate."""
    if not path.exists():
        print(f"Raw dataset not found at {path}.")
        print("Download instructions: data/README.md")
        sys.exit(1)
    sheets = pd.read_excel(path, sheet_name=None, engine="openpyxl")
    frames = [df.assign(_sheet=name) for name, df in sheets.items()]
    raw = pd.concat(frames, ignore_index=True)
    raw.columns = [c.strip() for c in raw.columns]
    return raw


def clean(raw: pd.DataFrame) -> pd.DataFrame:
    """Drop cancelled orders, non-positive quantities/prices, and missing IDs."""
    df = raw.rename(columns={"Customer ID": "CustomerID"}).copy()
    df = df.dropna(subset=["CustomerID", "InvoiceDate"])
    df["InvoiceNo"] = df["Invoice"].astype(str)
    df = df[~df["InvoiceNo"].str.startswith("C")]
    df = df[df["Quantity"] > 0]
    df = df[df["Price"] > 0]
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["CustomerID"] = df["CustomerID"].astype(int)
    df["LineRevenue"] = df["Quantity"] * df["Price"]
    return df


def build_customer_features(df: pd.DataFrame, snapshot_date: pd.Timestamp) -> pd.DataFrame:
    """Aggregate transactions to one row per customer with RFM + segment label."""
    grouped = df.groupby("CustomerID")
    customers = pd.DataFrame({
        "total_spend": grouped["LineRevenue"].sum().round(2),
        "order_count": grouped["InvoiceNo"].nunique(),
        "last_purchase_date": grouped["InvoiceDate"].max(),
        "first_purchase_date": grouped["InvoiceDate"].min(),
        "country": grouped["Country"].agg(lambda s: s.mode().iat[0]),
    }).reset_index()

    customers["avg_order_value"] = (customers["total_spend"] / customers["order_count"]).round(2)
    customers["days_since_last_purchase"] = (snapshot_date - customers["last_purchase_date"]).dt.days
    customers["customer_tenure_days"] = (snapshot_date - customers["first_purchase_date"]).dt.days

    # RFM quintile scores. Recency uses inverted ranking so that "most recent"
    # = score 5; frequency and monetary use natural ranking.
    customers["r_score"] = _quintile(customers["days_since_last_purchase"], ascending=False)
    customers["f_score"] = _quintile(customers["order_count"], ascending=True)
    customers["m_score"] = _quintile(customers["total_spend"], ascending=True)
    customers["rfm_score"] = customers["r_score"] + customers["f_score"] + customers["m_score"]

    customers["segment"] = customers.apply(_assign_segment, axis=1)
    return customers


def _quintile(series: pd.Series, ascending: bool) -> pd.Series:
    """Return integer quintile scores 1..5. Ties get the same bucket."""
    ranked = series.rank(method="average", ascending=ascending, pct=True)
    bins = np.clip(np.ceil(ranked * 5), 1, 5)
    return bins.astype(int)


def _assign_segment(row: pd.Series) -> str:
    """Recency-driven segment with a 'New' override for first-time recent buyers."""
    if row["order_count"] == 1 and row["customer_tenure_days"] <= NEW_CUSTOMER_DAYS:
        return "New"
    if row["days_since_last_purchase"] <= RECENCY_ACTIVE_DAYS:
        return "Active"
    if row["days_since_last_purchase"] <= RECENCY_AT_RISK_DAYS:
        return "At Risk"
    return "Lapsed"


def build_monthly_aggregates(df: pd.DataFrame, customers: pd.DataFrame) -> pd.DataFrame:
    """Per-month revenue, transaction count, distinct customers, and new customers."""
    df = df.copy()
    df["month"] = df["InvoiceDate"].dt.to_period("M").dt.to_timestamp()

    monthly = df.groupby("month").agg(
        revenue=("LineRevenue", "sum"),
        transactions=("InvoiceNo", "nunique"),
        active_customers=("CustomerID", "nunique"),
    ).reset_index()
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
    """Print headline numbers so the narrative + README can be written from real data."""
    seg_counts = customers["segment"].value_counts()
    seg_pct = (seg_counts / len(customers) * 100).round(1)
    print("\n=== Customer counts by segment ===")
    for seg in ["New", "Active", "At Risk", "Lapsed"]:
        n = int(seg_counts.get(seg, 0))
        pct = float(seg_pct.get(seg, 0.0))
        print(f"  {seg:8s} {n:6d}  ({pct:5.1f}%)")
    print(f"  Total    {len(customers):6d}")

    avg_spend_by_seg = customers.groupby("segment")["total_spend"].mean().round(2)
    print("\n=== Avg lifetime spend by segment ===")
    for seg, val in avg_spend_by_seg.items():
        print(f"  {seg:8s} £{val:,.2f}")

    print("\n=== Monthly revenue snapshot ===")
    avg_rev = monthly["revenue"].mean()
    peak = monthly.loc[monthly["revenue"].idxmax()]
    print(f"  Avg monthly revenue:  £{avg_rev:,.2f}")
    print(f"  Peak month:           {peak['month'].strftime('%Y-%m')}  £{peak['revenue']:,.2f}  ({peak['revenue']/avg_rev:.2f}x avg)")


def main() -> int:
    print(f"Loading {RAW_PATH.name} ...")
    raw = load_raw(RAW_PATH)
    print(f"  raw rows: {len(raw):,}")

    df = clean(raw)
    print(f"  rows after cleaning: {len(df):,}")

    snapshot_date = df["InvoiceDate"].max().normalize()
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
