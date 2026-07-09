"""
visualization.py
----------------
Chart-builder functions. Each function accepts a DataFrame plus an optional
`save_path`, produces a professionally styled Matplotlib/Seaborn figure and
saves it as a PNG so the README can reference it.
"""

from __future__ import annotations

import os
from typing import Optional

import matplotlib.pyplot as plt
import seaborn as sns

from . import analysis as an  # noqa: F401  (kept for direct-run usage)

# ---- Global styling ---------------------------------------------------------
sns.set_theme(style="whitegrid", context="talk")
NETFLIX_RED = "#E50914"
NETFLIX_DARK = "#221F1F"
PALETTE = [NETFLIX_RED, "#B81D24", "#F5F5F1", "#221F1F", "#831010"]


def _save(fig: plt.Figure, save_path: Optional[str]) -> None:
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        fig.savefig(save_path, dpi=140, bbox_inches="tight", facecolor="white")


# ---------------------------------------------------------------------------
# 1. Movies vs TV Shows -- pie
# ---------------------------------------------------------------------------
def plot_content_type_pie(df, save_path: Optional[str] = None) -> plt.Figure:
    counts = df["content_type"].value_counts()
    fig, ax = plt.subplots(figsize=(8, 6))
    colors = [NETFLIX_RED, NETFLIX_DARK]
    wedges, texts, autotexts = ax.pie(
        counts.values, labels=counts.index, autopct="%1.1f%%",
        colors=colors, startangle=90, wedgeprops={"edgecolor": "white", "linewidth": 2},
        textprops={"fontsize": 13},
    )
    for t in autotexts:
        t.set_color("white")
        t.set_fontweight("bold")
    ax.set_title("Movies vs TV Shows on Netflix", fontsize=16, fontweight="bold")
    _save(fig, save_path)
    return fig


# ---------------------------------------------------------------------------
# 2. Top countries -- horizontal bar
# ---------------------------------------------------------------------------
def plot_top_countries(df, n: int = 10, save_path: Optional[str] = None) -> plt.Figure:
    from .analysis import top_countries
    data = top_countries(df, n).sort_values()
    fig, ax = plt.subplots(figsize=(10, 7))
    bars = ax.barh(data.index, data.values, color=NETFLIX_RED, edgecolor=NETFLIX_DARK)
    for bar in bars:
        w = bar.get_width()
        ax.text(w + max(data.values) * 0.01, bar.get_y() + bar.get_height() / 2,
                f"{int(w)}", va="center", fontsize=11)
    ax.set_title(f"Top {n} Countries by Netflix Titles", fontsize=16, fontweight="bold")
    ax.set_xlabel("Number of Titles")
    ax.set_ylabel("Country")
    _save(fig, save_path)
    return fig


# ---------------------------------------------------------------------------
# 3. Top genres -- bar
# ---------------------------------------------------------------------------
def plot_top_genres(df, n: int = 10, save_path: Optional[str] = None) -> plt.Figure:
    from .analysis import top_genres
    data = top_genres(df, n)
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=data.values, y=data.index, ax=ax, palette="Reds_r", hue=data.index, legend=False)
    ax.set_title(f"Top {n} Genres on Netflix", fontsize=16, fontweight="bold")
    ax.set_xlabel("Number of Titles")
    ax.set_ylabel("Genre")
    for i, v in enumerate(data.values):
        ax.text(v + max(data.values) * 0.01, i, str(int(v)), va="center", fontsize=11)
    _save(fig, save_path)
    return fig


# ---------------------------------------------------------------------------
# 4. Ratings distribution -- countplot
# ---------------------------------------------------------------------------
def plot_rating_distribution(df, save_path: Optional[str] = None) -> plt.Figure:
    order = df["rating"].value_counts().index
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.countplot(data=df, x="rating", order=order, ax=ax,
                  palette="Reds_r", hue="rating", legend=False)
    ax.set_title("Distribution of Content Ratings", fontsize=16, fontweight="bold")
    ax.set_xlabel("Rating")
    ax.set_ylabel("Number of Titles")
    plt.xticks(rotation=45, ha="right")
    _save(fig, save_path)
    return fig


# ---------------------------------------------------------------------------
# 5. Titles added over time -- line
# ---------------------------------------------------------------------------
def plot_yearly_trend(df, save_path: Optional[str] = None) -> plt.Figure:
    from .analysis import yearly_additions
    data = yearly_additions(df)
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(data.index, data.values, marker="o", color=NETFLIX_RED,
            linewidth=2.5, markersize=8, markerfacecolor=NETFLIX_DARK)
    ax.fill_between(data.index, data.values, color=NETFLIX_RED, alpha=0.15)
    ax.set_title("Netflix Titles Added per Year", fontsize=16, fontweight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel("Number of Titles Added")
    ax.grid(True, alpha=0.3)
    _save(fig, save_path)
    return fig


# ---------------------------------------------------------------------------
# 6. Monthly seasonality -- bar
# ---------------------------------------------------------------------------
def plot_monthly_trend(df, save_path: Optional[str] = None) -> plt.Figure:
    from .analysis import monthly_additions
    data = monthly_additions(df)
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(data.index, data.values, color=NETFLIX_RED, edgecolor=NETFLIX_DARK)
    for b in bars:
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 5,
                str(int(b.get_height())), ha="center", fontsize=10)
    ax.set_title("Titles Added by Month (all years)", fontsize=16, fontweight="bold")
    ax.set_xlabel("Month")
    ax.set_ylabel("Number of Titles")
    plt.xticks(rotation=45, ha="right")
    _save(fig, save_path)
    return fig


