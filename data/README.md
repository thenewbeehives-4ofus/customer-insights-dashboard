# Data

This folder holds the raw dataset (untracked) and the derived CSVs that feed
the Tableau dashboard (committed).

## Files

| File | Tracked? | Notes |
|---|---|---|
| `online_retail_II.xlsx` | No | Raw input. Download from UCI (link below). |
| `customers.csv` | Yes | One row per customer with RFM scores and a segment label. 5,878 rows. |
| `monthly.csv` | Yes | One row per calendar month with revenue and customer counts. 25 rows. |

## Source

**UCI Machine Learning Repository — Online Retail II**
<https://archive.ics.uci.edu/dataset/502/online+retail+ii>

~1.07M transactions from a UK-based online retailer between
December 2009 and December 2011. Columns: `Invoice`, `StockCode`,
`Description`, `Quantity`, `InvoiceDate`, `Price`, `Customer ID`, `Country`.

## How to obtain

```bash
# Download and extract
curl -sSL -o online_retail_II.zip \
  "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip"
unzip online_retail_II.zip -d .
rm online_retail_II.zip
```

After the raw file is in place, run `python ../src/data_preparation.py`
from the project root to regenerate `customers.csv` and `monthly.csv`.
