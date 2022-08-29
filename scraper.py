import datetime
import requests


def get_pitching_stats(player_id):
    base_url = "https://www.fangraphs.com/api/players/game-log"
    params = {
        "playerid": player_id,
        "position": "P",
        "type": 0
    }
    response = requests.get(base_url, params)
    data = response.json()
    mlb_stats = data["mlb"]

    player_composite_stats = {
        "year_stats": mlb_stats[0],
        "game_stats": mlb_stats[1:]
    }

    return player_composite_stats


def get_pitching_info(player_id):
    base_url = "https://www.fangraphs.com/api/players/stats"
    params = {
        "playerid": player_id,
        "position": "P"
    }
    response = requests.get(base_url, params)
    data = response.json()
    pitcher_info = data["playerInfo"]
    return pitcher_info


def get_pitcher_team_info(player_id):
    base_url = "https://www.fangraphs.com/api/players/stats"
    params = {
        "playerid": player_id,
        "position": "P"
    }
    response = requests.get(base_url, params)
    data = response.json()
    team_info = data["teamInfo"]
    return team_info