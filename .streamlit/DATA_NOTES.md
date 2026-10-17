# Dataset notes

## Provenance

The bundled file is the user-provided `companies.csv`, with the previously prepared English `Industry Group` column. Its current saved version was checked before creating this project. No company values were fetched from the internet, refreshed, corrected or replaced.

Source CSV SHA-256:

```text
6c335b401cbf98cc3c733e74672bfe8b3ea1e72ecafccfca500c950881397db0
```

The file does **not** supply the source URL, observation date, fiscal-year boundaries, currency-conversion methodology, or definitions of revenue and employee headcount. The dashboard therefore does not label these observations as a particular year or claim that all companies use identical accounting periods. A company ranking resembles a published list but its origin is not assumed or independently verified.

## Controls for the supplied snapshot

| Control | Value |
|---|---:|
| Companies | 100 |
| Industry groups | 13 |
| Source columns | 8 |
| Revenue, USD millions | 12,234,609 |
| Employees | 16,267,793 |
| Missing required source fields | 0 |
| Duplicate company names | 0 |
| Estimated aggregate revenue growth | 4.959353% |
| Estimated net revenue change, USD millions | 578,088.029978 |

These totals describe this file only. Calculated monetary estimates retain floating-point precision internally; the interface rounds for readability.

## Industry groups

Agribusiness; Automotive; Conglomerates; Energy; Financial Services; Food and Beverages; Healthcare and Pharmaceuticals; Industrials; Media and Entertainment; Retail; Technology; Telecommunications; Transportation and Logistics.

These are editorial categories, not an official GICS/NAICS mapping. Amazon is grouped under Retail, Tesla under Automotive, and health insurers under Healthcare and Pharmaceuticals in the supplied file. The app preserves those choices.

## Meaning of each source column

| Column | Treatment |
|---|---|
| Rank | Original positive integer rank; retained, not recalculated |
| Name | Company name; one snapshot row per company |
| Industry | Original industry description |
| Revenue (USD millions) | English thousands separators parsed as numeric; USD millions |
| Revenue growth | Reported percentage; used as supplied, not independently verified |
| Employees | Reported headcount; whole number |
| Headquarters | Descriptive location; no geocoding or state inference |
| Industry Group | Supplied English category |

Rank and actual revenue are not perfectly ordered in the source: for example, the revenue at rank 80 is below the revenue at rank 81. Revenue charts and tables sort actual revenue rather than assuming the original rank is an exact monetary order. No source value was changed.

## Growth example

If Company A reports current revenue of USD 200 million and +100% growth, its reconstructed previous revenue is USD 100 million. If Company B reports USD 150 million and -50% growth, its reconstructed previous revenue is USD 300 million. Together they moved from USD 400 million to USD 350 million: **-12.5% aggregate growth**, not the +25% simple mean of the two rates.

The same reconstruction is applied to the supplied file. Because percentages were rounded and period comparability is unknown, aggregate growth and dollar changes must be described as **estimates based on the reported rates**.

## Percentage denominators

With **Current selection**, revenue and employee shares each sum to 100% across the complete selected rows, provided their totals are positive. With **Full dataset**, the denominator remains all 100 companies while filters limit the numerator. Top N does not change either denominator. CSV exports include all filtered rows and use that same selected basis. Values such as `6.0` in calculated percentage columns mean 6.0%, not the decimal fraction 0.06.

## No historical employee series

The workforce view presents absolute headcount and its percentage distribution. It cannot infer hiring, layoffs or employee growth from this one snapshot. No multi-year revenue chart or sector-wide market-share claim is generated.
