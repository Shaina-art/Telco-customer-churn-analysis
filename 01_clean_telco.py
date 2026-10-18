"""
01_clean_telco.py
Cleans the Telco Customer Churn dataset and writes telco_clean.csv.
Every change is printed so it can be copied into the README.

Usage on Kaggle: set RAW_PATH to the file shown in the notebook sidebar.
"""
import glob
import numpy as np
import pandas as pd

# ---------------------------------------------------------------- load
patterns = ["/kaggle/input/**/*Telco*Churn*.csv",        # Kaggle
            "/mnt/user-data/uploads/*Telco*Churn*.csv",  # this chat environment
            "./*Telco*Churn*.csv"]                       # current folder
files = [f for p in patterns for f in glob.glob(p, recursive=True)]
if not files:
    raise FileNotFoundError("Telco CSV not found - set RAW_PATH to the path in the Kaggle sidebar.")
RAW_PATH = files[0]
df = pd.read_csv(RAW_PATH)
log = []
log.append(f"Loaded {df.shape[0]} rows x {df.shape[1]} columns")

# ---------------------------------------------------------------- 1. whitespace
# Strip stray spaces from every text column (this is what hid the blanks in TotalCharges).
text_cols = df.select_dtypes(include=["object", "string"]).columns
for c in text_cols:
    df[c] = df[c].str.strip()

# ---------------------------------------------------------------- 2. duplicates
n_dup_rows = int(df.duplicated().sum())
n_dup_ids = int(df["customerID"].duplicated().sum())
df = df.drop_duplicates()
log.append(f"Duplicate rows: {n_dup_rows}; duplicate customerIDs: {n_dup_ids} (nothing removed)")

# ---------------------------------------------------------------- 3. TotalCharges
# TotalCharges is text because 11 rows contain a blank string.
blank_mask = df["TotalCharges"] == ""
n_blank = int(blank_mask.sum())
all_zero_tenure = bool((df.loc[blank_mask, "tenure"] == 0).all())
none_churned = bool((df.loc[blank_mask, "Churn"] == "No").all())
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"].replace("", np.nan))
# These customers have tenure 0, i.e. they have not been billed yet, so the true total is 0.
# We keep the rows (they are real, active customers) and set TotalCharges to 0.
df["TotalCharges"] = df["TotalCharges"].fillna(0.0)
log.append(f"TotalCharges: {n_blank} blank rows converted to 0 "
           f"(all tenure=0: {all_zero_tenure}; none churned: {none_churned})")

# ---------------------------------------------------------------- 4. target
df["churn_flag"] = df["Churn"].map({"Yes": 1, "No": 0}).astype(int)   # 1/0 for maths and models
log.append("Churn mapped to churn_flag (Yes=1, No=0); original Churn column kept as a label")

# ---------------------------------------------------------------- 5. SeniorCitizen
# It is 0/1 while every other yes/no column is text. Keep the number, add a readable label.
df["senior_label"] = df["SeniorCitizen"].map({1: "Senior", 0: "Non-senior"})

# ---------------------------------------------------------------- 6. new features
addon_cols = ["OnlineSecurity", "OnlineBackup", "DeviceProtection",
              "TechSupport", "StreamingTV", "StreamingMovies"]
# "No internet service" is treated as "No" when counting add-ons.
df["num_addons"] = (df[addon_cols] == "Yes").sum(axis=1)

df["tenure_band"] = pd.cut(df["tenure"], bins=[-1, 12, 24, 48, 72],
                           labels=["1. 0-12 months", "2. 13-24 months",
                                   "3. 25-48 months", "4. 49-72 months"]).astype(str)

# Monthly revenue that walked away with churned customers (0 for customers who stayed).
df["monthly_revenue_lost"] = df["MonthlyCharges"] * df["churn_flag"]
log.append("Added columns: churn_flag, senior_label, num_addons, tenure_band, monthly_revenue_lost")

# ---------------------------------------------------------------- 7. checks
assert df["customerID"].is_unique
assert df.isnull().sum().sum() == 0
assert df["TotalCharges"].dtype.kind == "f"
log.append(f"Final shape: {df.shape}; missing values left: {int(df.isnull().sum().sum())}; "
           f"churn rate: {df['churn_flag'].mean()*100:.1f}%")

df.to_csv("telco_clean.csv", index=False)
print("\n".join(log))
