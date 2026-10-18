# Telco Customer Churn: Analysis and Prediction

**Tools:** Python (pandas, scikit-learn, seaborn), SQL (SQLite), Looker Studio

**Links:**
- Kaggle notebook: `https://www.kaggle.com/code/shainapereira/telco-customer-churn-analysis-and-prediction`
- Interactive dashboard: `https://datastudio.google.com/reporting/f3b7a873-3af1-487b-aa97-37967dca57f0`

![Dashboard page 1](C:\Users\shain\Downloads\Telco churn customer\dashboard 1.png)
![Dashboard page 2](C:\Users\shain\Downloads\Telco churn customer\dashboard 2.png)

## Problem
Which customers are most likely to leave, why, and how much revenue is at risk? Where should a retention team focus first?

## Data
Public "Telco Customer Churn" dataset (IBM sample): 7,043 customers, 21 columns covering demographics, services, contract, billing and `Churn` (Yes/No). 1,869 customers (26.5%) churned.

## Method
1. **Cleaning (pandas)** - no rows were removed. Fixed 11 blank `TotalCharges` values (customers with tenure 0, not yet billed, set to 0), converted churn to 1/0, and added `num_addons`, `tenure_band` and `monthly_revenue_lost`. Full before/after table: `CHANGES_AND_DECISIONS.md`.
2. **SQL (SQLite)** - 11 queries including window functions (`RANK`, cumulative share), a CTE and a subquery.
3. **EDA** - churn rate by contract, internet service, payment method and tenure; tenure and charge distributions.
4. **Modelling** - logistic regression and random forest, with a leakage-safe setup (no ID or target-derived columns, threshold chosen on training data only, test set used once).
5. **Risk tiers** - every customer scored with out-of-fold predictions and grouped into High / Medium / Low risk.
6. **Dashboard (Looker Studio)** - two pages: Overview and Churn drivers and risk.

## Key findings
1. **Overall:** 26.5% churn (1,869 of 7,043). Churned customers represent $139,131 of $456,117 monthly revenue (30.5%), higher than their customer share because churners pay more per month ($74.40 vs $61.30).
2. **Contract is the biggest driver.** Month-to-month customers churn at 42.7%, against 11.3% on one-year and 2.8% on two-year contracts. Month-to-month customers are 55% of the base but 88.6% of all churners.
3. **One segment holds most of the loss.** Month-to-month customers with fiber optic internet are 30.2% of customers (2,128) but 62.2% of churners and **72.2% of lost monthly revenue** ($100,482 per month). Their churn rate is 54.6%.
4. **New customers leave fastest.** 47.4% churn in the first 12 months, falling to 9.5% after 4 years.
5. **Payment method:** electronic check customers churn at 45.3%, against 15.2% for automatic credit card payers.
6. **Support services protect.** Among internet customers, those with neither tech support nor online security churn at 49.0%; those with both churn at 9.0%. Churn falls steadily from 52.2% with 0 add-ons to 5.3% with all 6.
7. **Demographics:** senior customers without a partner or dependents churn at 49.2%, versus 13.7% for non-seniors with both. Gender shows no real difference (26.9% vs 26.2%).

These are associations in one snapshot, not proven causes. For example, fiber customers pay more ($91.50 vs $58.10 per month on average), so price, competition or service quality could all be behind their churn; the data cannot say which.

## Model results (test set: 1,409 customers, 374 churners)
| Approach | Precision | Recall | F1 | Customers flagged |
|---|---|---|---|---|
| Rule: month-to-month contract | 42.6% | 88.0% | 0.574 | 773 |
| Rule: month-to-month + fiber optic | 52.7% | 59.4% | 0.558 | 421 |
| Logistic regression (threshold 0.57) | 54.1% | 73.0% | 0.621 | 505 |
| Random forest (threshold 0.47) | 53.8% | 76.2% | 0.631 | 530 |

- ROC-AUC is 0.84 for both models (5-fold CV 0.845 and 0.844; test set 0.842 and 0.840), so the simpler, easier-to-explain logistic regression is the main model.
- The models beat the simple rules on F1, but only modestly. Their real advantage is **ranking**: at about the same number of customers contacted (422 vs 421), the model's top 30% catches 65.0% of churners at 57.6% precision, against 59.4% and 52.7% for the month-to-month + fiber rule.
- **Most important inputs** (permutation importance, drop in ROC-AUC): tenure (0.157), monthly charges (0.045), internet service (0.045), contract (0.039).

### If the retention team contacts only the highest-scored customers (test set)
| Contact top... | Customers | Precision | Churners caught | Churned revenue caught |
|---|---|---|---|---|
| 10% | 140 | 75.7% | 28.3% | 32.1% |
| 20% | 281 | 66.2% | 49.7% | 54.3% |
| 30% | 422 | 57.6% | 65.0% | 69.6% |
| 40% | 563 | 51.5% | 77.5% | 81.8% |

### Risk tiers (all 7,043 customers, out-of-fold scores)
| Tier | Customers | Actual churn rate | Share of lost monthly revenue |
|---|---|---|---|
| High (top 20%) | 1,409 | 67.7% | 55.6% |
| Medium (next 30%) | 2,113 | 32.1% | 33.4% |
| Low (bottom 50%) | 3,521 | 6.7% | 10.9% |

## Recommendations
- **Start with month-to-month + fiber optic customers** and offer a discounted one- or two-year contract. This group holds 72% of lost monthly revenue.
- **Add early-life care** (a check-in call, onboarding help) for the first 12 months, when churn is highest.
- **Move customers from electronic check to automatic payment**, for example with a small billing incentive.
- **Bundle tech support and online security** for internet customers who have neither.
- **Use the risk score to prioritise outreach:** call the High tier first (68% of them leave without action), then work down as team capacity allows.
- Test every offer with a small control group before a full rollout, because this analysis shows association, not cause.

## Limitations
- One public dataset and one snapshot in time; patterns may not hold for other companies or periods.
- The data does not say why customers left, and has no cost figures for retention offers, so profit from a campaign cannot be calculated.
- Precision is about 54%: roughly 1 in 2 flagged customers would not have left anyway.
- Revenue figures are monthly charges, not full customer lifetime value.

## Repository contents
- `Telco_Churn_Analysis.ipynb` - full notebook (cleaning, SQL, EDA, model, tiers)
- `code/01_clean_telco.py`, `code/02_queries.sql`, `code/02_run_sql.py`, `code/03_model.py` - the same code as separate files
- `telco_clean.csv` - cleaned data
- `telco_dashboard.csv` - cleaned data plus risk score and tier (used in Looker Studio)
- `CHANGES_AND_DECISIONS.md` - every change made to the data and why
- `images/` - dashboard screenshots
