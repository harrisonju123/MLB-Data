import math

import numpy as np


def calculate_general(player_stat):
    overall_pitcher_stats = player_stat["year_stats"]

    siera = calculate_siera(overall_pitcher_stats["SIERA"])
    xFIP = calculate_xfip(overall_pitcher_stats["xFIP"])
    k_rate = calculate_strikeout_rate(overall_pitcher_stats["K%"])

    player_summary = {
        "siera": siera,
        "x_fip": xFIP,
        "ip": overall_pitcher_stats["IP"] / overall_pitcher_stats["Games"],
        "k_rate": k_rate
    }
    return player_summary


# What trends do we need to know about a pitcher?
# Pitcher's SIERA trends last 10 games vs overall
# pitcher's xFIP trends last 10 games
#
def calculate_trends(player_stat):
    if len(player_stat) < 2:
        return
    overall_pitcher_stats = player_stat["year_stats"]
    game_stats = player_stat["game_stats"]
    o_swing_trend = o_swing_trends(game_stats)
    o_contact_trend = o_contact_trends(game_stats)
    z_swing_trend = z_swing_trends(game_stats)
    z_contact = z_contact_trends(game_stats)
    pi_zone = pitch_zones_trends(game_stats)
    ip = innings_trends(game_stats)
    k_rate = strikeout_trends(game_stats)
    fa_vertical = 0.0000
    fa_velocity = 0.0000
    if game_stats[0].get("piFA-Z", None) is not None:
        if game_stats[0]["piFA-Z"] > 0:
            fa_vertical = fastball_vertical_trend(game_stats)
            fa_velocity = fastball_velocity_trend(game_stats)

    sinker_vertical = 0.0000
    if game_stats[0].get("piSI-Z", 0) != 0:
        sinker_vertical = sinker_vertical_trend(game_stats)

    changeup_vertical = 0.0000
    changeup_velocity = 0.0000
    if game_stats[0].get("piCH-Z", 0) != 0:
        changeup_vertical = changeup_vertical_trend(game_stats)
        changeup_velocity = changeup_velocity_trend(game_stats)

    slider_vertical = 0.0000
    slider_velocity = 0.0000
    if game_stats[0].get("piSL-Z", 0) != 0:
        slider_vertical = slider_vertical_trend(game_stats)
        slider_velocity = slider_velocity_trend(game_stats)

    cutter_vertical = 0.0000
    cutter_velocity = 0.0000
    if game_stats[0].get("piCU-Z", 0) != 0:
        cutter_vertical = cutter_vertical_trend(game_stats)
        cutter_velocity = cutter_velocity_trend(game_stats)

    splitter_vertical = 0.0000
    splitter_velocity = 0.0000
    if game_stats[0].get("piFS-Z", 0) != 0:
        splitter_vertical = splitter_vertical_trend(game_stats)
        splitter_velocity = splitter_velocity_trend(game_stats)

    knuckleball_vertical = 0.0000
    knuckleball_velocity = 0.0000
    if game_stats[0].get("piKN-Z", 0) != 0:
        knuckleball_vertical = knuckleball_vertical_trend(game_stats)
        knuckleball_velocity = knuckball_velocity_trend(game_stats)

    pitcher_trends = {}
    pitcher_trends["strikeouts"] = k_rate
    pitcher_trends["o_swing"] = o_swing_trend
    pitcher_trends["o_contact"] = o_contact_trend
    pitcher_trends["z_swing"] = z_swing_trend
    pitcher_trends["z_contact"] = z_contact
    pitcher_trends["pi_zone"] = pi_zone
    pitcher_trends["innings"] = ip
    if fa_velocity != 0:
        pitcher_trends["fastball_velocity"] = fa_velocity
        pitcher_trends["fastball_vertical"] = fa_vertical

    if sinker_vertical != 0:
        pitcher_trends["sinker_vertical"] = sinker_vertical

    if changeup_vertical != 0:
        pitcher_trends["changeup_vertical"] = changeup_vertical
        pitcher_trends["changeup_velocity"] = changeup_velocity

    if slider_vertical != 0:
        pitcher_trends["slider_vertical"] = slider_vertical
        pitcher_trends["slider_velocity"] = slider_velocity

    if cutter_vertical != 0:
        pitcher_trends["cutter_vertical"] = cutter_vertical
        pitcher_trends["cutter_velocity"] = cutter_velocity

    if splitter_vertical != 0:
        pitcher_trends["splitter_vertical"] = splitter_vertical
        pitcher_trends["splitter_velocity"] = splitter_velocity

    if knuckleball_vertical != 0:
        pitcher_trends["knuckleball_vertical"] = knuckleball_vertical
        pitcher_trends["knuckleball_velocity"] = knuckleball_velocity

    return pitcher_trends


