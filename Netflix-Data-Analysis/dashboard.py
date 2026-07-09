"""
Streamlit interactive dashboard for the Netflix Data Analysis project.

Run:
    streamlit run dashboard.py
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import plotly.express as px
import streamlit as st

from src import analysis, cleaning

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Netflix Catalogue Dashboard",
    page_icon="🎬",
    layout="wide",
)

NETFLIX_RED = "#E50914"
NETFLIX_DARK = "#221F1F"

# Global CSS — dark theme, red accents, high-contrast text
st.markdown(
    f"""
    <style>
      .stApp {{ background:{NETFLIX_DARK}; color:#FFFFFF; }}
      h1, h2, h3, h4, h5, h6, p, label, span, div {{ color:#FFFFFF !important; }}
      .kpi-card {{
        background:#2b2727; padding:22px; border-radius:12px;
        border-left:6px solid {NETFLIX_RED};
        box-shadow:0 4px 14px rgba(0,0,0,0.35);
      }}
      .kpi-label {{ font-size:14px; color:#bbbbbb !important; letter-spacing:1px; }}
      .kpi-value {{ font-size:34px; font-weight:800; color:#FFFFFF !important; }}
      [data-testid="stSidebar"] {{ background:#171414; }}
      
      /* Make multiselect have white background with black text */
      div[data-baseweb="select"] > div {{
        background-color: white !important;
      }}
      div[data-baseweb="select"] input {{
        color: black !important;
      }}
      ul[data-baseweb="menu"] {{
        background-color: white !important;
      }}
      ul[data-baseweb="menu"] li {{
        background-color: white !important;
        color: black !important;
      }}
      ul[data-baseweb="menu"] li:hover {{
        background-color: #f0f0f0 !important;
        color: black !important;
      }}
      ul[data-baseweb="menu"] li div {{
        color: black !important;
      }}
      div[data-baseweb="tag"] {{
        background-color: #E50914 !important;
      }}
      div[data-baseweb="tag"] span {{
        color: white !important;
      }}
      div[data-baseweb="tag"] svg {{
        fill: white !important;
      }}
      
      /* Make the label text black */
      .stMultiSelect label {{
        color: black !important;
      }}
      .stMultiSelect .stMarkdown {{
        color: black !important;
      }}
      
      /* Make placeholder text black */
      .stMultiSelect div[data-baseweb="select"] div[role="combobox"] div {{
        color: black !important;
      }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
@st.cache_data
def load_clean_data() -> pd.DataFrame:
    path = os.path.join(os.path.dirname(__file__), "data", "netflix_titles.csv")
    return cleaning.clean_pipeline(path)


df = load_clean_data()

# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------
st.sidebar.markdown(f"<h2 style='color:{NETFLIX_RED}'>Filters</h2>", unsafe_allow_html=True)

types = st.sidebar.multiselect(
    "Content type",
    options=sorted(df["content_type"].unique()),
    default=sorted(df["content_type"].unique()),
)

year_min, year_max = int(df["year_added"].min()), int(df["year_added"].max())
year_range = st.sidebar.slider("Year added", year_min, year_max, (year_min, year_max))

all_countries = sorted(
    {c for lst in df["countries_list"] for c in lst if c and c != "Unknown"}
)
countries = st.sidebar.multiselect("Countries (empty = all)", options=all_countries)

# Apply filters
filtered = df[
    df["content_type"].isin(types)
    & df["year_added"].between(year_range[0], year_range[1])
]
if countries:
    filtered = filtered[
        filtered["countries_list"].apply(lambda lst: any(c in lst for c in countries))
    ]

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown(
    f"<h1 style='color:{NETFLIX_RED} !important; margin-bottom:0;"
    "letter-spacing:6px; font-weight:900'>NETFLIX</h1>"
    "<h3 style='margin-top:0; color:#eeeeee !important'>"
    "Catalogue Analytics Dashboard</h3>",
    unsafe_allow_html=True,
)
st.caption(f"Showing {len(filtered):,} of {len(df):,} titles based on current filters.")

# ---------------------------------------------------------------------------
# KPIs
# ---------------------------------------------------------------------------
kpis = analysis.compute_kpis(filtered) if len(filtered) else analysis.compute_kpis(df)

kpi_specs = [
    ("Total Titles", f"{kpis['total_titles']:,}"),
    ("Movies", f"{kpis['movies']:,}"),
    ("TV Shows", f"{kpis['tv_shows']:,}"),
    ("Countries", f"{kpis['countries']}"),
    ("Genres", f"{kpis['genres']}"),
    ("Top Rating", f"{kpis['most_common_rating']}"),
    ("Top Country", f"{kpis['top_country']}"),
]

cols = st.columns(len(kpi_specs))
for col, (label, value) in zip(cols, kpi_specs):
    col.markdown(
        f"<div class='kpi-card'>"
        f"<div class='kpi-label'>{label.upper()}</div>"
        f"<div class='kpi-value'>{value}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

st.markdown("---")

# ---------------------------------------------------------------------------
# Row 1 — Movies vs TV + Top countries
# ---------------------------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    st.subheader("Movies vs TV Shows")
    counts = filtered["content_type"].value_counts().reset_index()
    counts.columns = ["content_type", "count"]
    fig = px.pie(
        counts, values="count", names="content_type", hole=0.5,
        color_discrete_sequence=[NETFLIX_RED, "#831010"],
    )
    fig.update_layout(paper_bgcolor=NETFLIX_DARK, font_color="white", legend_font_color="white")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Top 10 Countries")
    tc = analysis.top_countries(filtered, 10).reset_index()
    tc.columns = ["country", "titles"]
    fig = px.bar(
        tc.sort_values("titles"), x="titles", y="country", orientation="h",
        color="titles", color_continuous_scale="Reds",
    )
    fig.update_layout(paper_bgcolor=NETFLIX_DARK, plot_bgcolor=NETFLIX_DARK,
                      font_color="white", xaxis_gridcolor="#444",
                      coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------------
# Row 2 — Top genres + Ratings
# ---------------------------------------------------------------------------
c3, c4 = st.columns(2)

with c3:
    st.subheader("Top 10 Genres")
    tg = analysis.top_genres(filtered, 10).reset_index()
    tg.columns = ["genre", "titles"]
    fig = px.bar(
        tg.sort_values("titles"), x="titles", y="genre", orientation="h",
        color="titles", color_continuous_scale="Reds",
    )
    fig.update_layout(paper_bgcolor=NETFLIX_DARK, plot_bgcolor=NETFLIX_DARK,
                      font_color="white", xaxis_gridcolor="#444",
                      coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

with c4:
    st.subheader("Rating Distribution")
    rd = analysis.rating_distribution(filtered).reset_index()
    rd.columns = ["rating", "count"]
    fig = px.bar(rd, x="rating", y="count", color="count",
                 color_continuous_scale="Reds")
    fig.update_layout(paper_bgcolor=NETFLIX_DARK, plot_bgcolor=NETFLIX_DARK,
                      font_color="white", yaxis_gridcolor="#444",
                      coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------------
# Row 3 — Yearly trend + Movie duration
# ---------------------------------------------------------------------------
c5, c6 = st.columns(2)

with c5:
    st.subheader("Titles Added Over Time")
    yr = analysis.yearly_additions(filtered).reset_index()
    yr.columns = ["year", "titles"]
    fig = px.area(yr, x="year", y="titles",
                  color_discrete_sequence=[NETFLIX_RED])
    fig.update_layout(paper_bgcolor=NETFLIX_DARK, plot_bgcolor=NETFLIX_DARK,
                      font_color="white",
                      xaxis_gridcolor="#444", yaxis_gridcolor="#444")
    st.plotly_chart(fig, use_container_width=True)

with c6:
    st.subheader("Movie Duration (minutes)")
    minutes = filtered.loc[
        filtered["content_type"] == "Movie", "duration_minutes"
    ].dropna()
    if len(minutes):
        fig = px.histogram(minutes, nbins=40,
                           color_discrete_sequence=[NETFLIX_RED])
        fig.update_layout(paper_bgcolor=NETFLIX_DARK, plot_bgcolor=NETFLIX_DARK,
                          font_color="white", showlegend=False,
                          xaxis_gridcolor="#444", yaxis_gridcolor="#444",
                          xaxis_title="Minutes", yaxis_title="Number of Movies")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No movies match the current filters.")

# ---------------------------------------------------------------------------
# Raw data preview
# ---------------------------------------------------------------------------
with st.expander("Preview filtered data (first 100 rows)"):
    st.dataframe(
        filtered.drop(columns=["genres_list", "countries_list", "cast_list"]).head(100),
        use_container_width=True,
    )

st.markdown(
    "<hr><p style='text-align:center;color:#888'>"
    "Built with Python, Pandas, Plotly and Streamlit — "
    "<b>Neethu Reddy Singireddy</b><br>"
    "<a href='https://github.com/neethu18reddy' style='color:#E50914'>GitHub</a> · "
    "<a href='https://www.linkedin.com/in/neethu-reddy-singireddy-425802369/' style='color:#E50914'>LinkedIn</a> · "
    "<a href='mailto:sneethureddy18@gmail.com' style='color:#E50914'>Email</a>"
    "</p>",
    unsafe_allow_html=True,
)
