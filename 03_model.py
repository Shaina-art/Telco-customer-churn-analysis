"""
03_model.py - churn prediction with a leakage-safe setup.

Design choices (each one is explained in the README):
  * Excluded columns: customerID (ID), Churn / churn_flag (target),
    monthly_revenue_lost (built from the target = leakage),
    tenure_band and senior_label (duplicates of tenure and SeniorCitizen).
  * 80/20 stratified split. The 20% test set is touched ONCE, at the end.
  * The decision threshold is chosen on out-of-fold predictions from the TRAINING set only.
"""
import numpy as np, pandas as pd
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_predict
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (roc_auc_score, precision_score, recall_score, f1_score,
                             confusion_matrix)

SEED = 42
df = pd.read_csv("telco_clean.csv")

drop_cols = ["customerID", "Churn", "churn_flag", "monthly_revenue_lost",
             "tenure_band", "senior_label"]
X = df.drop(columns=drop_cols)
y = df["churn_flag"]
num_cols = ["tenure", "MonthlyCharges", "TotalCharges", "num_addons"]
cat_cols = [c for c in X.columns if c not in num_cols + ["SeniorCitizen"]]

pre = ColumnTransformer([
    ("num", StandardScaler(), num_cols),
    ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
], remainder="passthrough")              # SeniorCitizen (0/1) passes through unchanged

models = {
    "Logistic regression": Pipeline([("pre", pre),
        ("clf", LogisticRegression(max_iter=2000, class_weight="balanced"))]),
    "Random forest": Pipeline([("pre", pre),
        ("clf", RandomForestClassifier(n_estimators=400, min_samples_leaf=5,
                                       class_weight="balanced", random_state=SEED, n_jobs=-1))]),
}

Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.20, stratify=y, random_state=SEED)
cv = StratifiedKFold(5, shuffle=True, random_state=SEED)

def metrics_at(y_true, proba, t):
    p = (proba >= t).astype(int)
    return dict(threshold=t, precision=precision_score(y_true, p), recall=recall_score(y_true, p),
                f1=f1_score(y_true, p), flagged=int(p.sum()))

results, fitted, test_proba = [], {}, {}
for name, pipe in models.items():
    oof = cross_val_predict(pipe, Xtr, ytr, cv=cv, method="predict_proba")[:, 1]   # train only
    grid = np.arange(0.20, 0.81, 0.01)
    best_t = max(grid, key=lambda t: f1_score(ytr, (oof >= t).astype(int)))        # F1-optimal on train OOF
    pipe.fit(Xtr, ytr)
    proba = pipe.predict_proba(Xte)[:, 1]
    fitted[name], test_proba[name] = pipe, proba
    row = metrics_at(yte, proba, round(float(best_t), 2))
    row.update(model=name, cv_auc=roc_auc_score(ytr, oof), test_auc=roc_auc_score(yte, proba))
    results.append(row)

res = pd.DataFrame(results)[["model", "cv_auc", "test_auc", "threshold",
                             "precision", "recall", "f1", "flagged"]].round(3)

# Baseline rules on the SAME test set
test_df = df.loc[yte.index]
rules = {
    "Rule: month-to-month contract": (test_df["Contract"] == "Month-to-month"),
    "Rule: month-to-month + fiber optic": (test_df["Contract"] == "Month-to-month")
                                          & (test_df["InternetService"] == "Fiber optic"),
}
rule_rows = []
for name, flag in rules.items():
    p = flag.astype(int)
    rule_rows.append(dict(model=name, precision=precision_score(yte, p), recall=recall_score(yte, p),
                          f1=f1_score(yte, p), flagged=int(p.sum())))
rule_res = pd.DataFrame(rule_rows).round(3)

if __name__ == "__main__":
    pd.set_option("display.width", 200); pd.set_option("display.max_columns", 20)
    print("Train/test sizes:", len(Xtr), len(Xte), "| test churners:", int(yte.sum()))
    print("\nModels (threshold chosen on training out-of-fold predictions):\n", res.to_string(index=False))
    print("\nRules on the same test set:\n", rule_res.to_string(index=False))
