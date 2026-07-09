"""
analysis.py
-----------
Business-question functions for the Netflix EDA project.

Each function answers ONE question and returns a pandas Series or DataFrame
that can be printed, plotted, or embedded in the dashboard.
"""

from __future__ import annotations

import pandas as pd


# ---------------------------------------------------------------------------
# Content mix
# ---------------------------------------------------------------------------
def content_type_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """Movies vs TV Shows: count + percentage."""
    counts = df["content_type"].value_counts()
    pct = (counts / counts.sum() * 100).round(2)
    return pd.DataFrame({"count": counts, "percentage": pct})


# ---------------------------------------------------------------------------
# Countries
# ---------------------------------------------------------------------------
def top_countries(df: pd.DataFrame, n: int = 10) -> pd.Series:
    """Top-N producing countries after exploding the multi-country column."""
    exploded = df.explode("countries_list")
    exploded = exploded[exploded["countries_list"].notna() &
                        (exploded["countries_list"] != "Unknown")]
    return exploded["countries_list"].value_counts().head(n)


# ---------------------------------------------------------------------------
# Genres
# ---------------------------------------------------------------------------
def top_genres(df: pd.DataFrame, n: int = 10) -> pd.Series:
    """Top-N most common genres after exploding the multi-genre column."""
    exploded = df.explode("genres_list")
    return exploded["genres_list"].value_counts().head(n)


def genre_growth(df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """How the top-N genres have grown over the years added."""
    exploded = df.explode("genres_list")
    top = exploded["genres_list"].value_counts().head(top_n).index
    subset = exploded[exploded["genres_list"].isin(top)]
    pivot = (
        subset.groupby(["year_added", "genres_list"])
        .size()
        .unstack(fill_value=0)
        .sort_index()
    )
    return pivot


# ---------------------------------------------------------------------------
# Ratings
# ---------------------------------------------------------------------------
def rating_distribution(df: pd.DataFrame) -> pd.Series:
    """Most common content ratings (PG-13, TV-MA, etc.)."""
    return df["rating"].value_counts()


def rating_by_type(df: pd.DataFrame) -> pd.DataFrame:
    """Cross-tab of content_type x rating."""
    return pd.crosstab(df["rating"], df["content_type"])


# ---------------------------------------------------------------------------
# Time trends
# ---------------------------------------------------------------------------
def yearly_additions(df: pd.DataFrame) -> pd.Series:
    """Count of titles added each year."""
    return df["year_added"].value_counts().sort_index()


def monthly_additions(df: pd.DataFrame) -> pd.Series:
    """Count of titles added by calendar month (aggregated across all years)."""
    order = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ]
    counts = df["month_added_name"].value_counts()
    return counts.reindex(order).fillna(0).astype(int)


def peak_year(df: pd.DataFrame) -> int:
    """The single year with the highest number of additions."""
    return int(df["year_added"].value_counts().idxmax())


# ---------------------------------------------------------------------------
# People
# ---------------------------------------------------------------------------
def top_directors(df: pd.DataFrame, n: int = 10) -> pd.Series:
    """Top-N directors by title count (excluding 'Unknown')."""
    directors = df[df["director"] != "Unknown"]["director"]
    # A row can have multiple directors comma-separated
    exploded = directors.str.split(",").explode().str.strip()
    return exploded.value_counts().head(n)


def top_actors(df: pd.DataFrame, n: int = 10) -> pd.Series:
    """Top-N actors by appearance count."""
    exploded = df.explode("cast_list")
    exploded = exploded[exploded["cast_list"].notna() &
                        (exploded["cast_list"] != "Unknown")]
    return exploded["cast_list"].value_counts().head(n)


# ---------------------------------------------------------------------------
# Duration
# ---------------------------------------------------------------------------
def movie_duration_stats(df: pd.DataFrame) -> pd.Series:
    """Descriptive statistics for movie runtime (minutes)."""
    return df.loc[df["content_type"] == "Movie", "duration_minutes"].describe()


def tv_seasons_distribution(df: pd.DataFrame) -> pd.Series:
    """Distribution of number of seasons for TV shows."""
    seasons = df.loc[df["content_type"] == "TV Show", "duration_seasons"]
    return seasons.value_counts().sort_index()


# ---------------------------------------------------------------------------
# KPI helper for dashboard
# ---------------------------------------------------------------------------
def compute_kpis(df: pd.DataFrame) -> dict:
    """Return a small dictionary of headline KPIs for the dashboard."""
    genres = df.explode("genres_list")["genres_list"].dropna().unique()
    countries = df.explode("countries_list")["countries_list"]
    countries = countries[countries.notna() & (countries != "Unknown")].unique()
    top_country = top_countries(df, 1).index[0]

    return {
        "total_titles": int(len(df)),
        "movies": int((df["content_type"] == "Movie").sum()),
        "tv_shows": int((df["content_type"] == "TV Show").sum()),
        "countries": int(len(countries)),
        "genres": int(len(genres)),
        "most_common_rating": df["rating"].mode()[0],
        "top_country": top_country,
    }
