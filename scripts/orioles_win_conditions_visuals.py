import os
import shutil
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

OUTPUT_DIR = "outputs_league"
TEAM_SUMMARY_FILE = "mlb_2025_should_have_won_team_summary.csv"
ORIOLES_NAME = "Baltimore Orioles"

# Color palette
ORIOLES_ORANGE = "#FF9900"
ORIOLES_BLACK = "#000000"
LIGHT_GRAY = "#D9D9D9"
MID_GRAY = "#A6A6A6"
DARK_GRAY = "#4D4D4D"
SOFT_BLUE = "#88A9C3"
SOFT_GREEN = "#8FBF8F"
SOFT_RED = "#D98C8C"
WHITE = "#FFFFFF"


def reset_output_dir():
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)


def setup_style():
    plt.style.use("default")
    plt.rcParams["figure.figsize"] = (10, 6)
    plt.rcParams["axes.titlesize"] = 18
    plt.rcParams["axes.titleweight"] = "bold"
    plt.rcParams["axes.labelsize"] = 12
    plt.rcParams["xtick.labelsize"] = 10.5
    plt.rcParams["ytick.labelsize"] = 10.5
    plt.rcParams["legend.fontsize"] = 10
    plt.rcParams["figure.dpi"] = 120
    plt.rcParams["axes.spines.top"] = False
    plt.rcParams["axes.spines.right"] = False
    plt.rcParams["axes.edgecolor"] = "#333333"
    plt.rcParams["axes.linewidth"] = 1.0
    plt.rcParams["grid.color"] = "#E6E6E6"
    plt.rcParams["grid.linestyle"] = "-"
    plt.rcParams["grid.linewidth"] = 0.8
    plt.rcParams["font.family"] = "DejaVu Sans"


def save_clean_chart(filename):
    plt.tight_layout()
    plt.savefig(
        os.path.join(OUTPUT_DIR, filename),
        dpi=300,
        bbox_inches="tight",
        facecolor="white"
    )
    plt.close()

def add_headroom(ax, values, pct=0.15):
    max_val = max(values)
    ax.set_ylim(0, max_val * (1 + pct))

def add_bar_labels(ax, decimals=0, padding=None, fontsize=10, suffix=""):
    y_min, y_max = ax.get_ylim()
    axis_range = y_max - y_min

    if padding is None:
        padding = axis_range * 0.015

    for container in ax.containers:
        for bar in container:
            height = bar.get_height()
            if pd.isna(height):
                continue
            label = f"{height:.{decimals}f}{suffix}" if decimals > 0 else f"{int(round(height))}{suffix}"
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height + padding,
                label,
                ha="center",
                va="bottom",
                fontsize=fontsize,
                color=ORIOLES_BLACK
            )

def add_barh_labels(ax, decimals=0, offset=0.15, fontsize=10, suffix=""):
    for container in ax.containers:
        for bar in container:
            width = bar.get_width()
            if pd.isna(width):
                continue
            label = f"{width:.{decimals}f}{suffix}" if decimals > 0 else f"{int(round(width))}{suffix}"
            ax.text(
                width + offset,
                bar.get_y() + bar.get_height() / 2,
                label,
                va="center",
                fontsize=fontsize,
                color=ORIOLES_BLACK
            )


def style_bar_colors(ax, labels, orioles_name=ORIOLES_NAME):
    for bar, label in zip(ax.patches, labels):
        if label == orioles_name:
            bar.set_color(ORIOLES_ORANGE)
            bar.set_edgecolor(ORIOLES_BLACK)
            bar.set_alpha(1.0)
            bar.set_linewidth(1.8)
        else:
            bar.set_color(LIGHT_GRAY)
            bar.set_edgecolor(MID_GRAY)
            bar.set_alpha(0.95)
            bar.set_linewidth(0.8)


def style_comparison_bars(ax):
    colors = [ORIOLES_ORANGE, SOFT_BLUE, LIGHT_GRAY]
    edges = [ORIOLES_BLACK, DARK_GRAY, MID_GRAY]
    for i, bar in enumerate(ax.patches):
        bar.set_color(colors[i])
        bar.set_edgecolor(edges[i])
        bar.set_linewidth(1.4 if i == 0 else 1.0)


def add_reference_lines(ax, values, orioles_value, decimals=3):
    mean_val = values.mean()
    median_val = values.median()
    ax.axvline(
        mean_val,
        linestyle="--",
        linewidth=2,
        color=SOFT_BLUE,
        label=f"League mean: {mean_val:.{decimals}f}"
    )
    ax.axvline(
        median_val,
        linestyle=":",
        linewidth=2,
        color=DARK_GRAY,
        label=f"League median: {median_val:.{decimals}f}"
    )
    ax.axvline(
        orioles_value,
        linewidth=2.5,
        color=ORIOLES_ORANGE,
        label=f"Orioles: {orioles_value:.{decimals}f}"
    )


