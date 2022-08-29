import datetime
import json
import scraper
from calculate import pitchers as calculate_pitchers
from calculate import teams as calculate_teams


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

        # let's take the data and actually compile some sense with it

        slate_player_stats.append({
            player_info["firstLastName"]: general_pitcher_status
        })

    final = json.dumps(slate_player_stats)
    game_file_name = today_date + '.json'
    with open(game_file_name, "w") as outfile:
        outfile.write(final)



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
