"""Sanity checks on the prepared CSVs.

Exits with status 1 (and prints all failures) if anything looks wrong;
otherwise prints a success line.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parent
CUSTOMERS_PATH = REPO_ROOT / "data" / "customers.csv"
MONTHLY_PATH = REPO_ROOT / "data" / "monthly.csv"

EXPECTED_VALUE_TIERS = {"Top 20%", "Upper 20%", "Middle 20%", "Lower 20%", "Bottom 20%"}
DATA_YEAR_LOWER = 2012
DATA_YEAR_UPPER = 2013


def check_files_exist(errors: list[str]) -> None:
    for path in (CUSTOMERS_PATH, MONTHLY_PATH):
        if not path.exists():
            errors.append(f"missing file: {path.relative_to(REPO_ROOT)}")


def check_customers(errors: list[str]) -> None:
    if not CUSTOMERS_PATH.exists():
        return
    df = pd.read_csv(CUSTOMERS_PATH, parse_dates=["last_purchase_date", "first_purchase_date"])

    if df.empty:
        errors.append("customers.csv has zero rows")
        return

    if df["CustomerID"].duplicated().any():
        n = int(df["CustomerID"].duplicated().sum())
        errors.append(f"customers.csv: {n} duplicate CustomerID rows")

    tiers_found = set(df["value_tier"].unique())
    missing = EXPECTED_VALUE_TIERS - tiers_found
    if missing:
        errors.append(f"customers.csv: missing value tiers {sorted(missing)}")

    tier_counts = df["value_tier"].value_counts()
    for tier in EXPECTED_VALUE_TIERS:
        if tier_counts.get(tier, 0) <= 0:
            errors.append(f"customers.csv: tier '{tier}' has 0 customers")

    for col in ("r_score", "f_score", "m_score"):
        bad = df[(df[col] < 1) | (df[col] > 5)]
        if not bad.empty:
            errors.append(f"customers.csv: {len(bad)} rows with {col} outside [1, 5]")

    min_year = df["first_purchase_date"].dt.year.min()
    max_year = df["last_purchase_date"].dt.year.max()
    if min_year < DATA_YEAR_LOWER or max_year > DATA_YEAR_UPPER:
        errors.append(
            f"customers.csv: purchase dates span {min_year}-{max_year}; "
            f"expected within {DATA_YEAR_LOWER}-{DATA_YEAR_UPPER}"
        )

    if (df["total_spend"] <= 0).any():
        errors.append("customers.csv: non-positive total_spend rows present")


def check_monthly(errors: list[str]) -> None:
    if not MONTHLY_PATH.exists():
        return
    df = pd.read_csv(MONTHLY_PATH, parse_dates=["month"])

    if df.empty:
        errors.append("monthly.csv has zero rows")
        return

    if df["month"].duplicated().any():
        errors.append("monthly.csv: duplicate month rows")

    years = df["month"].dt.year
    if years.min() < DATA_YEAR_LOWER or years.max() > DATA_YEAR_UPPER:
        errors.append(
            f"monthly.csv: months span {years.min()}-{years.max()}; "
            f"expected within {DATA_YEAR_LOWER}-{DATA_YEAR_UPPER}"
        )

    if (df["revenue"] <= 0).any():
        errors.append("monthly.csv: months with non-positive revenue present")

    if (df["active_customers"] <= 0).any():
        errors.append("monthly.csv: months with zero active customers present")


def main() -> int:
    errors: list[str] = []
    check_files_exist(errors)
    check_customers(errors)
    check_monthly(errors)

    if errors:
        print("VALIDATION FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("VALIDATION PASSED: all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