def comparison_bar_chart(orioles_value, league_mean, league_median, title, ylabel, filename, decimals=0):
    labels = ["Orioles", "League Mean", "League Median"]
    values = [orioles_value, league_mean, league_median]

    fig, ax = plt.subplots(figsize=(8, 6))
    fig.subplots_adjust(top=0.88)
    ax.bar(labels, values)
    style_comparison_bars(ax)

    add_headroom(ax, values)

    ax.set_title(title, pad=15)
    ax.set_ylabel(ylabel)
    ax.yaxis.set_major_locator(MaxNLocator(integer=(decimals == 0)))
    ax.grid(axis="y", alpha=0.25)
    add_bar_labels(ax, decimals=decimals)
    save_clean_chart(filename)


def distribution_dot_plot(df, metric, title, xlabel, filename, decimals=3):
    plot_df = df[["team", metric]].dropna().sort_values(metric).reset_index(drop=True)
    orioles_row = plot_df[plot_df["team"] == ORIOLES_NAME].copy()

    fig, ax = plt.subplots(figsize=(10, 6))

    other = plot_df[plot_df["team"] != ORIOLES_NAME]
    ax.scatter(
        other[metric],
        np.arange(len(other)),
        color=LIGHT_GRAY,
        s=55,
        edgecolor=MID_GRAY,
        linewidth=0.6
    )

    ax.scatter(
        orioles_row[metric],
        orioles_row.index,
        color=ORIOLES_ORANGE,
        s=130,
        edgecolor=ORIOLES_BLACK,
        linewidth=1.3,
        zorder=3
    )

    if not orioles_row.empty:
        x_val = orioles_row[metric].iloc[0]
        y_val = orioles_row.index[0]
        ax.annotate(
            "Orioles",
            (x_val, y_val),
            xytext=(8, 0),
            textcoords="offset points",
            va="center",
            fontsize=10,
            color=ORIOLES_BLACK,
            fontweight="bold"
        )

    add_reference_lines(
        ax,
        plot_df[metric],
        plot_df.loc[plot_df["team"] == ORIOLES_NAME, metric].iloc[0],
        decimals=decimals
    )

    ax.set_title(title, pad=15)
    ax.set_xlabel(xlabel)
    ax.set_yticks([])
    ax.grid(axis="x", alpha=0.25)
    ax.legend(frameon=False)
    save_clean_chart(filename)


def top_n_chart(df, metric, title, xlabel, filename, top_n=10, decimals=0):
    chart_df = df.sort_values(metric, ascending=False).head(top_n).copy()
    chart_df = chart_df.sort_values(metric, ascending=True)

    fig, ax = plt.subplots(figsize=(11, 7))
    ax.barh(chart_df["team"], chart_df[metric])
    ax.set_title(title, pad=15)
    ax.set_xlabel(xlabel)
    ax.grid(axis="x", alpha=0.25)
    style_bar_colors(ax, chart_df["team"].tolist())
    add_barh_labels(ax, decimals=decimals, offset=0.02 if decimals else 0.15)
    save_clean_chart(filename)


def full_rank_chart(df, metric, title, xlabel, filename, decimals=0):
    chart_df = df.sort_values(metric, ascending=False).copy()

    fig, ax = plt.subplots(figsize=(12, 10))
    ax.barh(chart_df["team"], chart_df[metric])
    ax.set_title(title, pad=15)
    ax.set_xlabel(xlabel)
    ax.invert_yaxis()
    ax.grid(axis="x", alpha=0.25)
    style_bar_colors(ax, chart_df["team"].tolist())
    add_barh_labels(ax, decimals=decimals, offset=0.02 if decimals else 0.15)
    save_clean_chart(filename)


def scatter_chart(df, x_metric, y_metric, title, xlabel, ylabel, filename):
    fig, ax = plt.subplots(figsize=(10, 7))

    other = df[df["team"] != ORIOLES_NAME]
    orioles = df[df["team"] == ORIOLES_NAME]

    ax.scatter(
        other[x_metric],
        other[y_metric],
        s=60,
        alpha=0.8,
        color=LIGHT_GRAY,
        edgecolor=MID_GRAY,
        linewidth=0.6,
        label="Other teams"
    )

    ax.scatter(
        orioles[x_metric],
        orioles[y_metric],
        s=140,
        color=ORIOLES_ORANGE,
        edgecolor=ORIOLES_BLACK,
        linewidth=1.2,
        label="Orioles",
        zorder=3
    )

    for _, row in orioles.iterrows():
        ax.annotate(
            row["team"],
            (row[x_metric], row[y_metric]),
            xytext=(8, 8),
            textcoords="offset points",
            fontsize=10,
            color=ORIOLES_BLACK,
            fontweight="bold"
        )

    ax.set_title(title, pad=15)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(alpha=0.25)
    ax.legend(frameon=False)
    save_clean_chart(filename)


