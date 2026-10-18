-- 02_queries.sql
-- Table: customers (loaded from telco_clean.csv)
-- churn_flag: 1 = churned, 0 = stayed. monthly_revenue_lost = MonthlyCharges for churned customers, else 0.
-- Each block starts with "-- Q<number>:" so the runner can split them.

-- Q1: Overall churn rate and monthly revenue at risk
SELECT COUNT(*)                                             AS customers,
       SUM(churn_flag)                                      AS churned,
       ROUND(100.0 * SUM(churn_flag) / COUNT(*), 1)         AS churn_pct,
       ROUND(SUM(monthly_revenue_lost), 0)                  AS monthly_revenue_lost,
       ROUND(SUM(MonthlyCharges), 0)                        AS total_monthly_revenue,
       ROUND(100.0 * SUM(monthly_revenue_lost) / SUM(MonthlyCharges), 1) AS pct_revenue_lost
FROM customers;

-- Q2: Churn by contract type
SELECT Contract,
       COUNT(*)                                     AS customers,
       SUM(churn_flag)                              AS churned,
       ROUND(100.0 * SUM(churn_flag) / COUNT(*), 1) AS churn_pct,
       ROUND(AVG(MonthlyCharges), 1)                AS avg_monthly
FROM customers
GROUP BY Contract
ORDER BY churn_pct DESC;

-- Q3: Churn by internet service
SELECT InternetService,
       COUNT(*)                                     AS customers,
       ROUND(100.0 * SUM(churn_flag) / COUNT(*), 1) AS churn_pct,
       ROUND(AVG(MonthlyCharges), 1)                AS avg_monthly
FROM customers
GROUP BY InternetService
ORDER BY churn_pct DESC;

-- Q4: Payment methods ranked by churn rate (window function)
SELECT PaymentMethod,
       COUNT(*)                                     AS customers,
       ROUND(100.0 * SUM(churn_flag) / COUNT(*), 1) AS churn_pct,
       RANK() OVER (ORDER BY 1.0 * SUM(churn_flag) / COUNT(*) DESC) AS churn_rank
FROM customers
GROUP BY PaymentMethod;

-- Q5: Churn by tenure band
SELECT tenure_band,
       COUNT(*)                                     AS customers,
       SUM(churn_flag)                              AS churned,
       ROUND(100.0 * SUM(churn_flag) / COUNT(*), 1) AS churn_pct
FROM customers
GROUP BY tenure_band
ORDER BY tenure_band;

-- Q6: Monthly charges and tenure, churned vs retained
SELECT Churn,
       COUNT(*)                       AS customers,
       ROUND(AVG(MonthlyCharges), 1)  AS avg_monthly_charge,
       ROUND(AVG(tenure), 1)          AS avg_tenure_months,
       ROUND(AVG(TotalCharges), 0)    AS avg_total_charges
FROM customers
GROUP BY Churn;

-- Q7: Churn by number of add-on services (CTE)
WITH addons AS (
  SELECT customerID, num_addons, churn_flag
  FROM customers
  WHERE InternetService <> 'No'
)
SELECT num_addons,
       COUNT(*)                                     AS customers,
       ROUND(100.0 * SUM(churn_flag) / COUNT(*), 1) AS churn_pct
FROM addons
GROUP BY num_addons
ORDER BY num_addons;

-- Q8: Top risk segments: contract x internet service (at least 100 customers)
SELECT Contract, InternetService,
       COUNT(*)                                     AS customers,
       SUM(churn_flag)                              AS churned,
       ROUND(100.0 * SUM(churn_flag) / COUNT(*), 1) AS churn_pct,
       ROUND(SUM(monthly_revenue_lost), 0)          AS monthly_revenue_lost
FROM customers
GROUP BY Contract, InternetService
HAVING COUNT(*) >= 100
ORDER BY churn_pct DESC;

-- Q9: Churn among internet customers by tech support and online security (subquery)
SELECT TechSupport, OnlineSecurity,
       COUNT(*)                                     AS customers,
       ROUND(100.0 * SUM(churn_flag) / COUNT(*), 1) AS churn_pct
FROM (SELECT * FROM customers WHERE InternetService <> 'No')
GROUP BY TechSupport, OnlineSecurity
ORDER BY churn_pct DESC;

-- Q10: Share of all churners by contract and cumulative share (window functions)
SELECT Contract,
       SUM(churn_flag) AS churned,
       ROUND(100.0 * SUM(churn_flag) / SUM(SUM(churn_flag)) OVER (), 1) AS pct_of_all_churners,
       ROUND(100.0 * SUM(SUM(churn_flag)) OVER (ORDER BY SUM(churn_flag) DESC)
             / SUM(SUM(churn_flag)) OVER (), 1) AS cumulative_pct
FROM customers
GROUP BY Contract
ORDER BY churned DESC;

-- Q11: Demographics: senior citizens, partners and dependents
SELECT senior_label, Partner, Dependents,
       COUNT(*)                                     AS customers,
       ROUND(100.0 * SUM(churn_flag) / COUNT(*), 1) AS churn_pct
FROM customers
GROUP BY senior_label, Partner, Dependents
HAVING COUNT(*) >= 100
ORDER BY churn_pct DESC;
