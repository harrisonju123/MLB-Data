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


def calculate_trends(player_stat):
    trends = {}



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