# ---------------------------------------------------------------------------
# 7. Movie duration -- histogram
# ---------------------------------------------------------------------------
def plot_movie_duration_hist(df, save_path: Optional[str] = None) -> plt.Figure:
    minutes = df.loc[df["content_type"] == "Movie", "duration_minutes"].dropna()
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.hist(minutes, bins=40, color=NETFLIX_RED, edgecolor=NETFLIX_DARK, alpha=0.85)
    ax.axvline(minutes.mean(), color=NETFLIX_DARK, linestyle="--",
               linewidth=2, label=f"Mean = {minutes.mean():.0f} min")
    ax.set_title("Distribution of Movie Durations (minutes)", fontsize=16, fontweight="bold")
    ax.set_xlabel("Duration (minutes)")
    ax.set_ylabel("Number of Movies")
    ax.legend()
    _save(fig, save_path)
    return fig


# ---------------------------------------------------------------------------
# 8. Movie duration -- box plot
# ---------------------------------------------------------------------------
def plot_movie_duration_box(df, save_path: Optional[str] = None) -> plt.Figure:
    minutes = df.loc[df["content_type"] == "Movie", "duration_minutes"].dropna()
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.boxplot(x=minutes, color=NETFLIX_RED, ax=ax)
    ax.set_title("Movie Duration -- Boxplot", fontsize=16, fontweight="bold")
    ax.set_xlabel("Duration (minutes)")
    _save(fig, save_path)
    return fig


# ---------------------------------------------------------------------------
# 9. Heatmap of rating x content_type
# ---------------------------------------------------------------------------
def plot_rating_type_heatmap(df, save_path: Optional[str] = None) -> plt.Figure:
    from .analysis import rating_by_type
    ct = rating_by_type(df)
    fig, ax = plt.subplots(figsize=(9, 8))
    sns.heatmap(ct, annot=True, fmt="d", cmap="Reds", linewidths=0.5, ax=ax)
    ax.set_title("Rating vs Content Type (Heatmap)", fontsize=16, fontweight="bold")
    _save(fig, save_path)
    return fig


# ---------------------------------------------------------------------------
# 10. Stacked bar -- genre growth over time
# ---------------------------------------------------------------------------
def plot_genre_growth_stacked(df, top_n: int = 5, save_path: Optional[str] = None) -> plt.Figure:
    from .analysis import genre_growth
    data = genre_growth(df, top_n=top_n)
    fig, ax = plt.subplots(figsize=(12, 6))
    data.plot(kind="bar", stacked=True, ax=ax,
              color=sns.color_palette("Reds_r", n_colors=top_n))
    ax.set_title(f"Growth of Top {top_n} Genres Over the Years", fontsize=16, fontweight="bold")
    ax.set_xlabel("Year Added")
    ax.set_ylabel("Number of Titles")
    ax.legend(title="Genre", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.xticks(rotation=45)
    _save(fig, save_path)
    return fig


# ---------------------------------------------------------------------------
# 11. TV Shows by number of seasons -- bar
# ---------------------------------------------------------------------------
def plot_tv_seasons(df, save_path: Optional[str] = None) -> plt.Figure:
    from .analysis import tv_seasons_distribution
    data = tv_seasons_distribution(df).head(15)
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(data.index.astype(int).astype(str), data.values,
                  color=NETFLIX_RED, edgecolor=NETFLIX_DARK)
    for b in bars:
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 5,
                str(int(b.get_height())), ha="center", fontsize=10)
    ax.set_title("TV Shows by Number of Seasons", fontsize=16, fontweight="bold")
    ax.set_xlabel("Number of Seasons")
    ax.set_ylabel("Number of TV Shows")
    _save(fig, save_path)
    return fig


def render_all(df, out_dir: str = "images") -> None:
    """Render every chart to disk. Handy for building the README."""
    plot_content_type_pie(df, f"{out_dir}/movies_vs_tv.png")
    plot_top_countries(df, save_path=f"{out_dir}/top_countries.png")
    plot_top_genres(df, save_path=f"{out_dir}/top_genres.png")
    plot_rating_distribution(df, f"{out_dir}/rating_distribution.png")
    plot_yearly_trend(df, f"{out_dir}/yearly_trend.png")
    plot_monthly_trend(df, f"{out_dir}/monthly_trend.png")
    plot_movie_duration_hist(df, f"{out_dir}/movie_duration_hist.png")
    plot_movie_duration_box(df, f"{out_dir}/movie_duration_box.png")
    plot_rating_type_heatmap(df, f"{out_dir}/rating_type_heatmap.png")
    plot_genre_growth_stacked(df, save_path=f"{out_dir}/genre_growth.png")
    plot_tv_seasons(df, f"{out_dir}/tv_seasons.png")
    plt.close("all")
