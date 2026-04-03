import os
import time
import pickle
import requests
import pandas as pd

SEASON = 2025

SLEEP_SECONDS = 0.01
SAVE_EVERY_N_GAMES = 100

LINESCORE_CACHE_FILE = "cache_linescore.pkl"
WINPROB_PARSED_CACHE_FILE = "cache_winprob_parsed.pkl"

FULL_GAME_LOG_CSV = "mlb_2025_should_have_won_full_game_logs.csv"
FULL_GAME_LOG_PARQUET = "mlb_2025_should_have_won_full_game_logs.parquet"

TEAM_SUMMARY_CSV = "mlb_2025_should_have_won_team_summary.csv"
TEAM_SUMMARY_PARQUET = "mlb_2025_should_have_won_team_summary.parquet"

ORIOLES_COMPARISON_CSV = "orioles_2025_league_comparison_row.csv"
ORIOLES_MEAN_MEDIAN_CSV = "orioles_2025_vs_league_mean_median.csv"

TEAMS = {
    108: "Los Angeles Angels",
    109: "Arizona Diamondbacks",
    110: "Baltimore Orioles",
    111: "Boston Red Sox",
    112: "Chicago Cubs",
    113: "Cincinnati Reds",
    114: "Cleveland Guardians",
    115: "Colorado Rockies",
    116: "Detroit Tigers",
    117: "Houston Astros",
    118: "Kansas City Royals",
    119: "Los Angeles Dodgers",
    120: "Washington Nationals",
    121: "New York Mets",
    133: "Athletics",
    134: "Pittsburgh Pirates",
    135: "San Diego Padres",
    136: "Seattle Mariners",
    137: "San Francisco Giants",
    138: "St. Louis Cardinals",
    139: "Tampa Bay Rays",
    140: "Texas Rangers",
    141: "Toronto Blue Jays",
    142: "Minnesota Twins",
    143: "Philadelphia Phillies",
    144: "Atlanta Braves",
    145: "Chicago White Sox",
    146: "Miami Marlins",
    147: "New York Yankees",
    158: "Milwaukee Brewers",
}


