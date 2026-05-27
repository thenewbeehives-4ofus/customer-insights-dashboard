"""Build the customer insights dashboard as a single self-contained HTML page.

Reads:
  data/customers.csv  (one row per customer, with RFM scores and value tier)
  data/monthly.csv    (one row per month, with revenue + customer counts)

Writes:
  docs/index.html     (the standalone interactive dashboard)

Run from the repo root:
    python src/build_dashboard.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go


REPO_ROOT = Path(__file__).resolve().parents[1]
CUSTOMERS_PATH = REPO_ROOT / "data" / "customers.csv"
MONTHLY_PATH = REPO_ROOT / "data" / "monthly.csv"
OUT_PATH = REPO_ROOT / "docs" / "index.html"

# Sequential blue palette: M1 (lowest value) lightest, M5 (highest) darkest.
TIER_COLORS = {
    1: "#c6dbef",
    2: "#9ecae1",
    3: "#6baed6",
    4: "#3182bd",
    5: "#08519c",
}
TIER_LABELS = {
    5: "Top 20%",
    4: "Upper 20%",
    3: "Middle 20%",
    2: "Lower 20%",
    1: "Bottom 20%",
}
TIER_ORDER = [5, 4, 3, 2, 1]


def fig_pareto(customers: pd.DataFrame) -> go.Figure:
    """Customer percentile vs cumulative revenue share — Lorenz-style curve."""
    sorted_spend = customers["total_spend"].sort_values(ascending=False).reset_index(drop=True)
    n = len(sorted_spend)
    x = np.arange(1, n + 1) / n * 100
    y = sorted_spend.cumsum() / sorted_spend.sum() * 100

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x, y=y,
            mode="lines",
            line=dict(color="#08519c", width=2.5),
            fill="tozeroy",
            fillcolor="rgba(8, 81, 156, 0.15)",
            name="Cumulative revenue share",
            hovertemplate="Top %{x:.1f}% of customers → %{y:.1f}% of revenue<extra></extra>",
        )
    )
    # Reference line: perfectly even distribution would be y=x.
    fig.add_trace(
        go.Scatter(
            x=[0, 100], y=[0, 100],
            mode="lines",
            line=dict(color="#cccccc", width=1, dash="dash"),
            name="Even distribution",
            hoverinfo="skip",
        )
    )
    # Marker dots at 5%, 10%, 20%.
    for pct in [5, 10, 20]:
        idx = int(n * pct / 100) - 1
        rev_share = y.iloc[idx]
        fig.add_trace(
            go.Scatter(
                x=[pct], y=[rev_share],
                mode="markers+text",
                marker=dict(size=10, color="#08519c", line=dict(color="white", width=2)),
                text=[f"{rev_share:.1f}%"],
                textposition="top center",
                textfont=dict(size=11, color="#08519c"),
                showlegend=False,
                hovertemplate=f"Top {pct}% → {rev_share:.1f}% of revenue<extra></extra>",
            )
        )

    fig.add_annotation(
        x=10, y=y.iloc[int(n * 0.10) - 1],
        ax=140, ay=40,
        text=(
            "<b>10% of customers = half the revenue</b><br>"
            "Top 5% generate 42%; top 20% generate 61%."
        ),
        showarrow=True, arrowhead=2, arrowwidth=1.5, arrowcolor="#08519c",
        bgcolor="rgba(255,255,255,0.95)", bordercolor="#08519c",
        borderwidth=1, borderpad=6,
        font=dict(size=12, color="#333"),
    )
    fig.update_layout(
        title=dict(text="Cumulative Revenue by Customer Rank", x=0, font=dict(size=18, color="#222")),
        xaxis=dict(title="Top N% of customers (ranked by lifetime spend)", showgrid=True, gridcolor="#eee", range=[0, 100], ticksuffix="%"),
        yaxis=dict(title="Share of total revenue", showgrid=True, gridcolor="#eee", range=[0, 105], ticksuffix="%"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=420,
        margin=dict(l=80, r=40, t=50, b=60),
        legend=dict(orientation="h", x=0, y=-0.18),
    )
    return fig


def fig_frequency_scatter(customers: pd.DataFrame) -> go.Figure:
    """Each customer plotted by order count vs avg order value, colored by value tier."""
    fig = go.Figure()
    for tier in TIER_ORDER:
        sub = customers[customers["m_score"] == tier]
        fig.add_trace(
            go.Scatter(
                x=sub["order_count"],
                y=sub["avg_order_value"],
                mode="markers",
                name=TIER_LABELS[tier],
                marker=dict(
                    color=TIER_COLORS[tier],
                    size=6,
                    opacity=0.55,
                    line=dict(width=0),
                ),
                hovertemplate=(
                    "<b>" + TIER_LABELS[tier] + "</b><br>"
                    "Order count: %{x}<br>"
                    "Avg order value: $%{y:.2f}<br>"
                    "Lifetime spend: $%{customdata:,.0f}<extra></extra>"
                ),
                customdata=sub["total_spend"],
            )
        )
    # Annotation pointing at the horizontal band where most points sit.
    fig.add_annotation(
        x=170, y=60,
        xref="x", yref="y",
        ax=-30, ay=-90,
        text=(
            "<b>AOV stays flat at $55–65 across all tiers</b><br>"
            "What separates Top customers from Bottom isn't bigger baskets —<br>"
            "it's more visits. Heavy quartile: 155 orders avg. Light: 22."
        ),
        showarrow=True, arrowhead=2, arrowwidth=1.5, arrowcolor="#444",
        bgcolor="rgba(255,255,255,0.95)", bordercolor="#444",
        borderwidth=1, borderpad=6,
        font=dict(size=12, color="#333"),
    )
    fig.update_layout(
        title=dict(
            text="Order Count × Average Order Value  (each dot = one customer)",
            x=0, font=dict(size=18, color="#222"),
        ),
        xaxis=dict(
            title="Order count (log scale)", type="log",
            showgrid=True, gridcolor="#eee",
        ),
        yaxis=dict(
            title="Avg order value ($, log scale)", type="log",
            showgrid=True, gridcolor="#eee",
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=500,
        margin=dict(l=80, r=40, t=50, b=60),
        legend=dict(title="Value tier", orientation="v", x=1.02, y=1),
    )
    return fig


def fig_monthly_trend(monthly: pd.DataFrame) -> go.Figure:
    monthly = monthly.sort_values("month").copy()
    monthly["month"] = pd.to_datetime(monthly["month"])
    x_ord = (monthly["month"] - monthly["month"].min()).dt.days.values
    slope, intercept = np.polyfit(x_ord, monthly["revenue"].values, 1)
    trend = slope * x_ord + intercept

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=monthly["month"],
            y=monthly["new_customers"],
            name="New customers",
            marker_color="#cccccc",
            yaxis="y2",
            opacity=0.7,
            hovertemplate="New customers: %{y:,}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=monthly["month"],
            y=monthly["revenue"],
            mode="lines+markers",
            name="Revenue",
            line=dict(color="#08519c", width=2.5),
            marker=dict(size=6, color="#08519c"),
            hovertemplate="<b>%{x|%b %Y}</b><br>Revenue: $%{y:,.0f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=monthly["month"],
            y=trend,
            mode="lines",
            name="Linear trend",
            line=dict(color="#08519c", width=1.5, dash="dash"),
            opacity=0.55,
            hoverinfo="skip",
        )
    )

    peak_idx = monthly["revenue"].idxmax()
    peak_row = monthly.loc[peak_idx]
    avg_rev = monthly["revenue"].mean()
    fig.add_annotation(
        x=peak_row["month"],
        y=float(peak_row["revenue"]),
        xref="x", yref="y",
        ax=-50, ay=-60,
        text=(
            "<b>February 2013 peak: $6.1M</b><br>"
            f"1.40× the {avg_rev / 1e6:.1f}M monthly average<br>"
            "Super Bowl + Valentine's + tax-refund window"
        ),
        showarrow=True, arrowhead=2, arrowwidth=1.5, arrowcolor="#08519c",
        bgcolor="rgba(255,255,255,0.95)", bordercolor="#08519c",
        borderwidth=1, borderpad=6,
        font=dict(size=12, color="#333"),
    )

    fig.update_layout(
        title=dict(
            text="Monthly Revenue with New-Customer Acquisition",
            x=0, font=dict(size=18, color="#222"),
        ),
        xaxis=dict(
            title=None,
            rangeslider=dict(visible=True, thickness=0.05),
            showgrid=True, gridcolor="#eee",
        ),
        yaxis=dict(
            title="Revenue", showgrid=True, gridcolor="#eee",
            tickformat=",.0f", tickprefix="$",
        ),
        yaxis2=dict(
            title="New customers / month",
            overlaying="y", side="right", showgrid=False,
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=520,
        margin=dict(l=80, r=80, t=50, b=80),
        legend=dict(orientation="h", x=0, y=-0.28),
        hovermode="x unified",
    )
    return fig


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Customer Insights Dashboard — Acquire Valued Shoppers (2012–2013)</title>
<style>
  :root {{ --text:#1f1f1f; --muted:#5a5a5a; --border:#e2e2e2; --bg:#fafafa; --bg-alt:#fff; --accent:#08519c; }}
  * {{ box-sizing: border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
    color: var(--text); background: var(--bg); margin: 0; line-height: 1.55;
  }}
  .container {{ max-width: 1100px; margin: 0 auto; padding: 32px 24px 64px; }}
  header.intro {{ margin-bottom: 32px; padding-bottom: 24px; border-bottom: 1px solid var(--border); }}
  h1 {{ font-size: 28px; margin: 0 0 8px 0; font-weight: 600; letter-spacing: -0.01em; }}
  .subtitle {{ font-size: 16px; color: var(--muted); margin: 0 0 16px 0; }}
  .lede {{ font-size: 15px; color: var(--text); margin: 0; max-width: 760px; }}
  .lede a {{ color: var(--accent); }}
  section.story {{ margin: 44px 0; }}
  section.story .step {{ font-size: 11px; letter-spacing: 0.12em; text-transform: uppercase; color: var(--muted); margin: 0 0 8px 0; font-weight: 600; }}
  section.story h2 {{ font-size: 22px; margin: 0 0 12px 0; font-weight: 600; letter-spacing: -0.01em; }}
  section.story p {{ font-size: 15px; color: var(--text); max-width: 760px; margin: 0 0 20px 0; }}
  .chart {{ background: var(--bg-alt); border: 1px solid var(--border); border-radius: 6px; padding: 14px; }}
  .takeaway {{ background: var(--bg-alt); border-left: 4px solid var(--accent); padding: 18px 22px; margin: 32px 0 0; max-width: 760px; border-radius: 0 4px 4px 0; }}
  .takeaway p {{ margin: 0; font-size: 15px; }}
  footer {{ margin-top: 56px; padding-top: 20px; border-top: 1px solid var(--border); font-size: 13px; color: var(--muted); }}
  footer a {{ color: var(--muted); }}
  code {{ background: #f0efe8; padding: 1px 5px; border-radius: 3px; font-size: 0.92em; }}
</style>
</head>
<body>
<div class="container">

<header class="intro">
  <h1>Customer Insights &mdash; US Retail (Acquire Valued Shoppers, 2012–2013)</h1>
  <p class="subtitle">Where does the value come from, and what would move the needle? A three-part read of 9,881 sampled customers and $56M in transactions.</p>
  <p class="lede">
    Built on the <a href="https://www.kaggle.com/c/acquire-valued-shoppers-challenge/data" target="_blank" rel="noopener">Acquire Valued Shoppers Challenge</a> dataset
    — a Kaggle release of real US grocery/CPG transactions (~350M rows across 311K customers, 2012–2013).
    Each customer is scored on Recency / Frequency / Monetary and bucketed into one of five value tiers by lifetime spend.
    Source &amp; reproducibility: <a href="https://github.com/thenewbeehives-4ofus/customer-insights-dashboard" target="_blank" rel="noopener">github.com/thenewbeehives-4ofus/customer-insights-dashboard</a>.
  </p>
</header>

<section class="story">
  <p class="step">Part 1 &mdash; The Concentration</p>
  <h2>10% of customers generate half the revenue</h2>
  <p>
    The customer base is heavily skewed. The <strong>top 5% of customers (494 of 9,881) generate 42% of revenue</strong>;
    the top 10% generate <strong>50%</strong>. The bottom 50% combined contribute only 15%. If you ranked customers
    by lifetime spend and started cutting from the bottom, you could lose half the customer base and 15% of revenue.
    Knowing who lives at the top of this curve is the entire game.
  </p>
  <div class="chart">{fig_pareto}</div>
</section>

<section class="story">
  <p class="step">Part 2 &mdash; The Diagnosis</p>
  <h2>It's visit frequency, not basket size</h2>
  <p>
    Top-tier customers don't have bigger baskets. <strong>Average order value sits at $55–65 across every tier</strong>
    from Bottom 20% to Top 20%. What separates them is how often they show up: <strong>top-frequency-quartile customers
    averaged 155 orders</strong> over the 13-month window, vs <strong>22 for the bottom quartile</strong>. The spend gap
    is a visit gap. The retention dollar's job is to convert middle-tier customers into more-frequent shoppers, not
    to push them toward bigger checkouts.
  </p>
  <div class="chart">{fig_scatter}</div>
</section>

<section class="story">
  <p class="step">Part 3 &mdash; The Opportunity</p>
  <h2>February is the seasonal high — and the conversion window</h2>
  <p>
    Monthly revenue climbed from <strong>$3.3M in March 2012</strong> to a peak of <strong>$6.1M in February 2013</strong>
    — 1.40× the monthly average. Super Bowl, Valentine's Day, and post-tax-refund spending compound into a clear
    late-winter peak. The pre-February ramp (November–January) is the natural window to push frequency programs
    aimed at Middle-tier customers: if you can move a customer from 75 orders/year to 95, you've moved them up a value tier.
  </p>
  <div class="chart">{fig_monthly}</div>
</section>

<div class="takeaway">
  <p><strong>One recommendation drops out of the three views:</strong>
  target frequency programs at Middle-tier (M3) customers in November–January, ahead of the February peak.
  They are the largest reachable cohort (~20% of the base, ~$6.5M in current spend) — and the visit-frequency
  lever has the highest theoretical ceiling because basket size is already where it needs to be.</p>
</div>

<footer>
  <p>Generated by <code>src/build_dashboard.py</code> from <code>data/customers.csv</code> and <code>data/monthly.csv</code>.
  Run <code>python src/data_preparation.py &amp;&amp; python src/build_dashboard.py</code> locally to regenerate this page from the raw dataset.</p>
</footer>

</div>
</body>
</html>
"""


def main() -> int:
    if not CUSTOMERS_PATH.exists() or not MONTHLY_PATH.exists():
        print("Missing inputs. Run src/data_preparation.py first to produce data/customers.csv and data/monthly.csv.")
        return 1

    customers = pd.read_csv(CUSTOMERS_PATH)
    monthly = pd.read_csv(MONTHLY_PATH)

    fig_p = fig_pareto(customers)
    fig_scatter = fig_frequency_scatter(customers)
    fig_month = fig_monthly_trend(monthly)

    div_p = fig_p.to_html(full_html=False, include_plotlyjs="cdn", div_id="fig-pareto")
    div_scatter = fig_scatter.to_html(full_html=False, include_plotlyjs=False, div_id="fig-scatter")
    div_month = fig_month.to_html(full_html=False, include_plotlyjs=False, div_id="fig-monthly")

    html = HTML_TEMPLATE.format(
        fig_pareto=div_p,
        fig_scatter=div_scatter,
        fig_monthly=div_month,
    )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(html, encoding="utf-8")
    print(f"Wrote {OUT_PATH.relative_to(REPO_ROOT)}  ({OUT_PATH.stat().st_size / 1024:.1f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
