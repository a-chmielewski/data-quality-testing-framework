import json
from pathlib import Path

import pandas as pd

ART_DIR = Path("artifacts")
ART_DIR.mkdir(parents=True, exist_ok=True)

recent_csv = Path("data/311_recent.csv")
hist_csv = Path("data/311_hist.csv")


def top_share(df: pd.DataFrame, col: str, k=5):
    s = df[col].fillna("NULL").value_counts(normalize=True).head(k)
    return [{"value": idx, "share": float(round(v, 4))} for idx, v in s.items()]


def null_rate(df: pd.DataFrame, cols: list[str]):
    out = {}
    for c in cols:
        out[c] = float(round(df[c].isna().mean(), 4))
    return out


def main():
    df_recent = pd.read_csv(recent_csv)
    df_hist = pd.read_csv(hist_csv)

    metrics = {
        "rows_recent": int(len(df_recent)),
        "rows_hist": int(len(df_hist)),
        "nulls_recent": null_rate(
            df_recent, ["created_date", "complaint_type", "borough"]
        ),
        "nulls_hist": null_rate(df_hist, ["created_date", "complaint_type", "borough"]),
        "top_complaint_type_recent": top_share(df_recent, "complaint_type"),
        "top_complaint_type_hist": top_share(df_hist, "complaint_type"),
        "generated_by": "build_metrics.py",
    }

    with open(ART_DIR / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print("Wrote artifacts/metrics.json")


if __name__ == "__main__":
    main()
