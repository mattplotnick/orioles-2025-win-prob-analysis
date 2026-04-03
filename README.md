# How the Orioles Lost Too Many “Should-Have-Won” Games in 2025

This project analyzes the Baltimore Orioles’ 2025 season through the lens of game-state conversion: how often they failed to win games they were in strong position to win, and how often they came back from weak positions.

The analysis combines rule-based definitions of “should-have-won” games with play-by-play win probability data from the MLB Stats API.

## Project Goal

The main question behind this project is:

**How often did the Orioles lose games they should have won, and how did that compare to the rest of MLB?**

To answer that, this project measures:

- losses after reaching 80%, 85%, 90%, and 95% win probability
- losses after leading after 6 innings
- losses after holding a 3+ run lead
- losses after scoring 5+ runs
- comeback wins after falling to 20%, 15%, 10%, and 5% win probability
- comeback wins after trailing after 6 innings

## Main Findings

The Orioles were below average in several key “finish the game” metrics in 2025.

Some of the biggest takeaways:

- 15 losses after reaching 80% win probability (7th most in MLB)
- 3 losses after reaching 95% win probability (4th most in MLB)
- 22 rule-based “should-have-won” losses
- 5th-worst 95% win probability loss rate
- 7th-worst 80% win probability loss rate
- 7th-worst wasted-offense loss rate
- 29th in 20% win probability comeback rate

The broader conclusion is that the Orioles not only struggled to protect strong positions, but also ranked near the bottom of the league in turning weak positions into comeback wins.

## Repository Structure

```text
.
├── charts/
│   ├── chart_01_...
│   ├── chart_02_...
│   └── ...
├── scripts/
│   ├── efficient_win_conditions.py
│   └── league_visuals.py
├── orioles_2025_article.ipynb
├── orioles_2025_article.pdf
├── orioles_2025_article.html
└── README.md
```
Files

scripts/efficient_win_conditions.py

Main data pipeline script. This script:
	•	pulls 2025 regular season game data from the MLB Stats API
	•	parses linescore and win probability data
	•	builds team-level opportunity, collapse, and comeback metrics
	•	outputs summary CSVs used in the analysis

scripts/league_visuals.py

Visualization script. This script:
	•	recreates the charts/ output folder each run
	•	generates all league-wide and Orioles-specific charts
	•	creates summary visuals and dashboards used in the article

charts/

Contains all exported figures used in the notebook/article, including:
	•	Orioles vs league comparison charts
	•	full-team rankings
	•	opportunity vs failure scatter plots
	•	comeback analysis charts
	•	Orioles full dashboard summary

orioles_2025_article_draft.ipynb

Notebook/article version of the project with embedded charts, written analysis, and supplementary materials.

Data Source

All game data was collected using the MLB Stats API, including:
	•	schedules and final scores
	•	inning-by-inning linescore data
	•	play-by-play win probability data

Methodology Notes
	•	Only 2025 regular season games were included
	•	Terminal win probability values (0% and 100%) were excluded
	•	League averages for rates were calculated as the mean of team-level rates, not pooled totals
	•	Opportunity-adjusted metrics were used whenever possible to avoid misleading raw totals

Reproducibility

To reproduce the project:
	1.	Run efficient_win_conditions.py
	2.	Run league_visuals.py
	3.	Open the notebook/article and insert or refresh figures as needed

Why This Project Matters

This project is meant to go beyond a simple fan reaction to a disappointing season. It provides a data-driven explanation for one specific way the Orioles underperformed in 2025: they were worse than average at converting favorable game states into wins.

In a 162-game season, a small number of high-leverage failures can have a major impact on playoff odds. This project attempts to quantify that gap.

Author

Matthew Plotnick
