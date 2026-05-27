# Data

This folder holds the raw dataset (untracked) and the derived CSVs that feed
the dashboard (committed).

## Files

| File | Tracked? | Notes |
|---|---|---|
| `transactions.csv.gz` | No | Raw input (~2.4 GB compressed, ~22 GB uncompressed). Download from Kaggle (steps below). |
| `customers.csv` | Yes | One row per sampled customer with RFM scores and a value-tier label. 9,881 rows. |
| `monthly.csv` | Yes | One row per calendar month with revenue and customer counts. 13 rows. |

The other competition files (`offers.csv`, `trainHistory.csv`, `testHistory.csv`,
`sampleSubmission.csv`) are not used by the analysis.

## Source

**Acquire Valued Shoppers Challenge** — Kaggle competition dataset of real
US grocery / CPG retail transactions.

<https://www.kaggle.com/c/acquire-valued-shoppers-challenge/data>

~350M transactions across 311K unique customers, March 2012 – July 2013.
Columns in `transactions.csv`: `id` (customer), `chain`, `dept`, `category`,
`company`, `brand`, `date`, `productsize`, `productmeasure`, `purchasequantity`,
`purchaseamount` (USD).

## How to obtain

The data is behind Kaggle's competition-data wall — anyone can access it,
but you must sign in to Kaggle and accept the competition rules first.

**Option A — Manual download (no CLI needed):**

1. Sign in to Kaggle. Go to
   <https://www.kaggle.com/c/acquire-valued-shoppers-challenge/data>.
2. Click **Late Submission** / **Join Competition** → accept the rules.
3. Download `transactions.csv.gz` from the Data tab. Place it in this folder.

**Option B — Kaggle CLI:**

```bash
pip install kaggle
# Create an API token at https://www.kaggle.com/settings → API → Create New Token
# Move the downloaded kaggle.json to ~/.kaggle/kaggle.json
# Accept the competition rules in your browser (required even with the CLI)
kaggle competitions download -c acquire-valued-shoppers-challenge -p data/
unzip -o data/acquire-valued-shoppers-challenge.zip -d data/
```

After the raw file is in place, run `python src/data_preparation.py` from
the project root to regenerate `customers.csv` and `monthly.csv`.

## Why this dataset

A US dataset with real prices, real dates, and real customer IDs is rare on
public data sites. The classic "Online Retail II" UCI dataset is well-suited
to RFM work but is UK-based with GBP currency; "Superstore Sales" is US/USD
but synthetic and overused; Instacart's public data has neither prices nor
absolute dates. Acquire Valued Shoppers is the closest public match for a
real US retail RFM analysis.
