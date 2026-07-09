# Interview Questions — Netflix Data Analysis Project

Below are 25 realistic questions an interviewer might ask about this project, grouped
by topic, with short model answers.

---

## A. Project & Business Context

**1. Walk me through this project in 60 seconds.**  
> I took Netflix's public catalogue of 8,807 titles, cleaned it end-to-end in pandas,
> answered 15 business questions such as "which genres are growing?" and "which
> countries dominate?", and packaged the findings into an executed Jupyter notebook and
> an interactive Streamlit dashboard. Headline insights include a stable 70/30 movie-vs-TV
> mix, US/India/UK producing >50% of titles, and 2019 being the peak year for content
> additions.

**2. What business decisions could this analysis support?**  
> Content acquisition (where are the gaps?), marketing calendars (February trough),
> localisation strategy (which growth countries?), and product / kids-content strategy.

**3. Why did you choose this dataset?**  
> It's realistic (mixed types, multi-value columns, dates, missing data), globally
> recognisable, and rich enough to demonstrate the full analytics workflow.

## B. Data Cleaning

**4. What were the biggest data-quality issues?**  
> Missing directors (~30%), missing cast (~9%), missing country (~9%), `date_added` stored
> as text, and `duration` mixing minutes and seasons in one column.

**5. Why did you fill missing directors with "Unknown" instead of dropping them?**  
> Dropping would remove ~30% of the dataset. `Unknown` preserves the row for
> country/genre/rating analysis where director is not needed.

**6. Why is `trim + standardise text` important?**  
> Raw CSV values often contain trailing whitespace or inconsistent casing
> ("United States" vs " united states"). If uncleaned, group-bys create phantom
> categories.

**7. How did you handle the multi-value `country`, `cast`, and `listed_in` columns?**  
> Split on comma into Python lists, kept both the raw and the list version, and
> used `.explode()` to run per-value counts.

**8. Explain your pipeline structure.**  
> Small pure functions (`load_data`, `handle_missing_values`, `parse_dates`, …) composed
> into a single `clean_pipeline(path)` orchestrator. This is easy to unit-test and reuse
> in the Streamlit app.

## C. EDA & Insight

**9. What is the movie-vs-TV split and why is it interesting?**  
> ~70% movies, ~30% TV. Interesting because Netflix's brand is associated with
> "series" but the catalogue is still film-heavy — signals investment strategy.

**10. Which country dominates? Any risk in that?**  
> The US produces ~2.8× the runner-up. Over-reliance on one market is a supply-side
> risk if licensing terms change; India (rank 2) is the diversification bet.

**11. Which rating is most common and what does that mean strategically?**  
> TV-MA. Netflix is adult-skewing — a gap versus Disney+ in the kids/family segment.

**12. What was the peak content year and why did growth slow after?**  
> 2019. Post-2019 the pandemic disrupted production; simultaneously Netflix pivoted to
> fewer, higher-budget originals.

**13. Which genres are growing fastest?**  
> International Movies and Dramas — Netflix's globalisation bet.

**14. What monthly seasonality did you find?**  
> Peaks in July, December and January (holiday windows); a clear February trough.

**15. What is the typical movie runtime?**  
> ~99-minute mean, 98-minute median, IQR 87–115 min. Classic feature length.

**16. Anything surprising about TV shows?**  
> The vast majority have only 1 season. Long-running hits are rare and disproportionately
> valuable.

## D. Technical / Python

**17. What is the difference between `dropna` and `fillna`?**  
> `dropna` removes rows/columns containing missing values; `fillna` replaces them with a
> chosen value (constant, mode, mean, forward-fill, etc.).

**18. What does `df.explode('col')` do?**  
> Turns a single row with a list value into multiple rows, one per list element —
> essential for per-genre or per-country analysis.

**19. Why convert `date_added` to datetime?**  
> To use `.dt.year`, `.dt.month`, sort chronologically, and run time-series aggregations.

**20. What is the difference between `value_counts` and `groupby().size()`?**  
> `value_counts` works on a Series and always sorts descending. `groupby().size()` works
> on a DataFrame and preserves the group order; more flexible for multi-key grouping.

**21. Why did you use `pd.crosstab` for the rating × type heatmap?**  
> It produces a compact frequency table with two categorical axes — exactly the shape
> `sns.heatmap` expects.

## E. Visualisation

**22. Why so many chart types?**  
> Different questions demand different encodings — categorical counts want bars, part-
> of-whole wants pies, time series want lines, distributions want histograms/boxes,
> two-way frequency wants heatmaps.

**23. How did you make the charts feel professional?**  
> Consistent Netflix-red palette, clear titles + axis labels, data labels on bars,
> larger figure sizes, and Seaborn `whitegrid` theme.

## F. Extension & Reflection

**24. If you had more time, what would you add?**  
> Merge with IMDb / TMDb to weight by quality; NLP topic modelling on descriptions;
> a time-series forecast of monthly additions; deploy Streamlit dashboard publicly.

**25. Biggest limitation of the dataset?**  
> It's a snapshot from 2021 with no engagement metrics — we can count titles but not
> hours watched, so all "popularity" claims are catalogue-side only.
