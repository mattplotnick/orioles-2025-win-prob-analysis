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