def side_by_side_metric_chart(df, metric_a, metric_b, title, xlabel, filename, top_n=10):
    chart_df = df[["team", metric_a, metric_b]].copy()
    chart_df = chart_df.sort_values(metric_a, ascending=False).head(top_n)
    chart_df = chart_df.sort_values(metric_a, ascending=True)

    y = np.arange(len(chart_df))
    h = 0.38

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.barh(
        y - h / 2,
        chart_df[metric_a],
        height=h,
        color=SOFT_BLUE,
        edgecolor=DARK_GRAY,
        label=metric_a
    )
    ax.barh(
        y + h / 2,
        chart_df[metric_b],
        height=h,
        color=SOFT_RED,
        edgecolor=DARK_GRAY,
        label=metric_b
    )
    ax.set_yticks(y)
    ax.set_yticklabels(chart_df["team"])
    ax.set_title(title, pad=15)
    ax.set_xlabel(xlabel)
    ax.grid(axis="x", alpha=0.25)
    ax.legend(frameon=False)
    save_clean_chart(filename)


def make_orioles_summary_table_image(df):
    orioles = df[df["team"] == ORIOLES_NAME].copy().iloc[0]

    metrics = [
        ("wp_95_loss_rate", "95% WP failure rate", "worst", True),
        ("wp_80_loss_rate", "80% WP failure rate", "worst", True),
        ("big_lead_loss_rate", "Big-lead failure rate", "worst", True),
        ("wasted_offense_loss_rate", "Wasted-offense failure rate", "worst", True),

        ("wp_95_losses", "95% WP losses", "worst", False),
        ("wp_90_losses", "90% WP losses", "worst", False),
        ("rule_based_losses", "Rule-based losses", "worst", False),

        ("games_reached_95_wp", "95% WP opportunities", "most", False),
        ("games_reached_90_wp", "90% WP opportunities", "most", False),
        ("games_led_after_6", "Led after 6 opportunities", "most", False),
        ("games_scored_5_plus", "5+ run opportunities", "most", False),

        ("wp_20_comeback_wins", "20% comeback wins", "most", False),
        ("wp_15_comeback_wins", "15% comeback wins", "most", False),
        ("wp_10_comeback_wins", "10% comeback wins", "most", False),
        ("wp_5_comeback_wins", "5% comeback wins", "most", False),

        ("wp_20_comeback_rate", "20% comeback rate", "most", True),
        ("wp_15_comeback_rate", "15% comeback rate", "most", True),
        ("wp_10_comeback_rate", "10% comeback rate", "most", True),
        ("wp_5_comeback_rate", "5% comeback rate", "most", True),

        ("trailed_after_6_wins", "Wins when trailing after 6", "most", False),
        ("trailed_after_6_win_rate", "Trailing-after-6 win rate", "most", True),

        ("games_fell_to_20_wp", "20% comeback opportunities", "most", False),
        ("games_fell_to_15_wp", "15% comeback opportunities", "most", False),
        ("games_fell_to_10_wp", "10% comeback opportunities", "most", False),
        ("games_fell_to_5_wp", "5% comeback opportunities", "most", False),
        ("games_trailed_after_6", "Games trailing after 6", "most", False),
    ]

    rows = []
    for metric, label, direction, is_rate in metrics:
        rank = orioles.get(f"{metric}_rank", None)
        if pd.isna(rank):
            rank_text = "N/A"
        else:
            rank = int(rank)
            rank_text = f"{rank}th worst" if direction == "worst" else f"{rank}th most"

        orioles_value = f"{orioles[metric]:.3f}" if is_rate else f"{orioles[metric]:.1f}"
        mean_value = f"{df[metric].mean():.3f}" if is_rate else f"{df[metric].mean():.1f}"
        median_value = f"{df[metric].median():.3f}" if is_rate else f"{df[metric].median():.1f}"

        rows.append([label, orioles_value, mean_value, median_value, rank_text])

    table_df = pd.DataFrame(
        rows,
        columns=["Metric", "Orioles", "League Mean", "League Median", "Rank"]
    )

    fig, ax = plt.subplots(figsize=(14, 9))
    ax.axis("off")
    ax.set_title(
        "Baltimore Orioles 2025: League Comparison Summary",
        pad=20,
        fontsize=18,
        fontweight="bold",
        color=ORIOLES_BLACK
    )

    table = ax.table(
        cellText=table_df.values,
        colLabels=table_df.columns,
        cellLoc="center",
        loc="center"
    )

    table.auto_set_font_size(False)
    table.set_fontsize(9.5)
    table.scale(1, 1.45)

    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_facecolor(ORIOLES_ORANGE)
            cell.set_text_props(weight="bold", color=WHITE)
        else:
            cell.set_facecolor("#FFF7F2" if row % 2 == 1 else WHITE)
            cell.set_edgecolor(LIGHT_GRAY)

    save_clean_chart("chart_24_orioles_summary_table.png")


