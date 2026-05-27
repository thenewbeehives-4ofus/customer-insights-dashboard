# ADR-002 — Visualization stack: Plotly + GitHub Pages

**Status:** Accepted, 2026-05-27
**Supersedes:** initial scaffolding which targeted Tableau Public

## Context

The project's purpose is to demonstrate dashboard skills with a working
public artifact: a recruiter clicks a link, sees an interactive dashboard,
forms an opinion within 30 seconds. The skill being demonstrated is
**dashboard design + analytical storytelling**, not proficiency with any
specific visualization tool.

That means the choice of rendering stack is a means to an end, evaluated on
five criteria:

1. **Public hosting via a stable URL** — recruiter-clickable, no logins.
2. **Real interactivity** — hover tooltips, zoom, legend filtering at minimum.
3. **Programmatic regeneration** — the dashboard should rebuild from the
   committed CSVs without manual GUI work, so future data updates are
   one-command operations.
4. **Reproducibility** — anyone cloning the repo can rebuild the same
   artifact deterministically.
5. **Operational simplicity** — no servers to maintain, no auth tokens to
   rotate, no second platform with its own outage history.

Options evaluated:

| Stack | Free hosting? | Interactive? | Programmatic? | Reproducible from repo? | Always-on? |
|---|---|---|---|---|---|
| **Tableau Public** | ✓ | ✓ | ✗ — GUI drag-and-drop, every edit is manual | ✗ — workbook drift between local + cloud | ✓ |
| **Plotly + GitHub Pages** | ✓ | ✓ | ✓ — single Python script renders the HTML | ✓ — `python src/build_dashboard.py` is deterministic | ✓ |
| **Streamlit Cloud** | ✓ | ✓ (widgets) | ✓ | ✓ | ✗ — free-tier apps cold-start in 10–20s on first visit |
| **Plotly Dash** (self-hosted) | ✗ (requires server) | ✓ | ✓ | ✓ | depends on host |
| **Power BI** | partial | ✓ | ✗ | ✗ | mostly |
| **Google Looker Studio** | ✓ | ✓ | ✗ — GUI-driven | ✗ | ✓ |

## Decision

Render the dashboard with **Plotly** as the chart library and **GitHub
Pages** as the hosting layer.

- A single Python script ([`src/build_dashboard.py`](../../src/build_dashboard.py))
  reads the customer + monthly CSVs and writes
  [`docs/index.html`](../../docs/index.html) — three Plotly figures
  embedded in an HTML/CSS wrapper.
- GitHub Pages serves `docs/index.html` from the `main` branch.
- The Plotly runtime loads from CDN; the artifact itself is a single
  ~500 KB self-contained file.

Live at <https://thenewbeehives-4ofus.github.io/customer-insights-dashboard/>.

## Consequences

### What this enabled

- **End-to-end reproducibility.** A reviewer can clone, run two scripts,
  and produce the same dashboard. No GUI state to capture, no workbook
  file to maintain alongside the data.
- **Zero manual iteration cost.** Every design tweak (a color, an
  annotation, a chart-type swap) is a code change. The next regeneration
  picks it up. Tableau's drag-and-drop is faster for one-off iteration
  but slower across many.
- **Version control captures the dashboard itself.** Diffs on
  `docs/index.html` are noisy but the source-of-truth diffs on
  `src/build_dashboard.py` are clean and review-friendly. A Tableau
  `.twb` file is XML technically, but the version-control story is much
  weaker.
- **One platform.** GitHub already hosts the code; GitHub Pages adds the
  dashboard at the same URL prefix. No second account, no second outage
  window to track.

### What this cost

- **Less polished out of the box than Tableau.** Tableau Public dashboards
  carry a recognizable visual style that signals "data tool" to viewers.
  An HTML page rendered with Plotly looks like, well, an HTML page —
  which is fine, but it's a different aesthetic.
- **Doesn't demonstrate Tableau proficiency.** Tableau is a recognizable
  skill on job postings and shows up frequently in healthcare/retail
  analyst roles. This project no longer demonstrates it. The companion
  project [`marketing-campaign-analysis`](https://github.com/thenewbeehives-4ofus/marketing-campaign-analysis)
  uses Tableau Public for its dashboard, so the Tableau skill is still
  represented in the portfolio.
- **Cross-filtering would require a JS framework.** Plotly's built-in
  interactivity (hover, legend toggle, rangeslider) is per-chart. A true
  segment-dropdown that re-filters every view would need Dash or
  Streamlit, which would force the always-on server requirement back in
  and contradict criterion 5. See [`dashboard/design_decisions.md`](../design_decisions.md)
  for the explicit cross-filter trade-off.
- **GitHub Pages requires the repo to be public.** Free Pages doesn't work
  on private repos. This was a one-time cost (flip the repo's visibility);
  worth noting for any future portfolio repo that wants the same setup.

### What might have changed our mind

- If the project's success criteria explicitly demanded Tableau and no
  other project in the portfolio demonstrated it, that constraint would
  have outweighed reproducibility.
- If the dataset required server-side filtering or auth-gated access,
  static HTML wouldn't work; we'd need Dash/Streamlit and an always-on
  host.
- If a recruiter survey suggested viewers strongly prefer the Tableau
  Public visual style, we'd reconsider.