def load_pickle_cache(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    return {}


def save_pickle_cache(obj, path):
    with open(path, "wb") as f:
        pickle.dump(obj, f)


def safe_divide(numerator, denominator, digits=3):
    if denominator is None or denominator == 0 or pd.isna(denominator):
        return None
    return round(numerator / denominator, digits)


def safe_save_parquet(df, path):
    try:
        df.to_parquet(path, index=False)
        print(f"Saved {path}")
    except Exception as e:
        print(f"Could not save {path}: {e}")


linescore_cache = load_pickle_cache(LINESCORE_CACHE_FILE)
winprob_cache = load_pickle_cache(WINPROB_PARSED_CACHE_FILE)


def get_schedule_for_team(team_id):
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&season={SEASON}&teamId={team_id}"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    data = r.json()

    rows = []
    team_name = TEAMS[team_id]

    for date_block in data.get("dates", []):
        game_date = date_block.get("date")

        for game in date_block.get("games", []):
            game_type = game.get("gameType")
            if game_type != "R":
                continue

            home_name = game["teams"]["home"]["team"]["name"]
            away_name = game["teams"]["away"]["team"]["name"]

            home_score = game["teams"]["home"].get("score")
            away_score = game["teams"]["away"].get("score")

            game_pk = int(game["gamePk"])
            status = game.get("status", {}).get("detailedState")
            abstract_status = game.get("status", {}).get("abstractGameState")

            team_is_home = home_name == team_name

            if team_is_home:
                team_runs = home_score
                opp_runs = away_score
                opponent = away_name
                home_away = "Home"
            else:
                team_runs = away_score
                opp_runs = home_score
                opponent = home_name
                home_away = "Away"

            result = None
            if team_runs is not None and opp_runs is not None:
                result = "W" if team_runs > opp_runs else "L"

            rows.append({
                "team_id": team_id,
                "team": team_name,
                "date": game_date,
                "gamePk": game_pk,
                "gameType": game_type,
                "status": status,
                "abstract_status": abstract_status,
                "opponent": opponent,
                "home_away": home_away,
                "team_is_home": team_is_home,
                "team_runs": team_runs,
                "opp_runs": opp_runs,
                "result": result,
            })

    return pd.DataFrame(rows)


def get_linescore(game_pk):
    game_pk = int(game_pk)

    if game_pk in linescore_cache:
        return linescore_cache[game_pk]

    url = f"https://statsapi.mlb.com/api/v1/game/{game_pk}/linescore"
    r = requests.get(url, timeout=30)
    data = r.json() if r.status_code == 200 else None
    linescore_cache[game_pk] = data
    return data


def parse_linescore_for_both_teams(game_pk):
    data = get_linescore(game_pk)

    base = {
        "home_led_after_6": None,
        "away_led_after_6": None,
        "home_biggest_lead": None,
        "away_biggest_lead": None,
        "home_runs_7_9": None,
        "away_runs_7_9": None,
    }

    if data is None:
        return base

    innings = data.get("innings", [])

    home_total = 0
    away_total = 0

    home_biggest_lead = 0
    away_biggest_lead = 0

    home_led_after_6 = False
    away_led_after_6 = False

    home_runs_7_9 = 0
    away_runs_7_9 = 0

    for inning_number, inning in enumerate(innings, start=1):
        home_runs = inning.get("home", {}).get("runs", 0)
        away_runs = inning.get("away", {}).get("runs", 0)

        home_total += home_runs
        away_total += away_runs

        home_lead = home_total - away_total
        away_lead = away_total - home_total

        home_biggest_lead = max(home_biggest_lead, home_lead)
        away_biggest_lead = max(away_biggest_lead, away_lead)

        if inning_number == 6:
            home_led_after_6 = home_lead > 0
            away_led_after_6 = away_lead > 0

        if inning_number in [7, 8, 9]:
            home_runs_7_9 += home_runs
            away_runs_7_9 += away_runs

    return {
        "home_led_after_6": home_led_after_6,
        "away_led_after_6": away_led_after_6,
        "home_biggest_lead": home_biggest_lead,
        "away_biggest_lead": away_biggest_lead,
        "home_runs_7_9": home_runs_7_9,
        "away_runs_7_9": away_runs_7_9,
    }


def parse_winprob_for_both_teams(game_pk):
    game_pk = int(game_pk)

    if game_pk in winprob_cache:
        return winprob_cache[game_pk]

    url = f"https://statsapi.mlb.com/api/v1/game/{game_pk}/winProbability"
    r = requests.get(url, timeout=30)

    base = {
        "home_max_win_prob_pct": None,
        "away_max_win_prob_pct": None,
    }

    if r.status_code != 200:
        winprob_cache[game_pk] = base
        return base

    data = r.json()
    if not isinstance(data, list):
        winprob_cache[game_pk] = base
        return base

    home_wp_values = []
    away_wp_values = []

    for play in data:
        if not isinstance(play, dict):
            continue

        home_wp = pd.to_numeric(play.get("homeTeamWinProbability"), errors="coerce")
        away_wp = pd.to_numeric(play.get("awayTeamWinProbability"), errors="coerce")

        if pd.isna(home_wp) or pd.isna(away_wp):
            continue

        if 0 < home_wp < 100:
            home_wp_values.append(float(home_wp))
        if 0 < away_wp < 100:
            away_wp_values.append(float(away_wp))

    result = {
        "home_max_win_prob_pct": round(max(home_wp_values), 1) if home_wp_values else None,
        "away_max_win_prob_pct": round(max(away_wp_values), 1) if away_wp_values else None,
    }

    winprob_cache[game_pk] = result
    return result


def build_unique_game_parse_table(schedule_df):
    unique_games = schedule_df[["gamePk", "date", "gameType", "abstract_status"]].drop_duplicates("gamePk").copy()

    unique_games = unique_games[
        (unique_games["gameType"] == "R") &
        (unique_games["abstract_status"] == "Final")
    ].drop_duplicates("gamePk").copy()

    parsed_rows = []
    total_games = len(unique_games)

    for idx, row in enumerate(unique_games.itertuples(index=False), start=1):
        game_pk = int(row.gamePk)

        line_info = parse_linescore_for_both_teams(game_pk)
        wp_info = parse_winprob_for_both_teams(game_pk)

        parsed_rows.append({
            "gamePk": game_pk,
            **line_info,
            **wp_info,
        })

        if idx % SAVE_EVERY_N_GAMES == 0 or idx == total_games:
            print(f"Parsed {idx}/{total_games} unique games")
            save_pickle_cache(linescore_cache, LINESCORE_CACHE_FILE)
            save_pickle_cache(winprob_cache, WINPROB_PARSED_CACHE_FILE)

        time.sleep(SLEEP_SECONDS)

    return pd.DataFrame(parsed_rows)


def build_full_league_game_log():
    schedule_frames = []

    for i, (team_id, team_name) in enumerate(TEAMS.items(), start=1):
        print(f"Fetching schedule {i}/30: {team_name}")
        schedule_frames.append(get_schedule_for_team(team_id))

    schedule_df = pd.concat(schedule_frames, ignore_index=True)

    schedule_df = schedule_df[
        (schedule_df["gameType"] == "R") &
        (schedule_df["abstract_status"] == "Final") &
        (schedule_df["team_runs"].notna()) &
        (schedule_df["opp_runs"].notna())
    ].drop_duplicates(subset=["team_id", "gamePk"]).copy()

    print("\nParsing unique games once...")
    parsed_games_df = build_unique_game_parse_table(schedule_df)

    full_df = schedule_df.merge(parsed_games_df, on="gamePk", how="left")

    full_df["led_after_6"] = full_df.apply(
        lambda r: r["home_led_after_6"] if r["team_is_home"] else r["away_led_after_6"],
        axis=1
    )

    full_df["biggest_lead"] = full_df.apply(
        lambda r: r["home_biggest_lead"] if r["team_is_home"] else r["away_biggest_lead"],
        axis=1
    )

    full_df["team_runs_7_9"] = full_df.apply(
        lambda r: r["home_runs_7_9"] if r["team_is_home"] else r["away_runs_7_9"],
        axis=1
    )

    full_df["opp_runs_7_9"] = full_df.apply(
        lambda r: r["away_runs_7_9"] if r["team_is_home"] else r["home_runs_7_9"],
        axis=1
    )

    full_df["max_win_prob_pct"] = full_df.apply(
        lambda r: r["home_max_win_prob_pct"] if r["team_is_home"] else r["away_max_win_prob_pct"],
        axis=1
    )

    full_df["is_loss"] = full_df["result"] == "L"
    full_df["scored_5_plus"] = full_df["team_runs"] >= 5

    full_df["reached_80_wp"] = full_df["max_win_prob_pct"] >= 80.0
    full_df["reached_85_wp"] = full_df["max_win_prob_pct"] >= 85.0
    full_df["reached_90_wp"] = full_df["max_win_prob_pct"] >= 90.0
    full_df["reached_95_wp"] = full_df["max_win_prob_pct"] >= 95.0

    full_df["games_led_after_6_flag"] = full_df["led_after_6"] == True
    full_df["games_biggest_lead_3_plus_flag"] = full_df["biggest_lead"] >= 3
    full_df["games_scored_5_plus_flag"] = full_df["scored_5_plus"] == True

    full_df["late_lead_loss"] = full_df["is_loss"] & (full_df["led_after_6"] == True)
    full_df["big_lead_loss"] = full_df["is_loss"] & (full_df["biggest_lead"] >= 3)
    full_df["wasted_offense_loss"] = full_df["is_loss"] & (full_df["scored_5_plus"] == True)

    full_df["should_have_won_rule_based"] = (
        full_df["late_lead_loss"] |
        full_df["big_lead_loss"] |
        full_df["wasted_offense_loss"]
    )

    full_df["late_collapse"] = (
        full_df["is_loss"] &
        (full_df["led_after_6"] == True) &
        (full_df["opp_runs_7_9"] > full_df["team_runs_7_9"])
    )

    full_df["wp_80_loss"] = full_df["is_loss"] & (full_df["max_win_prob_pct"] >= 80.0)
    full_df["wp_85_loss"] = full_df["is_loss"] & (full_df["max_win_prob_pct"] >= 85.0)
    full_df["wp_90_loss"] = full_df["is_loss"] & (full_df["max_win_prob_pct"] >= 90.0)
    full_df["wp_95_loss"] = full_df["is_loss"] & (full_df["max_win_prob_pct"] >= 95.0)

    full_df["date"] = pd.to_datetime(full_df["date"])

    return full_df


def summarize_team(group):
    team_name = group.name[0]
    team_id = group.name[1]

    losses = int((group["result"] == "L").sum())
    wins = int((group["result"] == "W").sum())

    games_reached_80_wp = int(group["reached_80_wp"].sum())
    games_reached_85_wp = int(group["reached_85_wp"].sum())
    games_reached_90_wp = int(group["reached_90_wp"].sum())
    games_reached_95_wp = int(group["reached_95_wp"].sum())

    games_led_after_6 = int(group["games_led_after_6_flag"].sum())
    games_biggest_lead_3_plus = int(group["games_biggest_lead_3_plus_flag"].sum())
    games_scored_5_plus = int(group["games_scored_5_plus_flag"].sum())

    late_lead_losses = int(group["late_lead_loss"].sum())
    big_lead_losses = int(group["big_lead_loss"].sum())
    wasted_offense_losses = int(group["wasted_offense_loss"].sum())

    rule_based_losses = int(group["should_have_won_rule_based"].sum())
    late_collapses = int(group["late_collapse"].sum())

    wp_80_losses = int(group["wp_80_loss"].sum())
    wp_85_losses = int(group["wp_85_loss"].sum())
    wp_90_losses = int(group["wp_90_loss"].sum())
    wp_95_losses = int(group["wp_95_loss"].sum())

    row = {
        "team": team_name,
        "team_id": team_id,
        "games": len(group),
        "wins": wins,
        "losses": losses,
        "games_reached_80_wp": games_reached_80_wp,
        "games_reached_85_wp": games_reached_85_wp,
        "games_reached_90_wp": games_reached_90_wp,
        "games_reached_95_wp": games_reached_95_wp,
        "games_led_after_6": games_led_after_6,
        "games_biggest_lead_3_plus": games_biggest_lead_3_plus,
        "games_scored_5_plus": games_scored_5_plus,
        "rule_based_losses": rule_based_losses,
        "late_lead_losses": late_lead_losses,
        "big_lead_losses": big_lead_losses,
        "wasted_offense_losses": wasted_offense_losses,
        "late_collapses": late_collapses,
        "wp_80_losses": wp_80_losses,
        "wp_85_losses": wp_85_losses,
        "wp_90_losses": wp_90_losses,
        "wp_95_losses": wp_95_losses,
    }

    row["rule_based_per_loss"] = safe_divide(rule_based_losses, losses)
    row["wp_80_per_loss"] = safe_divide(wp_80_losses, losses)
    row["wp_85_per_loss"] = safe_divide(wp_85_losses, losses)
    row["wp_90_per_loss"] = safe_divide(wp_90_losses, losses)
    row["wp_95_per_loss"] = safe_divide(wp_95_losses, losses)

    row["late_lead_loss_rate"] = safe_divide(late_lead_losses, games_led_after_6)
    row["big_lead_loss_rate"] = safe_divide(big_lead_losses, games_biggest_lead_3_plus)
    row["wasted_offense_loss_rate"] = safe_divide(wasted_offense_losses, games_scored_5_plus)

    row["wp_80_loss_rate"] = safe_divide(wp_80_losses, games_reached_80_wp)
    row["wp_85_loss_rate"] = safe_divide(wp_85_losses, games_reached_85_wp)
    row["wp_90_loss_rate"] = safe_divide(wp_90_losses, games_reached_90_wp)
    row["wp_95_loss_rate"] = safe_divide(wp_95_losses, games_reached_95_wp)

    return pd.Series(row)


def add_ranks(df):
    rank_cols = [
        "games_reached_80_wp",
        "games_reached_85_wp",
        "games_reached_90_wp",
        "games_reached_95_wp",
        "games_led_after_6",
        "games_biggest_lead_3_plus",
        "games_scored_5_plus",
        "rule_based_losses",
        "late_lead_losses",
        "big_lead_losses",
        "wasted_offense_losses",
        "wp_80_losses",
        "wp_85_losses",
        "wp_90_losses",
        "wp_95_losses",
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
    ]

    for col in rank_cols:
        df[f"{col}_rank"] = df[col].rank(ascending=False, method="min").astype("Int64")

    return df


def main():
    start = time.time()

    print("Current working directory:", os.getcwd())
    print("Linescore cache exists:", os.path.exists(LINESCORE_CACHE_FILE))
    print("Winprob parsed cache exists:", os.path.exists(WINPROB_PARSED_CACHE_FILE))
    print("Linescore cache entries:", len(linescore_cache))
    print("Winprob parsed cache entries:", len(winprob_cache))

    full_df = build_full_league_game_log()

    full_df.to_csv(FULL_GAME_LOG_CSV, index=False)
    safe_save_parquet(full_df, FULL_GAME_LOG_PARQUET)

    team_summary = (
        full_df.groupby(["team", "team_id"])
        .apply(summarize_team)
        .reset_index(drop=True)
    )

    team_summary = add_ranks(team_summary)
    team_summary = team_summary.sort_values("wp_90_losses", ascending=False).reset_index(drop=True)

    team_summary.to_csv(TEAM_SUMMARY_CSV, index=False)
    safe_save_parquet(team_summary, TEAM_SUMMARY_PARQUET)

    orioles_row = team_summary[team_summary["team"] == "Baltimore Orioles"].copy()
    orioles_row.to_csv(ORIOLES_COMPARISON_CSV, index=False)

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
    ]

    comparison_rows = []
    for metric in metrics:
        row = {
            "metric": metric,
            "league_mean": round(team_summary[metric].mean(), 3) if pd.api.types.is_numeric_dtype(team_summary[metric]) else None,
            "league_median": round(team_summary[metric].median(), 3) if pd.api.types.is_numeric_dtype(team_summary[metric]) else None,
            "orioles_value": round(float(orioles_row.iloc[0][metric]), 3) if pd.notna(orioles_row.iloc[0][metric]) else None,
        }

        rank_col = f"{metric}_rank"
        row["orioles_rank"] = int(orioles_row.iloc[0][rank_col]) if rank_col in orioles_row.columns and pd.notna(orioles_row.iloc[0][rank_col]) else None
        comparison_rows.append(row)

    comparison_df = pd.DataFrame(comparison_rows)
    comparison_df.to_csv(ORIOLES_MEAN_MEDIAN_CSV, index=False)

    save_pickle_cache(linescore_cache, LINESCORE_CACHE_FILE)
    save_pickle_cache(winprob_cache, WINPROB_PARSED_CACHE_FILE)

    elapsed = time.time() - start

    print("\nSaved:")
    print(f"- {FULL_GAME_LOG_CSV}")
    print(f"- {TEAM_SUMMARY_CSV}")
    print(f"- {ORIOLES_COMPARISON_CSV}")
    print(f"- {ORIOLES_MEAN_MEDIAN_CSV}")
    print(f"- {LINESCORE_CACHE_FILE}")
    print(f"- {WINPROB_PARSED_CACHE_FILE}")

    print(f"\nElapsed time: {elapsed / 60:.2f} minutes")

    print("\nOrioles summary:")
    print(orioles_row.to_string(index=False))

    print("\nOrioles vs league:")
    print(comparison_df.to_string(index=False))


if __name__ == "__main__":
    main()