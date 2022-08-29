import requests
import datetime
from fangraphs.leaders import leaders


def scrape_team_batting_stats(filters=None):
    if filters is None or filters == {}:
        filters = None
    by_hand = []
    if filters is not None and filters["pitcher_hand"] == "L":
        by_hand = [1]
    elif filters is not None and filters["pitcher_hand"] == "R":
        by_hand = [2]
    start_date = ""
    if filters is not None:
        start_date = filters["start_date"] if filters.get("start_date", None) is not None else "2022-03-01"

    base_url = "https://fangraphs.com/api/leaders/splits/splits-leaders"
    params = {
        "strPlayerId": "all",
        "strSplitArr": by_hand,
        "strGroup": "season",
        "strPosition": "B",
        "strType": "2",
        "strStartDate": start_date if start_date != "" else "2022-03-01",
        "strEndDate": "2022-11-01",
        "strSplitTeams": False,
        "dctFilters": [],
        "strStatType": "team",
        "strAutoPt": "false",
        "arrPlayerId": [],
        "strSplitArrPitch": []
    }

    with leaders.Splits() as scraper:
        scraper.configure("stat", "Batting")
        scraper.configure("type", "2")
        batting = scraper.export("Batting.csv")

        scraper.quit()
    return batting


def calculate_general(pitcher_hand=None):
    team_stats = {}
    stats_filter = {}
    if pitcher_hand is not None:
        stats_filter = {"pitcher_hand": pitcher_hand}

    year_team_stats = scrape_team_batting_stats(stats_filter)
    team_stats["season"] = year_team_stats

    # create month filter
    previous_month = (datetime.date.today() - datetime.timedelta(days=30))
    start_date = previous_month.strftime("%Y-%m-%d")
    stats_filter = {"start_date": start_date}
    if pitcher_hand is not None:
        stats_filter["pitcher_hand"] = pitcher_hand

    monthly_team_stats = scrape_team_batting_stats(stats_filter)
    team_stats["month"] = monthly_team_stats

    # weekly filter
    previous_week = (datetime.date.today() - datetime.timedelta(days=14))
    start_date = previous_week.strftime("%Y-%m-%d")
    stats_filter = {"start_date": start_date}
    if pitcher_hand is not None:
        stats_filter["pitcher_hand"] = pitcher_hand
    weekly_team_stats = scrape_team_batting_stats(stats_filter)
    team_stats["week"] = weekly_team_stats
    return team_stats


# takes in a team's stats and does the same calculations regardless of where they're from
def calculate_team(team_stats):
    print("hi")
    s = "hi"
    return s


# calculate stats for things we want repeatedly
def calculate_bats(self, team_id):
    # first find the team stats
    team_stats = {}
    team_abbr = self.teams["id_to_abbr"][team_id]

    # overall stats
    for team in self.team_stats:
        if team["team_abbr"] == team_abbr:
            s = calculate_team(team)
            team_stats["overall"] = s

    # lefty stats
    for team in self.team_stats:
        if team["team_abbr"] == team_abbr:
            l = calculate_team(team)
            team_stats["left"] = l

    # righty stats
    for team in self.team_stats:
        if team["team_abbr"] == team_abbr:
            r = calculate_team(team)
            team_stats["right"] = r

    return team_stats


def calculate_trend(stats):
    wrc_form = comparewRC(stats)
    k_form = compareK(stats)
    bb_form = compareBB(stats)
    ops_form = compare_ops(stats)

    return {
        "wrc": wrc_form,
        "k": k_form,
        "bb_form": bb_form,
        "ops_form": ops_form
    }


def calculate_trends(self, team_stats):
    trends = {}
    # trends for all hands
    overall_trend = calculate_trend(team_stats["overall"])
    trends["overall"] = overall_trend

    # trends for lefties
    left_trend = calculate_trend(team_stats["left"])
    trends["left"] = left_trend

    # trends for righties
    right_trend = calculate_trend((team_stats["right"]))
    trends["right"] = right_trend

    return trends


# we want to sort by wRC+
def sort_team_stats(team_stats):
    sorted_team_stats = sorted(team_stats, key=lambda i: i["wRC+"], reverse=True)
    return sorted_team_stats


def comparewRC(stats):
    overall_wrc = stats["overall"]["wRC+"]
    monthly_wrc = stats["monthly"]["wRC+"]
    weekly_wrc = stats["weekly"]["wRC+"]
    month_to_overall = monthly_wrc - overall_wrc
    week_to_month = weekly_wrc - monthly_wrc
    week_to_overall = weekly_wrc - overall_wrc
    return {
        "month": month_to_overall,
        "week_to_month": week_to_month,
        "week": week_to_overall
    }


def compareK(stats):
    overall = stats["overall"]["K%"]
    monthly = stats["monthly"]["K%"]
    weekly = stats["weekly"]["K%"]
    month_to_overall = monthly - overall
    week_to_month = weekly - monthly
    week_to_overall = weekly - overall
    return {
        "month": month_to_overall,
        "week_to_month": week_to_month,
        "week": week_to_overall
    }


def compare_ops(stats):
    overall = stats["overall"]["OPS"]
    monthly = stats["monthly"]["OPS"]
    weekly = stats["weekly"]["OPS"]
    month_to_overall = monthly - overall
    week_to_month = weekly - monthly
    week_to_overall = weekly - overall
    return {
        "month": month_to_overall,
        "week_to_month": week_to_month,
        "week": week_to_overall
    }


def compareBB(stats):
    overall = stats["overall"]["BB%"]
    monthly = stats["monthly"]["BB%"]
    weekly = stats["weekly"]["BB%"]
    month_to_overall = monthly - overall
    week_to_month = weekly - monthly
    week_to_overall = weekly - overall
    return {
        "month": month_to_overall,
        "week_to_month": week_to_month,
        "week": week_to_overall
    }


def get_k_rate(k_rate):
    if k_rate <= 10:
        return "excellent"
    elif k_rate <= 12.5:
        return "great"
    elif k_rate <= 16:
        return "above average"
    elif k_rate <= 20:
        return "average"
    elif k_rate <= 22:
        return "below average"
    elif k_rate <= 25:
        return "poor"
    return "awful"


def get_bb_rate(bb_rate):
    if bb_rate >= 15:
        return "excellent"
    elif bb_rate >= 12.5:
        return "great"
    elif bb_rate >= 10:
        return "above average"
    elif bb_rate >= 8:
        return "average"
    elif bb_rate >= 7:
        return "below average"
    elif bb_rate >= 5.5:
        return "poor"
    else:
        return "awful"


def get_wrc_plus(wrc):
    if wrc >= 160:
        return "excellent"
    elif wrc >= 140:
        return "great"
    elif wrc >= 115:
        return "above average"
    elif wrc >= 100:
        return "average"
    elif wrc >= 80:
        return "below average"
    elif wrc >= 75:
        return "poor"
    else:
        return "awful"