# we also want to see pitcher strikeout trends
# check for last 10 game strikeouts and how many were below average
# also returns last 10 game average as well as overall average.
def strikeout_trends(game_stats):
    ks = []
    total_k = 0
    recent_k = 0
    total_pitches = 0
    for i, game in enumerate(game_stats):
        strikeout = game["SO"]
        pitches = game["Pitches"]
        total_k += strikeout
        total_pitches += pitches
    recent_pitch_count = 0
    average = total_k / len(game_stats)
    below_average = 0
    worst_k = 99
    for i, game in enumerate(game_stats):
        strikeout = game["SO"]
        pitches = game["Pitches"]
        if worst_k > strikeout:
            worst_k = strikeout
        if i <= 9:
            if strikeout < math.floor(average):
                below_average += 1
            recent_k += strikeout
            recent_pitch_count += pitches

    total_pitch_average = total_pitches / len(game_stats)
    recent_average = recent_k / 10
    recent_pitch_count_average = recent_pitch_count / 10

    return {
        "recent_average": recent_average,
        "below_average_count": below_average,
        "overall_average": average,
        "total_pitch_average": total_pitch_average,
        "recent_pitch_count_average": recent_pitch_count_average,
        "worst_k": worst_k
    }


# check swings outside the strike zone
# look for trends
# First get the o-swing data in a list
# Arrange using numpy and use the built-in polyfit
def o_swing_trends(game_stats):
    o_swings = []
    average_o_swing = 0.0000
    total_o_swing = 0.0000
    trend_o_swing = 0.0000

    for i, game in enumerate(game_stats):
        o_swing = game.get("O-Swing%", 0)
        # go over just the first 4 i < 4
        if i < 4:
            trend_o_swing += o_swing
        total_o_swing += o_swing
        o_swings.append(o_swing)

    average_o_swing = total_o_swing / len(o_swings)
    average_trend_o_swing = trend_o_swing / 4

    x = np.arange(0, len(o_swings))
    y = np.array(o_swings)
    z = []
    try:
        z = np.polyfit(x, y, 1)
    except Exception as e:
        z.append(0)

    return {
        "trend": z[0] * 100,
        "compared_to_average": average_trend_o_swing / average_o_swing
    }


def o_contact_trends(game_stats):
    stat_list = []
    average = 0.0000
    total = 0.0000
    trend = 0.0000

    for i, game in enumerate(game_stats):
        stat = game.get("O-Contact%", 0)
        # go over just the first 4
        if i < 4:
            trend += stat
        total += stat
        stat_list.append(stat)

    average_stat = total / len(stat_list)
    average_trend = trend / 4

    x = np.arange(0, len(stat_list))
    y = np.array(stat_list)
    z = []
    try:
        z = np.polyfit(x, y, 1)
    except Exception as e:
        z.append(0)

    return {
        "trend": z[0] * 100,
        "compared_to_average": average_trend / average_stat
    }


def z_swing_trends(game_stats):
    stat_list = []
    average = 0.0000
    total = 0.0000
    trend = 0.0000

    for i, game in enumerate(game_stats):
        stat = game.get("Z-Swing%", 0)
        # go over just the first 4
        if i < 4:
            trend += stat
        total += stat
        stat_list.append(stat)

    average_stat = total / len(stat_list)
    average_trend = trend / 4

    x = np.arange(0, len(stat_list))
    y = np.array(stat_list)
    z = []
    try:
        z = np.polyfit(x, y, 1)
    except Exception as e:
        z.append(0)

    return {
        "trend": z[0] * 100,
        "compared_to_average": average_trend / average_stat
    }


def z_contact_trends(game_stats):
    stat_list = []
    average = 0.0000
    total = 0.0000
    trend = 0.0000

    for i, game in enumerate(game_stats):
        stat = game.get("Z-Contact%", 0)
        # go over just the first 4
        if i < 4:
            trend += stat
        total += stat
        stat_list.append(stat)

    average_stat = total / len(stat_list)
    average_trend = trend / 4

    x = np.arange(0, len(stat_list))
    y = np.array(stat_list)
    z = []
    try:
        z = np.polyfit(x, y, 1)
    except Exception as e:
        z.append(0)

    return {
        "trend": z[0] * 100,
        "compared_to_average": average_trend / average_stat
    }


