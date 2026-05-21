# Customer Insights Dashboard

Interactive Tableau dashboard exploring customer behavior across demographics and purchase history with trend analysis and RFM segmentation.

**Tech:** Python (data prep), Tableau

🔗 [View Interactive Dashboard on Tableau Public](#) *(link pending)*

## Overview

Narrative-driven dashboard built around a clear analytic question: how do customer segments differ in behavior over time, and where should the business focus retention effort? Includes RFM segmentation, trend-with-trendline views, and annotated callouts.

## Quick Start

```bash
pip install -r requirements.txt
python src/data_preparation.py
```

Then open the Tableau workbook (link above) or view static screenshots in [tableau/screenshots/](tableau/screenshots/).

## Project Structure

```
data/                 Input data (see data/README.md)
src/                  Data preparation script
tableau/              Dashboard screenshots, narrative arc, design notes
report/               Dashboard walkthrough for non-Tableau viewers
validate_results.py   Sanity checks on prepared data
```

## Design Philosophy

See [tableau/narrative_arc.md](tableau/narrative_arc.md) and [tableau/design_decisions.md](tableau/design_decisions.md).

## License

MIT