def make_orioles_rank_chart(df):
    orioles = df[df["team"] == ORIOLES_NAME].copy().iloc[0]

    metrics = [
        ("wp_95_loss_rate_rank", "95% WP failure rate"),
        ("wp_80_loss_rate_rank", "80% WP failure rate"),
        ("big_lead_loss_rate_rank", "Big-lead failure rate"),
        ("wasted_offense_loss_rate_rank", "Wasted-offense failure rate"),
        ("wp_95_losses_rank", "95% WP losses"),
        ("rule_based_losses_rank", "Rule-based losses"),
        ("games_reached_95_wp_rank", "95% WP opportunities"),
        ("games_reached_90_wp_rank", "90% WP opportunities"),

        ("wp_20_comeback_wins_rank", "20% comeback wins"),
        ("wp_15_comeback_wins_rank", "15% comeback wins"),
        ("wp_10_comeback_wins_rank", "10% comeback wins"),
        ("wp_5_comeback_wins_rank", "5% comeback wins"),

        ("wp_20_comeback_rate_rank", "20% comeback rate"),
        ("wp_15_comeback_rate_rank", "15% comeback rate"),
        ("wp_10_comeback_rate_rank", "10% comeback rate"),
        ("wp_5_comeback_rate_rank", "5% comeback rate"),

        ("trailed_after_6_wins_rank", "Wins trailing after 6"),
        ("trailed_after_6_win_rate_rank", "Trailing-after-6 win rate"),

        ("games_fell_to_20_wp_rank", "20% comeback opportunities"),
        ("games_fell_to_15_wp_rank", "15% comeback opportunities"),
        ("games_fell_to_10_wp_rank", "10% comeback opportunities"),
        ("games_fell_to_5_wp_rank", "5% comeback opportunities"),
        ("games_trailed_after_6_rank", "Games trailing after 6"),
    ]

    rows = []
    for metric, label in metrics:
        val = orioles.get(metric, None)
        if pd.notna(val):
            rows.append((label, int(val)))

    rank_df = pd.DataFrame(rows, columns=["Metric", "Rank"]).sort_values("Rank", ascending=True)

    fig, ax = plt.subplots(figsize=(11, 8))
    ax.barh(
        rank_df["Metric"],
        rank_df["Rank"],
        color=ORIOLES_ORANGE,
        edgecolor=ORIOLES_BLACK,
        alpha=0.9
    )
    ax.set_title("Orioles 2025 MLB Rank Across Key Metrics", pad=15)
    ax.set_xlabel("Rank (1 = highest / worst for collapse metrics, 30 = lowest)")
    ax.invert_yaxis()
    ax.grid(axis="x", alpha=0.25)

    for i, v in enumerate(rank_df["Rank"]):
        ax.text(v + 0.2, i, str(v), va="center", fontsize=10, color=ORIOLES_BLACK)

    ax.set_xlim(0, 31)
    save_clean_chart("chart_25_orioles_rank_profile.png")


