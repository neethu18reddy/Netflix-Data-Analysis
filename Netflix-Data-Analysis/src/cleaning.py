"""
cleaning.py
-----------
Reusable data cleaning functions for the Netflix Movies and TV Shows dataset.

Every function is small, well-commented, and beginner-friendly. The goal is
that a reader can follow the WHY behind each transformation, not just the WHAT.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# 1. Load & inspect
# ---------------------------------------------------------------------------
def load_data(path: str) -> pd.DataFrame:
    """Load the Netflix CSV file into a pandas DataFrame."""
    df = pd.read_csv(path)
    return df


def inspect_data(df: pd.DataFrame) -> None:
    """Print quick facts about the dataset for a first sanity check."""
    print(f"Shape           : {df.shape}")
    print(f"Columns         : {df.columns.tolist()}")
    print("\nDtypes:")
    print(df.dtypes)
    print("\nMissing values per column:")
    print(df.isna().sum())
    print("\nDuplicated rows :", df.duplicated().sum())


# ---------------------------------------------------------------------------
# 2. Column-level cleaning
# ---------------------------------------------------------------------------
def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename columns to friendlier, snake_case names when useful."""
    return df.rename(
        columns={
            "listed_in": "genres",       # 'listed_in' is not intuitive
            "type": "content_type",      # 'type' is a Python builtin
        }
    )


def trim_and_standardize_text(df: pd.DataFrame) -> pd.DataFrame:
    """Strip whitespace and standardise casing on all string columns.

    WHY: Raw CSV data often has leading/trailing spaces and inconsistent
    casing (e.g. 'united states' vs 'United States'). Cleaning this early
    prevents phantom duplicates during group-bys.
    """
    text_cols = df.select_dtypes(include="object").columns
    for col in text_cols:
        df[col] = df[col].astype(str).str.strip()
        # Replace literal 'nan' produced by astype(str) back with NaN
        df[col] = df[col].replace({"nan": np.nan, "": np.nan})
    return df


# ---------------------------------------------------------------------------
# 3. Missing values
# ---------------------------------------------------------------------------
def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Fill / drop missing values with domain-aware defaults.

    WHY:
    - director / cast / country: unknown is more honest than dropping the row
      (would lose thousands of records).
    - date_added: only ~10 rows, safe to drop.
    - rating & duration: only a handful missing, fill with mode.
    """
    df = df.copy()

    df["director"] = df["director"].fillna("Unknown")
    df["cast"] = df["cast"].fillna("Unknown")
    df["country"] = df["country"].fillna("Unknown")

    df = df.dropna(subset=["date_added"])

    if df["rating"].isna().any():
        df["rating"] = df["rating"].fillna(df["rating"].mode()[0])
    if df["duration"].isna().any():
        df["duration"] = df["duration"].fillna(df["duration"].mode()[0])

    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Drop exact duplicate rows.

    WHY: Duplicates skew every count / percentage in EDA.
    """
    before = len(df)
    df = df.drop_duplicates()
    print(f"Removed {before - len(df)} duplicate rows")
    return df


# ---------------------------------------------------------------------------
# 4. Feature engineering
# ---------------------------------------------------------------------------
def parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Convert `date_added` to datetime and derive Year/Month added.

    WHY: Enables all time-series analysis (yearly trends, monthly seasonality).
    """
    df = df.copy()
    df["date_added"] = pd.to_datetime(df["date_added"], errors="coerce")
    df = df.dropna(subset=["date_added"])
    df["year_added"] = df["date_added"].dt.year.astype(int)
    df["month_added"] = df["date_added"].dt.month.astype(int)
    df["month_added_name"] = df["date_added"].dt.month_name()
    return df


def split_multivalue_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Split comma-separated `genres`, `country`, and `cast` into Python lists.

    WHY: These columns hold multiple values per cell. Splitting into lists
    lets us `.explode()` for per-genre / per-country analytics.
    """
    df = df.copy()

    def _split(cell: str) -> list[str]:
        if pd.isna(cell):
            return []
        return [item.strip() for item in str(cell).split(",") if item.strip()]

    df["genres_list"] = df["genres"].apply(_split)
    df["countries_list"] = df["country"].apply(_split)
    df["cast_list"] = df["cast"].apply(_split)
    return df


def add_duration_features(df: pd.DataFrame) -> pd.DataFrame:
    """Turn the free-text `duration` column into two numeric columns.

    WHY: 'duration' mixes minutes (movies) and seasons (TV shows). Splitting
    them lets us analyse each cleanly.
    """
    df = df.copy()

    # Movies duration -> minutes
    is_movie = df["content_type"] == "Movie"
    df["duration_minutes"] = np.where(
        is_movie,
        df["duration"].str.extract(r"(\d+)").astype(float)[0],
        np.nan,
    )

    # TV Show duration -> number of seasons
    is_tv = df["content_type"] == "TV Show"
    df["duration_seasons"] = np.where(
        is_tv,
        df["duration"].str.extract(r"(\d+)").astype(float)[0],
        np.nan,
    )
    return df


# ---------------------------------------------------------------------------
# 5. Orchestrator
# ---------------------------------------------------------------------------
def clean_pipeline(path: str) -> pd.DataFrame:
    """Full cleaning pipeline. Returns an analysis-ready DataFrame."""
    df = load_data(path)
    df = rename_columns(df)
    df = trim_and_standardize_text(df)
    df = handle_missing_values(df)
    df = remove_duplicates(df)
    df = parse_dates(df)
    df = split_multivalue_columns(df)
    df = add_duration_features(df)
    return df


def verify_clean(df: pd.DataFrame) -> None:
    """Final sanity check — print key facts after cleaning."""
    print("Final shape       :", df.shape)
    print("Missing per column (expected: duration_minutes NaN for TV Shows,")
    print("                   duration_seasons NaN for Movies -- by design)")
    print(df.isna().sum())
    # duplicated() cannot hash list columns, so drop them for the check.
    hashable = df.drop(columns=["genres_list", "countries_list", "cast_list"])
    print("Duplicates        :", hashable.duplicated().sum())
    print("Date range        :", df["date_added"].min(), "->", df["date_added"].max())


if __name__ == "__main__":
    clean_df = clean_pipeline("data/netflix_titles.csv")
    verify_clean(clean_df)
