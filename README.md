# Company Atlas

A complete Streamlit dashboard for a static snapshot of 100 companies across 13 industry groups. The interface, charts and source code are in English. The original grouped dataset is bundled, so the app works immediately without a database, API key, AI service or manual data preparation.

## Run locally

Use Python 3.12 (tested). Open a terminal inside this project folder:

```bash
python -m venv .venv
```

Activate the environment on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Or on macOS / Linux:

```bash
source .venv/bin/activate
```

Then install and run:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Publish with GitHub and Streamlit Community Cloud

1. Extract the ZIP. Upload the **contents of `company_atlas/`** to a GitHub repository, preserving the `data/` and `.streamlit/` folders. Put `app.py`, `analytics.py` and `requirements.txt` at the repository root.
2. Open [Streamlit Community Cloud](https://share.streamlit.io/) and create an app from that repository.
3. Select the repository and branch, set the entrypoint to `app.py`, select Python 3.12 in advanced settings, then deploy. No secrets are needed.
4. Share the deployed app URL. The bundled CSV is the default source on every new session.

If you upload the parent folder to GitHub instead, the entrypoint is `company_atlas/app.py`. The root layout above is recommended because it also picks up the theme configuration consistently.

Official deployment instructions: [file organization](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/file-organization), [dependencies](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies), [deployment](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy).

## Views

| View | Questions answered |
|---|---|
| Overview | Which sectors lead in revenue? Where are employees concentrated? |
| Growth & scale | Which companies and sectors grow fastest? Which add the most estimated dollars? |
| Workforce | How many employees does each company/sector have? What share do they represent? |
| Company explorer | What are one company's revenue, growth, headcount and shares? |
| Data & methodology | How are metrics calculated? What are the limitations? Download source and derived tables. |

Filters apply to all views. Choose industry groups, a company-name search and growing/declining revenue, then click **Apply filters**. Choose whether percentages use the **current selection** or **full dataset**. **Top N** limits company charts only, never totals or denominators. You can switch chart amounts between USD billions and millions.

## Data and calculations

- `Revenue (USD millions)` means revenue, not profit. A value of `648,125` means USD 648.125 billion.
- `Employees` is headcount, not jobs created. This dataset cannot measure employee growth.
- `Revenue growth` is the reported percentage supplied in the CSV. The source gives no dates or original source URL, so no calendar year is assigned.
- Prior revenue is **estimated** as `current revenue / (1 + growth / 100)`.
- Dollar change is **estimated** as `current revenue - estimated prior revenue`.
- Sector growth is **estimated** as `(sum(current) / sum(estimated prior) - 1) * 100`. A simple average of company percentages would answer a different question and is not used.
- Source rates are rounded. Reconstructed amounts are approximate and assume comparable prior periods. They are not independently verified historical amounts.
- Shares use the selected denominator, explicitly displayed above the tabs. Full-dataset shares for a filtered selection do not necessarily sum to 100%.
- Source ranks are preserved, including any order inconsistencies. Visual revenue rankings use actual revenue values.
- Categories are curated and broad. One company is assigned to one group; diversified companies are not split by segment.
- Sector totals represent **only these companies**, not the entire economy or market. Summed revenues are not GDP, market capitalization or profit.
- Revenue per employee is a descriptive ratio, not profit or a direct measure of worker productivity. Zero headcount gives an unavailable ratio.

## Update the snapshot later

Replace `data/companies.csv` with a compatible UTF-8 CSV and commit it to GitHub. Alternatively, use the optional CSV upload in the sidebar to explore a temporary replacement during the current session. Uploads do not overwrite the repository. The app validates headers, numbers, unique company names and unique ranks.

Required columns: `Rank`, `Name`, `Industry`, `Revenue (USD millions)`, `Revenue growth`, `Employees`, `Headquarters`, `Industry Group`.

English numeric formats are expected: commas separate thousands, a period marks decimals, and `6.0%` means six percent. A bare `6.0` in the growth source is also interpreted as six percent, not 600%. Rates must exceed -100% so prior revenue can be reconstructed. One row per company; no multi-year input is supported.

## Files

| File | Purpose |
|---|---|
| `app.py` | Streamlit interface, interactive Plotly charts and downloads |
| `analytics.py` | Parsing, validation, filters, aggregation and percentage calculations |
| `data/companies.csv` | Original 100-company snapshot, including English industry groups |
| `requirements.txt` | Tested direct dependency versions |
| `.streamlit/config.toml` | Dark theme and disabled usage telemetry |
| `tests/test_analytics.py` | Calculation, reconciliation and input-validation tests |
| `tests/test_app.py` | App execution and filter/denominator interaction tests |
| `DATA_NOTES.md` | Provenance, units, reconciliation totals and data limitations |

## Verify

From the project folder, after installing requirements:

```bash
python -m unittest discover -s tests -v
```

No testing packages beyond the application dependencies are required. Browser rendering was also inspected at desktop and mobile viewport sizes during preparation. Tests do not contact external services.

## A short presentation outline

Start with the sector landscape. Explain that revenue measures scale and growth measures pace. Open **Growth & scale** to compare percentage growth with estimated dollar change; bubble area shows current revenue. Open **Workforce** to show absolute headcount and employee shares, stating the percentage denominator. End on a company profile and disclose that this is a static snapshot with rounded growth rates, not a live or multi-year dashboard.
