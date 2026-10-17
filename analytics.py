"""Deterministic calculations. Monetary source values are USD millions."""
from io import BytesIO
import pandas as pd
import numpy as np

REVENUE = "Revenue (USD millions)"
GROWTH = "Revenue growth (%)"
PRIOR = "Prior revenue (estimated, USD millions)"
CHANGE = "Revenue change (estimated, USD millions)"
RPE = "Revenue per employee (USD)"
GROUP = "Industry Group"
REQUIRED = ["Rank", "Name", "Industry", REVENUE, "Revenue growth", "Employees", "Headquarters", GROUP]


def load_data(content: bytes) -> pd.DataFrame:
    """Read the original English-format CSV and fail clearly on invalid input."""
    try:
        df = pd.read_csv(BytesIO(content), encoding="utf-8-sig", dtype=str, keep_default_na=False)
    except (ValueError, UnicodeError, pd.errors.ParserError) as exc:
        raise ValueError("The file must be a UTF-8 CSV with the original English column headers.") from exc
    df.columns = df.columns.str.strip()
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError("Missing columns: " + ", ".join(missing))
    df = df[REQUIRED].copy()
    if df.empty:
        raise ValueError("The file contains no companies.")
    for c in REQUIRED:
        df[c] = df[c].str.strip()
        if df[c].eq("").any():
            raise ValueError(f"Column '{c}' contains blank values.")
    for c in ["Rank", REVENUE, "Employees"]:
        df[c] = pd.to_numeric(df[c].str.replace(",", "", regex=False), errors="coerce")
        if df[c].isna().any() or not np.isfinite(df[c]).all() or df[c].lt(0).any():
            raise ValueError(f"Column '{c}' must contain finite, nonnegative numbers using English separators.")
    for c in ["Rank", "Employees"]:
        if df[c].mod(1).ne(0).any():
            raise ValueError(f"Column '{c}' must contain whole numbers.")
        df[c] = df[c].astype("int64")
    if df["Rank"].lt(1).any() or df["Rank"].duplicated().any():
        raise ValueError("Ranks must be positive and unique.")
    if df["Name"].str.casefold().duplicated().any():
        raise ValueError("Company names must be unique; this app expects one snapshot per company.")
    df[GROWTH] = pd.to_numeric(df["Revenue growth"].str.replace("%", "", regex=False), errors="coerce")
    if df[GROWTH].isna().any() or not np.isfinite(df[GROWTH]).all() or df[GROWTH].le(-100).any():
        raise ValueError("Revenue growth must be a finite percentage greater than -100% (for example, 6.0%).")
    df[PRIOR] = df[REVENUE] / (1 + df[GROWTH] / 100)
    df[CHANGE] = df[REVENUE] - df[PRIOR]
    df[RPE] = df[REVENUE] * 1_000_000 / df["Employees"].replace(0, np.nan)
    return df


def totals(df: pd.DataFrame) -> dict:
    current, prior = float(df[REVENUE].sum()), float(df[PRIOR].sum())
    return {"companies": len(df), "revenue": current, "employees": int(df["Employees"].sum()),
            "prior": prior, "change": current - prior,
            "growth": (current / prior - 1) * 100 if prior else float("nan")}


def share(values, denominator):
    return values / denominator * 100 if denominator else values * float("nan")


def add_shares(df: pd.DataFrame, denominator: dict) -> pd.DataFrame:
    out = df.copy()
    out["Revenue share (%)"] = share(out[REVENUE], denominator["revenue"])
    out["Employee share (%)"] = share(out["Employees"], denominator["employees"])
    return out


def sector_summary(df: pd.DataFrame, denominator: dict) -> pd.DataFrame:
    out = df.groupby(GROUP, as_index=False).agg(
        **{"Companies": ("Name", "size"), REVENUE: (REVENUE, "sum"),
           "Employees": ("Employees", "sum"), PRIOR: (PRIOR, "sum"), CHANGE: (CHANGE, "sum")})
    out[GROWTH] = (out[REVENUE] / out[PRIOR].replace(0, np.nan) - 1) * 100
    out[RPE] = out[REVENUE] * 1_000_000 / out["Employees"].replace(0, np.nan)
    out["Company share (%)"] = share(out["Companies"], denominator["companies"])
    return add_shares(out, denominator)


def filter_data(df, sectors, query="", direction="All companies"):
    out = df[df[GROUP].isin(sectors)]
    if query.strip():
        out = out[out["Name"].str.contains(query.strip(), case=False, regex=False)]
    if direction == "Growing revenue":
        out = out[out[GROWTH] > 0]
    elif direction == "Declining revenue":
        out = out[out[GROWTH] < 0]
    elif direction == "Unchanged revenue":
        out = out[out[GROWTH] == 0]
    return out.copy()
