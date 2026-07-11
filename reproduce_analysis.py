"""
Reproduce the statistical audit for Team 5's packaged sample.

Usage
-----
python reproduce_analysis.py --data sample_data.csv --out reproduced_results

The CSV has no header and is interpreted as:
datetime, demand, temperature, wind_speed, precipitation, humidity
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


COLS = ["datetime", "demand", "temperature", "wind_speed", "precipitation", "humidity"]


def metrics(y, p):
    y = np.asarray(y, dtype=float)
    p = np.asarray(p, dtype=float)
    return {
        "MAE": mean_absolute_error(y, p),
        "RMSE": math.sqrt(mean_squared_error(y, p)),
        "MAPE(%)": np.mean(np.abs((y - p) / y)) * 100,
        "sMAPE(%)": np.mean(2 * np.abs(y - p) / (np.abs(y) + np.abs(p))) * 100,
        "R2": r2_score(y, p),
    }


def add_time_features(frame):
    x = frame.copy()
    x["hour_sin"] = np.sin(2 * np.pi * x["datetime"].dt.hour / 24)
    x["hour_cos"] = np.cos(2 * np.pi * x["datetime"].dt.hour / 24)
    return x


def main(data_path: Path, out: Path):
    out.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(data_path, header=None, names=COLS)
    df["datetime"] = pd.to_datetime(df["datetime"])
    for c in COLS[1:]:
        df[c] = pd.to_numeric(df[c])
    df["date"] = df["datetime"].dt.date
    df["hour"] = df["datetime"].dt.hour

    quality = {
        "n_rows": len(df),
        "start": df["datetime"].min(),
        "end": df["datetime"].max(),
        "missing_cells": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "duplicate_timestamps": int(df["datetime"].duplicated().sum()),
        "non_hourly_gaps": int(
            (df["datetime"].sort_values().diff().dropna() != pd.Timedelta(hours=1)).sum()
        ),
    }
    pd.Series(quality, name="value").to_csv(out / "data_quality.csv", encoding="utf-8-sig")

    df[COLS[1:]].describe().T.to_csv(out / "descriptive_statistics.csv", encoding="utf-8-sig")

    corr = []
    for c in ["temperature", "wind_speed", "precipitation", "humidity"]:
        pr, pp = pearsonr(df["demand"], df[c])
        sr, sp = spearmanr(df["demand"], df[c])
        corr.append([c, pr, pp, sr, sp])
    pd.DataFrame(
        corr,
        columns=["variable", "Pearson_r", "Pearson_p", "Spearman_rho", "Spearman_p"],
    ).to_csv(out / "correlations.csv", index=False, encoding="utf-8-sig")

    train, test = df.iloc[:72].copy(), df.iloc[72:].copy()
    rows = []
    rows.append(
        ["1h persistence", *metrics(test["demand"], df["demand"].shift(1).iloc[72:]).values()]
    )
    rows.append(
        ["24h seasonal naive", *metrics(test["demand"], df["demand"].shift(24).iloc[72:]).values()]
    )
    same_hour = train.groupby(train["datetime"].dt.hour)["demand"].mean()
    rows.append(
        ["same-hour mean", *metrics(test["demand"], test["datetime"].dt.hour.map(same_hour)).values()]
    )

    train_f, test_f = add_time_features(train), add_time_features(test)
    for label, features in [
        ("Ridge calendar", ["hour_sin", "hour_cos"]),
        (
            "Ridge calendar+observed weather",
            ["hour_sin", "hour_cos", "temperature", "wind_speed", "precipitation", "humidity"],
        ),
    ]:
        model = Pipeline(
            [
                (
                    "prep",
                    ColumnTransformer(
                        [("num", StandardScaler(), features)],
                        remainder="drop",
                    ),
                ),
                ("ridge", Ridge(alpha=10)),
            ]
        )
        model.fit(train_f, train["demand"])
        pred = model.predict(test_f)
        rows.append([label, *metrics(test["demand"], pred).values()])

    pd.DataFrame(
        rows,
        columns=["model", "MAE", "RMSE", "MAPE(%)", "sMAPE(%)", "R2"],
    ).to_csv(out / "baseline_metrics.csv", index=False, encoding="utf-8-sig")

    plt.figure(figsize=(10, 4.5))
    plt.plot(df["datetime"], df["demand"])
    plt.title("Hourly Electricity Demand")
    plt.xlabel("Datetime")
    plt.ylabel("Demand (packaged unit)")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(out / "hourly_demand.png", dpi=180)
    plt.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path("sample_data.csv"))
    parser.add_argument("--out", type=Path, default=Path("reproduced_results"))
    args = parser.parse_args()
    main(args.data, args.out)