def pitch_zones_trends(game_stats):
    stat_list = []
    average = 0.0000
    total = 0.0000
    trend = 0.0000

    for i, game in enumerate(game_stats):
        stat = game.get("piZone%", 0)
        # go over just the first 4
        if i < 4:
            trend += stat
        total += stat
        stat_list.append(stat)

    average_stat = total / len(stat_list)
    average_trend = trend / 4

    x = np.arange(0, len(stat_list))
    y = np.array(stat_list)
    z = []
    try:
        z = np.polyfit(x, y, 1)
    except Exception as e:
        z.append(0)

    return {
        "trend": z[0] * 100,
        "compared_to_average": average_trend / average_stat
    }


def innings_trends(game_stats):
    stat_list = []
    average = 0.0000
    total = 0.0000
    trend = 0.0000

    for i, game in enumerate(game_stats):
        stat = game["IP"]
        # go over just the first 4
        if i < 4:
            trend += stat
        total += stat
        stat_list.append(stat)

    average_stat = total / len(stat_list)
    average_trend = trend / 4

    x = np.arange(0, len(stat_list))
    y = np.array(stat_list)
    z = []
    try:
        z = np.polyfit(x, y, 1)
    except Exception as e:
        z.append(0)

    return {
        "trend": z[0] * 100,
        "compared_to_average": average_trend / average_stat
    }


# less is better
def fastball_vertical_trend(game_stats):
    stat_list = []
    average = 0.0000
    total = 0.0000
    trend = 0.0000

    for i, game in enumerate(game_stats):
        stat = game.get("piFA-Z", 0)
        # go over just the first 4
        if i < 4:
            trend += stat
        total += stat
        stat_list.append(stat)

    average_stat = total / len(stat_list)
    average_trend = trend / 4

    x = np.arange(0, len(stat_list))
    y = np.array(stat_list)
    if len(stat_list) > 1:
        z = np.polyfit(x, y, 1)
    else:
        z = [0]

    return {
        "trend": z[0] * 100,
        "compared_to_average": average_trend / average_stat
    }


def fastball_velocity_trend(game_stats):
    stat_list = []
    average = 0.0000
    total = 0.0000
    trend = 0.0000

    for i, game in enumerate(game_stats):
        stat = game.get("FBv", 0)
        # go over just the first 4
        if i < 4:
            trend += stat
        total += stat
        stat_list.append(stat)

    average_stat = total / len(stat_list)
    average_trend = trend / 4

    x = np.arange(0, len(stat_list))
    y = np.array(stat_list)
    if len(stat_list) > 1:
        z = np.polyfit(x, y, 1)
    else:
        z = [0]

    return {
        "trend": z[0] * 100,
        "compared_to_average": average_trend / average_stat
    }


# more is better
def sinker_vertical_trend(game_stats):
    stat_list = []
    average = 0.0000
    total = 0.0000
    trend = 0.0000

    for i, game in enumerate(game_stats):
        stat = game.get("piSI-Z", 0)
        # go over just the first 4
        if i < 4:
            trend += stat
        total += stat
        stat_list.append(stat)

    average_stat = total / len(stat_list)
    average_trend = trend / 4

    x = np.arange(0, len(stat_list))
    y = np.array(stat_list)
    if len(stat_list) > 1:
        z = np.polyfit(x, y, 1)
    else:
        z = [0]

    return {
        "trend": z[0] * 100,
        "compared_to_average": average_trend / average_stat
    }


# more is better
def changeup_vertical_trend(game_stats):
    stat_list = []
    average = 0.0000
    total = 0.0000
    trend = 0.0000

    for i, game in enumerate(game_stats):
        stat = game.get("piCH-Z", 0)
        # go over just the first 4
        if i < 4:
            trend += stat
        total += stat
        stat_list.append(stat)

    average_stat = total / len(stat_list)
    average_trend = trend / 4

    x = np.arange(0, len(stat_list))
    y = np.array(stat_list)
    if len(stat_list) > 1:
        z = np.polyfit(x, y, 1)
    else:
        z = [0]

    return {
        "trend": z[0] * 100,
        "compared_to_average": average_trend / average_stat
    }


def changeup_velocity_trend(game_stats):
    stat_list = []
    average = 0.0000
    total = 0.0000
    trend = 0.0000

    for i, game in enumerate(game_stats):
        stat = game.get("CHv", 0)
        # go over just the first 4
        if i < 4:
            trend += stat
        total += stat
        stat_list.append(stat)

    average_stat = total / len(stat_list)
    average_trend = trend / 4

    x = np.arange(0, len(stat_list))
    y = np.array(stat_list)
    if len(stat_list) > 1:
        z = np.polyfit(x, y, 1)
    else:
        z = [0]

    return {
        "trend": z[0] * 100,
        "compared_to_average": average_trend / average_stat if average_stat != 0 else 0
    }


