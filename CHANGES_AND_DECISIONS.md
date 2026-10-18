# What I changed in the data, and why

Raw file: `WA_Fn-UseC_-Telco-Customer-Churn.csv` (7,043 rows x 21 columns).
Cleaned file: `telco_clean.csv` (7,043 rows x 26 columns). Code: `code/01_clean_telco.py`.

## What was checked and found fine (no change needed)
| Check | Result |
|---|---|
| Missing values (`isnull`) | 0 |
| Duplicate rows | 0 |
| Duplicate `customerID` | 0 |
| Rows removed | **0** (all 7,043 customers kept) |

## Changes made
| # | Change | Before | After | Why |
|---|---|---|---|---|
| 1 | Trimmed spaces in all text columns | stray spaces possible | clean text | Spaces were hiding the blank values in `TotalCharges` |
| 2 | `TotalCharges` converted from text to number | text (11 values were a blank space) | decimal number | The column could not be summed or averaged as text |
| 3 | 11 blank `TotalCharges` set to **0** | blank | 0.0 | All 11 customers have `tenure` = 0 (not billed yet) and none churned, so a total of 0 is the true value. Rows were kept because they are real, active customers |
| 4 | Added `churn_flag` | `Churn` = Yes/No | 1 / 0 | Lets SQL and models count and average churn. The original `Churn` text column is kept |
| 5 | Added `senior_label` | `SeniorCitizen` = 0/1 | "Senior" / "Non-senior" | `SeniorCitizen` is the only yes/no column stored as a number; the label is easier to read in charts. The 0/1 column is kept |
| 6 | Added `num_addons` | none | 0 to 6 | Counts how many of the 6 add-on services a customer has (online security, backup, device protection, tech support, streaming TV, streaming movies). "No internet service" counts as no add-on |
| 7 | Added `tenure_band` | `tenure` in months | 4 bands: 0-12, 13-24, 25-48, 49-72 | Easier to chart and explain than 73 separate values. Band names start with a number so they sort correctly in Looker Studio |
| 8 | Added `monthly_revenue_lost` | none | `MonthlyCharges` if churned, else 0 | Turns churn into money: summing it gives the monthly revenue that left |

## Things I deliberately did NOT change
- **"No internet service" and "No phone service" values** were left as they are. They are real categories (they tell you the customer has no such service), not errors.
- **`customerID`** stays in the cleaned file so you can count customers in the dashboard. It is excluded from the model because an ID has no predictive meaning.
- **No outliers were removed.** `MonthlyCharges` ($18.25 to $118.75) and `tenure` (0 to 72 months) are in realistic ranges.

## Model decisions (code: `code/03_model.py`)
| Decision | Reason |
|---|---|
| `monthly_revenue_lost` excluded from the model | It is calculated from the answer (churn), so including it would be **data leakage** and give fake accuracy |
| `tenure_band` and `senior_label` excluded | They only repeat `tenure` and `SeniorCitizen` |
| 80/20 split with the test set used only once | Gives an honest estimate of performance on unseen customers |
| Decision threshold chosen on **training** out-of-fold predictions only | Choosing it on the test set would make results look better than they are |
| `class_weight="balanced"` | Only 26.5% of customers churn, so the model must not ignore the minority class |
| Precision, recall, F1 and ROC-AUC reported | Accuracy alone is misleading with imbalanced classes |

## The extra file for the dashboard
`telco_dashboard.csv` = `telco_clean.csv` plus two columns, `churn_risk_score` and `risk_tier`. Every customer is scored by a model that never saw that customer (5-fold out-of-fold predictions), so the tiers are honest, not memorised. Tiers: High = top 20% of scores, Medium = next 30%, Low = bottom 50%.
