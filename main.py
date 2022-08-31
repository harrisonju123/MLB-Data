import datetime
import json
import scraper
from calculate import pitchers as calculate_pitchers
from calculate import teams as calculate_teams
import csv


def main():
    today_date = datetime.datetime.today().strftime('%m-%d-%Y')
    teams = get_teams()
    # team_stats = calculate_teams.calculate_general()
    # lefty_stats = calculate_teams.calculate_general("L")
    # righty_stats = calculate_teams.calculate_general("R")
    # self.team_stats = team_stats
    # self.lefty_stats = lefty_stats
    # self.righty_stats = righty_stats

    scrape_pitcher_data(teams, today_date)


def scrape_pitcher_data(teams, today_date):
    # get pitcher to player id for fangraphs
    fangraphs_players_file = open('pitchers/pitchers.json', 'r')
    fangraphs_ids = json.load(fangraphs_players_file)

    # open today's pitchers
    pitcher_file_name = 'pitchers/' + today_date + '.json'
    pitcher_file = open(pitcher_file_name, 'r')
    pitcher_json = json.load(pitcher_file)

    # open today's games
    game_file_name = 'teams/' + today_date + '.json'
    game_file = open(game_file_name, 'r')
    games_json = json.load(game_file)

    # fetch the player info from fangraphs
    # counter to keep track of missing players
    missing_players = []
    slate_player_stats = []
    for player_name in pitcher_json["players"]:
        player_id = fangraphs_ids.get(player_name, None)
        if player_id is None:
            missing_players.append(player_name)
            continue

        # if we got here, it means we can call fangraphs with the player_id
        player_stats = scraper.get_pitching_stats(player_id)
        player_info = scraper.get_pitching_info(player_id)
        team_info = scraper.get_pitcher_team_info(player_id)
        # now that we have all the stats, we need to run calculations
        general_pitcher_status = calculate_pitchers.calculate_general(player_stats)
        pitcher_trends = calculate_pitchers.calculate_trends(player_stats)

        # fetch team stats from fangraphs
        pitcher_team_id = team_info["teamid"]
        pitcher_team_abbr = teams["id_to_abbr"][pitcher_team_id]
        # opposing_team_id = games_json[teams["abbr_to_id"][pitcher_team_abbr]]

        # # fetch opposing team stats
        # opposing_team_stats = calculate_teams.calculate_bats(self, opposing_team_id)
        #
        # # team trends
        # trends = calculate_teams.calculate_trends(self, opposing_team_stats)

        higher_is_good = ["o_swing", "pi_zone", "innings", "fastball_velocity", "fastball_vertical", "slider_vertical",
                          "slider_velocity", "splitter_vertical", "changeup_vertical"]
        lower_is_good = ["o_contact", "z_swing", "z_contact"]

        # let's take the data and actually compile some sense with it
        pitcher_score = 0
        for trend in pitcher_trends:
            comp_to_avg = pitcher_trends[trend].get("compared_to_average", 0)
            if comp_to_avg != 0:
                if comp_to_avg >= 1.1 and trend in higher_is_good:
                    if trend == "fastball_vertical":
                        if pitcher_trends[trend].get("trend", 0) < 0:
                            pitcher_score += 0.5
                    else:
                        pitcher_score += 0.5
                elif comp_to_avg <= 0.9 and trend in lower_is_good:
                    pitcher_score += 0.5

        if general_pitcher_status["siera"] == "excellent":
            pitcher_score += 3
        elif general_pitcher_status["siera"] == "great":
            pitcher_score += 2
        elif general_pitcher_status["siera"] == "above average":
            pitcher_score += 1
        elif general_pitcher_status["siera"] == "below average":
            pitcher_score -= 1
        elif general_pitcher_status["siera"] == "poor":
            pitcher_score -= 2
        elif general_pitcher_status["siera"] == "awful":
            pitcher_score -= 3
        elif general_pitcher_status["siera"] == "worst":
            pitcher_score -= 4

        if general_pitcher_status["x_fip"] == "excellent":
            pitcher_score += 3
        elif general_pitcher_status["x_fip"] == "great":
            pitcher_score += 2
        elif general_pitcher_status["x_fip"] == "above average":
            pitcher_score += 1
        elif general_pitcher_status["x_fip"] == "below average":
            pitcher_score -= 1
        elif general_pitcher_status["x_fip"] == "poor":
            pitcher_score -= 2
        elif general_pitcher_status["x_fip"] == "awful":
            pitcher_score -= 3
        elif general_pitcher_status["x_fip"] == "worst":
            pitcher_score -= 4

        general_pitcher_status["score"] = pitcher_score
        try:
            recent_k_average = pitcher_trends["strikeouts"]["recent_average"]
            below_average_count = pitcher_trends["strikeouts"]["below_average_count"]
            overall_k_average = pitcher_trends["strikeouts"]["overall_average"]
            siera = general_pitcher_status["siera"]
            x_fip = general_pitcher_status["x_fip"]
            ip = general_pitcher_status["ip"]
            k_rate = general_pitcher_status["k_rate"]
            total_pitch_average = pitcher_trends["strikeouts"]["total_pitch_average"]
            recent_pitch_count_average = pitcher_trends["strikeouts"]["recent_pitch_count_average"]
            worst_k = pitcher_trends["strikeouts"]["worst_k"]
        except Exception as e:
            recent_k_average = 0
            below_average_count = 0
            overall_k_average = 0
            siera = 0
            x_fip = 0
            ip = 0
            k_rate = 0
            total_pitch_average = 0
            recent_pitch_count_average = 0
            worst_k = 0

        slate_player_stats.append({
            "player": player_info["firstLastName"],
            "siera": siera,
            "x_fip": x_fip,
            "ip": ip,
            "k_rate": k_rate,
            "score": pitcher_score,
            "recent_k_average": recent_k_average,
            "below_average_count": below_average_count,
            "overall_k_average": overall_k_average,
            "total_pitch_average": total_pitch_average,
            "recent_pitch_count_average": recent_pitch_count_average,
            "worst_k": worst_k
        }
        )

    headers = ["player", "siera", "x_fip", "ip", "score", "k_rate","recent_k_average", "below_average_count", "overall_k_average", "total_pitch_average","recent_pitch_count_average", "worst_k"]
    game_file_name = today_date + '.csv'
    f = open(game_file_name, 'w')
    writer = csv.writer(f)
    writer.writerow(headers)
    for player in slate_player_stats:
        row = []
        for header in headers:
            row.append(player.get(header, 0))
        writer.writerow(row)
    f.close()


# generates a dictionary where the key is team id and value is team abbreviation
def get_teams():
    # get pitcher to player id for fangraphs
    teams_file = open('teams/teams.json', 'r')
    teams = json.load(teams_file)
    res = {}
    id_to_abbr = {}
    abbr_to_id = {}
    for team in teams:
        id_to_abbr[team["teamid"]] = team["AbbName"]
        abbr_to_id[team["AbbName"]] = team["teamid"]

    res["id_to_abbr"] = id_to_abbr
    res["abbr_to_id"] = abbr_to_id
    return res


if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