# more is better
def slider_vertical_trend(game_stats):
    stat_list = []
    average = 0.0000
    total = 0.0000
    trend = 0.0000

    for i, game in enumerate(game_stats):
        stat = game.get("piSL-Z", 0)
        # go over just the first 4
        if i < 4:
            trend += stat
        total += stat
        stat_list.append(stat)

    average_stat = total / len(stat_list)
    average_trend = trend / 4

    x = np.arange(0, len(stat_list))
    y = np.array(stat_list)
    if len(stat_list) > 1:
        z = np.polyfit(x, y, 1)
    else:
        z = [0]

    return {
        "trend": z[0] * 100,
        "compared_to_average": average_trend / average_stat
    }


def slider_velocity_trend(game_stats):
    stat_list = []
    average = 0.0000
    total = 0.0000
    trend = 0.0000

    for i, game in enumerate(game_stats):
        stat = game.get("SLv", 0)
        # go over just the first 4
        if i < 4:
            trend += stat
        total += stat
        stat_list.append(stat)

    average_stat = total / len(stat_list)
    average_trend = trend / 4

    x = np.arange(0, len(stat_list))
    y = np.array(stat_list)
    if len(stat_list) > 1:
        z = np.polyfit(x, y, 1)
    else:
        z = [0]

    return {
        "trend": z[0] * 100,
        "compared_to_average": average_trend / average_stat if average_stat != 0 else 0
    }


def curveball_vertical_trend(game_stats):
    stat_list = []
    average = 0.0000
    total = 0.0000
    trend = 0.0000

    for i, game in enumerate(game_stats):
        stat = game.get("piCU-Z", 0)
        # go over just the first 4
        if i < 4:
            trend += stat
        total += stat
        stat_list.append(stat)

    average_stat = total / len(stat_list)
    average_trend = trend / 4

    x = np.arange(0, len(stat_list))
    y = np.array(stat_list)
    if len(stat_list) > 1:
        z = np.polyfit(x, y, 1)
    else:
        z = [0]

    return {
        "trend": z[0] * 100,
        "compared_to_average": average_trend / average_stat
    }


def curveball_velocity_trend(game_stats):
    stat_list = []
    average = 0.0000
    total = 0.0000
    trend = 0.0000

    for i, game in enumerate(game_stats):
        stat = game.get("CBv", 0)
        # go over just the first 4
        if i < 4:
            trend += stat
        total += stat
        stat_list.append(stat)

    average_stat = total / len(stat_list)
    average_trend = trend / 4

    x = np.arange(0, len(stat_list))
    y = np.array(stat_list)
    if len(stat_list) > 1:
        z = np.polyfit(x, y, 1)
    else:
        z = [0]

    return {
        "trend": z[0] * 100,
        "compared_to_average": average_trend / average_stat
    }


def cutter_vertical_trend(game_stats):
    stat_list = []
    average = 0.0000
    total = 0.0000
    trend = 0.0000

    for i, game in enumerate(game_stats):
        stat = game.get("piFC-Z%", 0)
        # go over just the first 4
        if i < 4:
            trend += stat
        total += stat
        stat_list.append(stat)

    average_stat = total / len(stat_list)
    average_trend = trend / 4

    x = np.arange(0, len(stat_list))
    y = np.array(stat_list)
    if len(stat_list) > 1:
        z = np.polyfit(x, y, 1)
    else:
        z = [0]

    return {
        "trend": z[0] * 100,
        "compared_to_average": average_trend / average_stat if average_stat != 0 else 0
    }


def cutter_velocity_trend(game_stats):
    stat_list = []
    average = 0.0000
    total = 0.0000
    trend = 0.0000

    for i, game in enumerate(game_stats):
        stat = game.get("CTv", 0)
        # go over just the first 4
        if i < 4:
            trend += stat
        total += stat
        stat_list.append(stat)

    average_stat = total / len(stat_list)
    average_trend = trend / 4

    x = np.arange(0, len(stat_list))
    y = np.array(stat_list)
    if len(stat_list) > 1:
        z = np.polyfit(x, y, 1)
    else:
        z = [0]

    return {
        "trend": z[0] * 100,
        "compared_to_average": average_trend / average_stat if average_stat != 0 else 0
    }