def make_full_orioles_dashboard(df):
    orioles = df[df["team"] == ORIOLES_NAME].iloc[0]

    metrics = [
        "rule_based_losses",
        "wp_80_losses",
        "wp_85_losses",
        "wp_90_losses",
        "wp_95_losses",
        "games_reached_80_wp",
        "games_reached_85_wp",
        "games_reached_90_wp",
        "games_reached_95_wp",
        "games_led_after_6",
        "games_biggest_lead_3_plus",
        "games_scored_5_plus",
        "rule_based_per_loss",
        "wp_80_per_loss",
        "wp_85_per_loss",
        "wp_90_per_loss",
        "wp_95_per_loss",
        "late_lead_loss_rate",
        "big_lead_loss_rate",
        "wasted_offense_loss_rate",
        "wp_80_loss_rate",
        "wp_85_loss_rate",
        "wp_90_loss_rate",
        "wp_95_loss_rate",
        "games_fell_to_20_wp",
        "games_fell_to_15_wp",
        "games_fell_to_10_wp",
        "games_fell_to_5_wp",
        "wp_20_comeback_wins",
        "wp_15_comeback_wins",
        "wp_10_comeback_wins",
        "wp_5_comeback_wins",
        "wp_20_comeback_rate",
        "wp_15_comeback_rate",
        "wp_10_comeback_rate",
        "wp_5_comeback_rate",
        "games_trailed_after_6",
        "trailed_after_6_wins",
        "trailed_after_6_win_rate"
    ]

    rows = []
    for m in metrics:
        val = orioles[m]
        mean = df[m].mean()
        median = df[m].median()
        rank = orioles.get(f"{m}_rank", None)

        if "rate" in m or "per_loss" in m:
            val_fmt = f"{val:.3f}"
            mean_fmt = f"{mean:.3f}"
            median_fmt = f"{median:.3f}"
        else:
            val_fmt = f"{val:.1f}"
            mean_fmt = f"{mean:.1f}"
            median_fmt = f"{median:.1f}"

        rows.append([
            m,
            val_fmt,
            mean_fmt,
            median_fmt,
            int(rank) if pd.notna(rank) else "N/A"
        ])

    table_df = pd.DataFrame(
        rows,
        columns=["Metric", "Orioles", "League Mean", "League Median", "Rank"]
    )

    fig, ax = plt.subplots(figsize=(16, 14))
    ax.axis("off")
    ax.set_title(
        "Baltimore Orioles 2025: Full League Comparison Dashboard",
        fontsize=20,
        fontweight="bold",
        pad=20,
        color=ORIOLES_BLACK
    )

    table = ax.table(
        cellText=table_df.values,
        colLabels=table_df.columns,
        cellLoc="center",
        loc="center"
    )

    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.5)

    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_facecolor(ORIOLES_ORANGE)
            cell.set_text_props(weight="bold", color=WHITE)
        else:
            cell.set_facecolor("#FFF7F2" if row % 2 == 1 else WHITE)
            cell.set_edgecolor(LIGHT_GRAY)

    save_clean_chart("chart_99_orioles_full_dashboard.png")


def make_summary_table_csv(df):
    orioles = df[df["team"] == ORIOLES_NAME].iloc[0]

    metrics = [
        "rule_based_losses",
        "wp_80_losses",
        "wp_90_losses",
        "wp_95_losses",
        "games_reached_90_wp",
        "games_reached_95_wp",
        "wp_80_loss_rate",
        "wp_90_loss_rate",
        "wp_95_loss_rate",
        "big_lead_loss_rate",
        "wasted_offense_loss_rate",
        "wp_20_comeback_wins",
        "wp_10_comeback_wins",
        "wp_5_comeback_wins",
        "wp_20_comeback_rate",
        "wp_10_comeback_rate",
        "wp_5_comeback_rate",
        "trailed_after_6_win_rate",
    ]

    rows = []
    for metric in metrics:
        rows.append({
            "metric": metric,
            "orioles_value": orioles[metric],
            "league_mean": df[metric].mean(),
            "league_median": df[metric].median(),
            "orioles_rank": orioles.get(f"{metric}_rank", None),
        })

    pd.DataFrame(rows).to_csv(
        os.path.join(OUTPUT_DIR, "orioles_league_visual_summary.csv"),
        index=False
    )