def splitter_vertical_trend(game_stats):
    stat_list = []
    average = 0.0000
    total = 0.0000
    trend = 0.0000

    for i, game in enumerate(game_stats):
        stat = game.get("piFS-Z", 0)
        # go over just the first 4
        if i < 4:
            trend += stat
        total += stat
        stat_list.append(stat)

    average_stat = total / len(stat_list)
    average_trend = trend / 4

    x = np.arange(0, len(stat_list))
    y = np.array(stat_list)
    if len(stat_list) > 1:
        z = np.polyfit(x, y, 1)
    else:
        z = [0]

    return {
        "trend": z[0] * 100,
        "compared_to_average": average_trend / average_stat
    }


def splitter_velocity_trend(game_stats):
    stat_list = []
    average = 0.0000
    total = 0.0000
    trend = 0.0000

    for i, game in enumerate(game_stats):
        stat = game.get("SFv", 0)
        # go over just the first 4
        if i < 4:
            trend += stat
        total += stat
        stat_list.append(stat)

    average_stat = total / len(stat_list)
    average_trend = trend / 4

    x = np.arange(0, len(stat_list))
    y = np.array(stat_list)
    if len(stat_list) > 1:
        z = np.polyfit(x, y, 1)
    else:
        z = [0]

    return {
        "trend": z[0] * 100,
        "compared_to_average": average_trend / average_stat if average_stat != 0 else 0
    }


def knuckball_velocity_trend(game_stats):
    stat_list = []
    average = 0.0000
    total = 0.0000
    trend = 0.0000

    for i, game in enumerate(game_stats):
        stat = game.get("KNv", 0)
        # go over just the first 4
        if i < 4:
            trend += stat
        total += stat
        stat_list.append(stat)

    average_stat = total / len(stat_list)
    average_trend = trend / 4

    x = np.arange(0, len(stat_list))
    y = np.array(stat_list)
    if len(stat_list) > 1:
        z = np.polyfit(x, y, 1)
    else:
        z = [0]

    return {
        "trend": z[0] * 100,
        "compared_to_average": average_trend / average_stat
    }


def knuckleball_vertical_trend(game_stats):
    stat_list = []
    average = 0.0000
    total = 0.0000
    trend = 0.0000

    for i, game in enumerate(game_stats):
        stat = game.get("piKN-Z", 0)
        # go over just the first 4 i <
        if i < 4:
            trend += stat
        total += stat
        stat_list.append(stat)

    average_stat = total / len(stat_list)
    average_trend = trend / 4

    x = np.arange(0, len(stat_list))
    y = np.array(stat_list)
    if len(stat_list) > 1:
        z = np.polyfit(x, y, 1)
    else:
        z = [0]

    return {
        "trend": z[0] * 100,
        "compared_to_average": average_trend / average_stat
    }


def calculate_siera(siera):
    # SIERA -
    # 1. 2.9 Excellent
    # 2. 3.25 Great
    # 3. 3.75 Above average
    # 4. 3.9 Average
    # 5. 4.2 Below Average
    # 6. 4.5 Poor
    # 7. 5.0 Awful
    if siera <= 2.9:
        return "excellent"
    elif siera <= 3.25:
        return "great"
    elif siera <= 3.75:
        return "above average"
    elif siera <= 3.9:
        return "average"
    elif siera <= 4.2:
        return "below average"
    elif siera <= 4.5:
        return "poor"
    else:
        return "worst"


def calculate_xfip(xfip):
    # Excellent
    # 2.90
    # Great
    # 3.20
    # Above Average
    # 3.50
    # Average
    # 3.80
    # Below Average
    # 4.10
    # Poor
    # 4.40
    # Awful
    # 4.70
    if xfip <= 2.9:
        return "excellent"
    elif xfip <= 3.20:
        return "great"
    elif xfip <= 3.5:
        return "above average"
    elif xfip <= 3.8:
        return "average"
    elif xfip <= 4.1:
        return "below average"
    elif xfip <= 4.4:
        return "poor"
    elif xfip <= 4.7:
        return "awful"
    else:
        return "worst"


def calculate_strikeout_rate(k):
    # 1.27 % 10k / 9 excellent
    # 2.24 % 9k / 9 great
    # 3.22 % 8.2 / 9 aboveaverage
    # 4.20 % 7.7 average
    # 5.17 % 7.0 belowaverage
    # 6.15 % 6.0 poor
    # 7.13 % 5.0 awful
    if k > 0.24:
        return 10.00 / 9.00
    elif k > 0.22:
        return 9.00 / 9.00
    elif k > 0.2:
        return 8.20 / 9.00
    elif k > 0.17:
        return 7.00 / 9.00
    elif k > 0.15:
        return 6.00 / 9.00
    else:
        return 5.00 / 9.00