def main():
    reset_output_dir()
    setup_style()

    df = pd.read_csv(TEAM_SUMMARY_FILE)

    orioles = df[df["team"] == ORIOLES_NAME].copy()
    if orioles.empty:
        raise ValueError("Baltimore Orioles row not found in team summary file.")
    orioles = orioles.iloc[0]

    # Collapse visuals
    comparison_bar_chart(
        orioles["wp_95_loss_rate"], df["wp_95_loss_rate"].mean(), df["wp_95_loss_rate"].median(),
        "Orioles vs League: 95% Win Probability Failure Rate", "Failure rate",
        "chart_01_orioles_vs_league_wp95_rate.png", decimals=3
    )

    comparison_bar_chart(
        orioles["wp_80_loss_rate"], df["wp_80_loss_rate"].mean(), df["wp_80_loss_rate"].median(),
        "Orioles vs League: 80% Win Probability Failure Rate", "Failure rate",
        "chart_02_orioles_vs_league_wp80_rate.png", decimals=3
    )

    comparison_bar_chart(
        orioles["big_lead_loss_rate"], df["big_lead_loss_rate"].mean(), df["big_lead_loss_rate"].median(),
        "Orioles vs League: Big-Lead Failure Rate", "Failure rate",
        "chart_03_orioles_vs_league_big_lead_rate.png", decimals=3
    )

    comparison_bar_chart(
        orioles["wasted_offense_loss_rate"], df["wasted_offense_loss_rate"].mean(), df["wasted_offense_loss_rate"].median(),
        "Orioles vs League: Wasted-Offense Failure Rate", "Failure rate",
        "chart_04_orioles_vs_league_wasted_offense_rate.png", decimals=3
    )

    comparison_bar_chart(
        orioles["wp_95_losses"], df["wp_95_losses"].mean(), df["wp_95_losses"].median(),
        "Orioles vs League: 95% Win Probability Losses", "Number of losses",
        "chart_05_orioles_vs_league_wp95_losses.png", decimals=1
    )

    comparison_bar_chart(
        orioles["wp_80_losses"], df["wp_80_losses"].mean(), df["wp_80_losses"].median(),
        "Orioles vs League: 80% Win Probability Losses", "Number of losses",
        "chart_06_orioles_vs_league_wp80_losses.png", decimals=1
    )

    comparison_bar_chart(
        orioles["games_reached_95_wp"], df["games_reached_95_wp"].mean(), df["games_reached_95_wp"].median(),
        "Orioles vs League: 95% Win Probability Opportunities", "Number of games",
        "chart_07_orioles_vs_league_wp95_opportunities.png", decimals=1
    )

    distribution_dot_plot(
        df, "wp_95_loss_rate",
        "Distribution of 95% Win Probability Failure Rate",
        "95% WP failure rate",
        "chart_08_dist_wp95_loss_rate.png",
        decimals=3
    )

    distribution_dot_plot(
        df, "wp_80_loss_rate",
        "Distribution of 80% Win Probability Failure Rate",
        "80% WP failure rate",
        "chart_09_dist_wp80_loss_rate.png",
        decimals=3
    )

    distribution_dot_plot(
        df, "wasted_offense_loss_rate",
        "Distribution of Wasted-Offense Failure Rate",
        "Loss rate in 5+ run games",
        "chart_10_dist_wasted_offense_rate.png",
        decimals=3
    )

    top_n_chart(
        df, "wp_95_loss_rate",
        "Top 10 Teams by 95% Win Probability Failure Rate",
        "Failure rate",
        "chart_11_top10_wp95_loss_rate.png",
        top_n=10, decimals=3
    )

    top_n_chart(
        df, "wp_80_loss_rate",
        "Top 10 Teams by 80% Win Probability Failure Rate",
        "Failure rate",
        "chart_12_top10_wp80_loss_rate.png",
        top_n=10, decimals=3
    )

    top_n_chart(
        df, "wasted_offense_loss_rate",
        "Top 10 Teams by Wasted-Offense Failure Rate",
        "Failure rate",
        "chart_13_top10_wasted_offense_rate.png",
        top_n=10, decimals=3
    )

    top_n_chart(
        df, "big_lead_loss_rate",
        "Top 10 Teams by Big-Lead Failure Rate",
        "Failure rate",
        "chart_14_top10_big_lead_rate.png",
        top_n=10, decimals=3
    )

    full_rank_chart(
        df, "wp_95_loss_rate",
        "All MLB Teams Ranked by 95% Win Probability Failure Rate",
        "Failure rate",
        "chart_15_ranked_wp95_loss_rate.png", decimals=3
    )

    full_rank_chart(
        df, "wp_80_loss_rate",
        "All MLB Teams Ranked by 80% Win Probability Failure Rate",
        "Failure rate",
        "chart_16_ranked_wp80_loss_rate.png", decimals=3
    )

    scatter_chart(
        df, "games_reached_95_wp", "wp_95_loss_rate",
        "95% Win Probability Opportunities vs Failure Rate",
        "Games reaching 95% WP",
        "95% WP failure rate",
        "chart_17_scatter_wp95_opportunity_vs_failure.png"
    )

    scatter_chart(
        df, "games_reached_80_wp", "wp_80_loss_rate",
        "80% Win Probability Opportunities vs Failure Rate",
        "Games reaching 80% WP",
        "80% WP failure rate",
        "chart_18_scatter_wp80_opportunity_vs_failure.png"
    )

    scatter_chart(
        df, "games_scored_5_plus", "wasted_offense_loss_rate",
        "5+ Run Games vs Wasted-Offense Failure Rate",
        "Games scoring 5+ runs",
        "Wasted-offense failure rate",
        "chart_19_scatter_5plus_vs_failure.png"
    )

    side_by_side_metric_chart(
        df, "wp_80_losses", "wp_95_losses",
        "Top Teams: 80% WP Losses vs 95% WP Losses",
        "Number of losses",
        "chart_20_side_by_side_wp80_vs_wp95.png",
        top_n=10
    )

    threshold_df = pd.DataFrame({
        "Threshold": ["80%+", "85%+", "90%+", "95%+"],
        "Orioles": [orioles["wp_80_losses"], orioles["wp_85_losses"], orioles["wp_90_losses"], orioles["wp_95_losses"]],
        "League Mean": [df["wp_80_losses"].mean(), df["wp_85_losses"].mean(), df["wp_90_losses"].mean(), df["wp_95_losses"].mean()]
    })

    x = np.arange(len(threshold_df))
    width = 0.38
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x - width / 2, threshold_df["Orioles"], width=width, color=ORIOLES_ORANGE, edgecolor=ORIOLES_BLACK, label="Orioles")
    ax.bar(x + width / 2, threshold_df["League Mean"], width=width, color=SOFT_BLUE, edgecolor=DARK_GRAY, label="League Mean")
    ax.set_xticks(x)
    ax.set_xticklabels(threshold_df["Threshold"])
    ax.set_title("Orioles vs League Mean Across WP Collapse Thresholds", pad=15)
    ax.set_ylabel("Number of losses")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False)
    add_bar_labels(ax, decimals=1)
    save_clean_chart("chart_21_orioles_vs_league_threshold_counts.png")

    failure_rate_df = pd.DataFrame({
        "Metric": ["WP 80 Rate", "WP 95 Rate", "Big Lead Rate", "Wasted Offense Rate"],
        "Orioles": [orioles["wp_80_loss_rate"], orioles["wp_95_loss_rate"], orioles["big_lead_loss_rate"], orioles["wasted_offense_loss_rate"]],
        "League Mean": [df["wp_80_loss_rate"].mean(), df["wp_95_loss_rate"].mean(), df["big_lead_loss_rate"].mean(), df["wasted_offense_loss_rate"].mean()]
    })

    x = np.arange(len(failure_rate_df))
    width = 0.38
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.bar(x - width / 2, failure_rate_df["Orioles"], width=width, color=ORIOLES_ORANGE, edgecolor=ORIOLES_BLACK, label="Orioles")
    ax.bar(x + width / 2, failure_rate_df["League Mean"], width=width, color=SOFT_BLUE, edgecolor=DARK_GRAY, label="League Mean")
    ax.set_xticks(x)
    ax.set_xticklabels(failure_rate_df["Metric"], rotation=10)
    ax.set_title("Orioles Failure Rates vs League Mean", pad=15)
    ax.set_ylabel("Failure rate")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False)
    add_bar_labels(ax, decimals=3)
    save_clean_chart("chart_22_orioles_failure_rates_vs_league.png")

    opportunity_df = pd.DataFrame({
        "Metric": ["Reached 80% WP", "Reached 95% WP", "Led After 6", "Scored 5+"],
        "Orioles": [orioles["games_reached_80_wp"], orioles["games_reached_95_wp"], orioles["games_led_after_6"], orioles["games_scored_5_plus"]],
        "League Mean": [df["games_reached_80_wp"].mean(), df["games_reached_95_wp"].mean(), df["games_led_after_6"].mean(), df["games_scored_5_plus"].mean()]
    })

    x = np.arange(len(opportunity_df))
    width = 0.38
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.bar(x - width / 2, opportunity_df["Orioles"], width=width, color=ORIOLES_ORANGE, edgecolor=ORIOLES_BLACK, label="Orioles")
    ax.bar(x + width / 2, opportunity_df["League Mean"], width=width, color=SOFT_BLUE, edgecolor=DARK_GRAY, label="League Mean")
    ax.set_xticks(x)
    ax.set_xticklabels(opportunity_df["Metric"], rotation=10)
    ax.set_title("Orioles Opportunities vs League Mean", pad=15)
    ax.set_ylabel("Number of games")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False)
    add_bar_labels(ax, decimals=1, padding=0.15)
    save_clean_chart("chart_23_orioles_opportunities_vs_league.png")

    # Orioles summary visuals
    make_orioles_summary_table_image(df)
    make_orioles_rank_chart(df)
    make_full_orioles_dashboard(df)

    # Comeback visuals
    comparison_bar_chart(
        orioles["wp_20_comeback_wins"], df["wp_20_comeback_wins"].mean(), df["wp_20_comeback_wins"].median(),
        "Orioles vs League: Wins After Falling to 20% WP", "Number of wins",
        "chart_26_orioles_vs_league_wp20_comeback_wins.png", decimals=1
    )

    comparison_bar_chart(
        orioles["wp_15_comeback_wins"], df["wp_15_comeback_wins"].mean(), df["wp_15_comeback_wins"].median(),
        "Orioles vs League: Wins After Falling to 15% WP", "Number of wins",
        "chart_27_orioles_vs_league_wp15_comeback_wins.png", decimals=1
    )

    comparison_bar_chart(
        orioles["wp_10_comeback_wins"], df["wp_10_comeback_wins"].mean(), df["wp_10_comeback_wins"].median(),
        "Orioles vs League: Wins After Falling to 10% WP", "Number of wins",
        "chart_28_orioles_vs_league_wp10_comeback_wins.png", decimals=1
    )

    comparison_bar_chart(
        orioles["wp_5_comeback_wins"], df["wp_5_comeback_wins"].mean(), df["wp_5_comeback_wins"].median(),
        "Orioles vs League: Wins After Falling to 5% WP", "Number of wins",
        "chart_29_orioles_vs_league_wp5_comeback_wins.png", decimals=1
    )

    comparison_bar_chart(
        orioles["wp_20_comeback_rate"], df["wp_20_comeback_rate"].mean(), df["wp_20_comeback_rate"].median(),
        "Orioles vs League: 20% Comeback Rate", "Comeback rate",
        "chart_30_orioles_vs_league_wp20_comeback_rate.png", decimals=3
    )

    comparison_bar_chart(
        orioles["wp_15_comeback_rate"], df["wp_15_comeback_rate"].mean(), df["wp_15_comeback_rate"].median(),
        "Orioles vs League: 15% Comeback Rate", "Comeback rate",
        "chart_31_orioles_vs_league_wp15_comeback_rate.png", decimals=3
    )

    comparison_bar_chart(
        orioles["wp_10_comeback_rate"], df["wp_10_comeback_rate"].mean(), df["wp_10_comeback_rate"].median(),
        "Orioles vs League: 10% Comeback Rate", "Comeback rate",
        "chart_32_orioles_vs_league_wp10_comeback_rate.png", decimals=3
    )

    comparison_bar_chart(
        orioles["wp_5_comeback_rate"], df["wp_5_comeback_rate"].mean(), df["wp_5_comeback_rate"].median(),
        "Orioles vs League: 5% Comeback Rate", "Comeback rate",
        "chart_33_orioles_vs_league_wp5_comeback_rate.png", decimals=3
    )

    distribution_dot_plot(
        df, "wp_20_comeback_wins",
        "Distribution of MLB Teams by 20% Comeback Wins",
        "Wins after falling to 20% WP",
        "chart_34_dist_wp20_comeback_wins.png",
        decimals=1
    )

    distribution_dot_plot(
        df, "wp_20_comeback_rate",
        "Distribution of MLB Teams by 20% Comeback Rate",
        "20% comeback rate",
        "chart_35_dist_wp20_comeback_rate.png",
        decimals=3
    )

    top_n_chart(
        df, "wp_20_comeback_wins",
        "Top 10 Teams by 20% Comeback Wins",
        "Number of wins",
        "chart_36_top10_wp20_comeback_wins.png",
        top_n=10, decimals=0
    )

    top_n_chart(
        df[df["games_fell_to_20_wp"] >= 5].copy(), "wp_20_comeback_rate",
        "Top Teams by 20% Comeback Rate",
        "Comeback rate",
        "chart_37_top_wp20_comeback_rate.png",
        top_n=10, decimals=3
    )

    full_rank_chart(
        df, "wp_20_comeback_wins",
        "All MLB Teams Ranked by 20% Comeback Wins",
        "Number of wins",
        "chart_38_ranked_wp20_comeback_wins.png",
        decimals=0
    )

    full_rank_chart(
        df[df["games_fell_to_20_wp"] >= 5].copy(), "wp_20_comeback_rate",
        "All MLB Teams Ranked by 20% Comeback Rate",
        "Comeback rate",
        "chart_39_ranked_wp20_comeback_rate.png",
        decimals=3
    )

    scatter_chart(
        df, "games_fell_to_20_wp", "wp_20_comeback_rate",
        "20% Comeback Opportunities vs Comeback Rate",
        "Games falling to 20% WP",
        "20% comeback rate",
        "chart_40_scatter_wp20_comeback_opportunity_vs_rate.png"
    )

    comparison_bar_chart(
        orioles["trailed_after_6_wins"], df["trailed_after_6_wins"].mean(), df["trailed_after_6_wins"].median(),
        "Orioles vs League: Wins When Trailing After 6",
        "Number of wins",
        "chart_41_orioles_vs_league_trailed_after_6_wins.png",
        decimals=1
    )

    comparison_bar_chart(
        orioles["trailed_after_6_win_rate"], df["trailed_after_6_win_rate"].mean(), df["trailed_after_6_win_rate"].median(),
        "Orioles vs League: Win Rate When Trailing After 6",
        "Comeback rate",
        "chart_42_orioles_vs_league_trailed_after_6_rate.png",
        decimals=3
    )

    make_summary_table_csv(df)

    print("Outputs reset and recreated in /outputs_league")


if __name__ == "__main__":
    main()