#    How to write a new stat:
#        1  If you need more information than is in the HudCache table, then you have to write SQL.
#        2  The raw stats are available in the stat_dict dict. For example the number of vpips would be
#           stat_dict[player]["vpip"]. So the % vpip is
#           float(stat_dict[player]["vpip"])/float(stat_dict[player]["vpip_opp"]). You can see how the
#           keys of stat_dict relate to the column names in HudCache by inspecting
#           the proper section of the SQL.py module.
#        3  You have to write a small function for each stat you want to add. See
#           the vpip() function for example.  This function has to be protected from
#           exceptions, using something like the try:/except: paragraphs in vpip.
#        4  The name of the function has to be the same as the of the stat used
#           in the config file.
#        5  The stat functions have a peculiar return value, which is outlined in
#           the do_stat function. This format is useful for tool tips and maybe
#           other stuff.

def do_stat(stat_dict, player=1, stat="vpip"):
    # Calculates a specific statistic for a given player in a hand.
    # 
    # Args:
    #     stat_dict (dict): A dictionary containing statistics for all players in the hand.
    #     player (int, optional): The player for whom to calculate the statistic. Defaults to 24.
    #     stat (str, optional): The statistic to calculate. Defaults to 'vpip'.
    # 
    # Returns:
    #     The calculated statistic for the player, or None if the statistic is not in the list of available statistics.

    if stat not in STAT_LIST:
        return None

    result = eval(f"{stat}(stat_dict, {player})")

    return result

#    OK, for reference the tuple returned by the stat is:
#    0 - formatted stat with appropriate precision, eg. 33; shown in HUD
#    1 - formatted stat with appropriate precision, punctuation and name of stat, eg vpip=33%
#    2 - the calculation that got the stat, eg 9/27
#    3 - the name of the stat, useful for a tooltip, eg vpip

###########################################
#    Functions that return individual stats

def vpip(stat_dict, player):
    # A function to calculate and return VPIP (Voluntarily Put In Pot) percentage.
    # 
    # Args:
    #     stat_dict (dict): A dictionary containing player statistics.
    #     player (str): The player for whom to calculate the VPIP.
    # 
    # Returns:
    #     tuple: A tuple containing:
    #         - VPIP percentage formatted as a string
    #         - 'vpip=' followed by VPIP percentage formatted as a percentage string
    #         - '(x/y)' where x is the VPIP and y is VPIP opportunities
    #         - 'Voluntarily put in preflop %'
    # 
    #     If an error occurs, returns:
    #         - 'NA'
    #         - 'vpip=NA'
    #         - '(0/0)'
    #         - 'Voluntarily put in preflop %'
    try:
        opp = stat_dict[player]["vpip_opp"]
        action = stat_dict[player]["vpip"]
        stat = float(action) / opp

        return f"{stat * 100:3.1f}", f"vpip={stat * 100:3.1f}", f"({action}/{opp})", "Voluntarily put in preflop %"
    except Exception:
        return "NA", "vpip=NA", "(0/0)", "Voluntarily put in preflop %"

def pfr(stat_dict, player):
    # Calculate and return the preflop raise percentage (pfr) for a player.
    # 
    # Args:
    #     stat_dict (dict): A dictionary containing player statistics.
    #     player (int): The player for whom the pfr is calculated.
    # 
    # Returns:
    #     tuple: A tuple containing the pfr value, formatted pfr percentages, and related information.
    try:
        opp = stat_dict[player]["pfr_opp"]
        action = stat_dict[player]["pfr"]
        stat = float(action) / opp

        return f"{stat * 100:3.1f}", f"pfr={stat * 100:3.1f}", f"({action}/{opp})", "Preflop raise %"
    except Exception:
        return "NA", "pfr=NA", "(0/0)", "Preflop raise %"

def n(stat_dict, player):
    # Calculate and format the number of hands seen for a player.
    # 
    # Args:
    #     stat_dict (dict): A dictionary containing player statistics.
    #     player (int): The player for whom the number of hands seen is calculated.
    # 
    # Returns:
    #     tuple: A tuple containing formatted strings representing the number of hands seen in different ways.
    try:
        # If sample is large enough, use X.Yk notation instead
        n = stat_dict[player]["n"]
        fmt = f"{n}"

        if n >= 10000:
            fmt = f"{n / 1000:.1f}k"

        return fmt, f"n={n}", f"", "Number of hands seen"
    except Exception:
        # Number of hands shouldn't ever be "NA"; zeroes are better here
        return "0", "n=0", "", "Number of hands seen"

def steal(stat_dict, player):
    # Calculate and format the steal percentage for a player.
    # 
    # Args:
    #     stat_dict (dict): A dictionary containing player statistics.
    #     player (int): The player for whom the steal percentage is calculated.
    # 
    # Returns:
    #     tuple: A tuple containing formatted strings representing the steal percentage in different ways.
    #         - '%3.1f' (str): The steal percentage formatted as a string with 3 decimal places.
    #         - 'steal=%3.1f%%' (str): The steal percentage formatted as a string with 3 decimal places and a percentage sign.
    #         - '(%d/%d)' (str): The steal count and steal opponent count formatted as a string.
    #         - '% steal attempted' (str): The description of the steal percentage.
    try:
        opp = stat_dict[player]["steal_opp"]
        action = stat_dict[player]["steal"]
        stat = float(action) / opp

        return f"{stat * 100:3.1f}", f"steal={stat * 100:3.1f}", f"({action}/{opp})", "% steal attempted"
    except Exception:
        return "NA", "steal=NA", "(0/0)", "% steal attempted"

def f_SB_steal(stat_dict, player):
    # Calculate the folded Small Blind (SB) to steal statistics for a player.
    # 
    # Args:
    #     stat_dict (dict): A dictionary containing player statistics.
    #     player (int): The player for whom the statistics are calculated.
    # 
    # Returns:
    #     tuple: A tuple containing the folded SB to steal statistics.
    #         - '%3.1f' (str): The folded SB to steal percentage formatted as a string with 3 decimal places.
    #         - 'f_SB_steal=%3.1f%%' (str): The folded SB to steal percentage formatted with a specific label.
    #         - '(%d/%d)' (str): The number of folded SB to steal and the total number of folded SB formatted as a string.
    #         - '% folded SB to steal' (str): The description of the folded SB to steal percentage.
    try:
        opp = stat_dict[player]["sb_stolen"]
        action = stat_dict[player]["sb_not_def"]
        stat = float(action) / opp

        return f"{stat * 100:3.1f}", f"f_SB_steal={stat * 100:3.1f}", f"({action}/{opp})", "% folded SB to steal"
    except Exception:
        return "NA", "f_SB_steal=NA", "(0/0)", "% folded SB to steal"

def f_BB_steal(stat_dict, player):
    # Calculate the folded Big Blind (BB) to steal statistics for a player.
    # 
    # Args:
    #     stat_dict (dict): A dictionary containing player statistics.
    #     player (int): The player for whom the statistics are calculated.
    # 
    # Returns:
    #     tuple: A tuple containing the calculated statistics in different formats:
    #         - String: The statistic formatted as a percentage with one decimal place.
    #         - String: A formatted string representing the statistic with a suffix.
    #         - String: A formatted string showing the count of BB not defended and BB stolen.
    #         - String: A description of the statistic.
    try:
        opp = stat_dict[player]["bb_stolen"]
        action = stat_dict[player]["bb_not_def"]
        stat = float(action) / opp

        return f"{stat * 100:3.1f}", f"f_BB_steal={stat * 100:3.1f}", f"({action}/{opp})", "% folded BB to steal"
    except Exception:
        return "NA", "f_BB_steal=NA", "(0/0)", "% folded BB to steal"

def three_B(stat_dict, player):
    # Calculate the three bet statistics for a player.
    # 
    # Args:
    #     stat_dict (dict): A dictionary containing player statistics.
    #     player (int): The player for whom the statistics are calculated.
    # 
    # Returns:
    #     tuple: A tuple containing the calculated statistics in different formats:
    #         - String: The statistic formatted as a percentage with one decimal place.
    #         - String: A formatted string representing the statistic with a suffix.
    #         - String: A formatted string showing the count of three bets made and opponent's three bets.
    #         - String: A description of the statistic.
    try:
        opp = stat_dict[player]["tb_opp_0"]
        action = stat_dict[player]["tb_0"]
        stat = float(action) / opp

        return f"{stat * 100:3.1f}", f"3B_pf={stat * 100:3.1f}", f"({action}/{opp})", "% 3 bet preflop"
    except Exception:
        return "NA", "3B_pf=NA", "(0/0)", "% 3 bet preflop"

def four_B(stat_dict, player):
    # Calculate the four bet statistics for a player.
    # 
    # Args:
    #     stat_dict (dict): A dictionary containing player statistics.
    #     player (int): The player for whom the statistics are calculated.
    # 
    # Returns:
    #     tuple: A tuple containing the calculated statistics in different formats:
    #         - String: The statistic formatted as a percentage with one decimal place.
    #         - String: A formatted string representing the statistic with a suffix.
    #         - String: A formatted string showing the count of four bets made and opponent's four bets.
    #         - String: A description of the statistic.
    try:
        opp = stat_dict[player]["fb_opp_0"]
        action = stat_dict[player]["fb_0"]
        stat = float(action) / opp

        return f"{stat * 100:3.1f}", f"4B_pf={stat * 100:3.1f}", f"({action}/{opp})", "% 4 bet preflop"
    except Exception:
        return "NA", "4B_pf=NA", "(0/0)", "% 4 bet preflop"

def raiseToSteal(stat_dict, player):
    # Calculate the raise to steal stat for a player.
    # 
    # Args:
    #     stat_dict (dict): A dictionary containing stats for each player.
    #     player (int): The player for whom the stat is calculated.
    # 
    # Returns:
    #     tuple: A tuple containing the raise to steal stat, formatted percentages, and additional information.
    try:
        opp = stat_dict[player]["rts_opp"]
        action = stat_dict[player]["rts"]
        stat = float(action) / opp

        return f"{stat * 100:3.1f}", f"rts={stat * 100:3.1f}", f"({action}/{opp})", "% raise to steal"
    except Exception:
        return "NA", "rts=NA", "(0/0)", "% raise to steal"

def f_3bet(stat_dict, player):
    # Calculate the Fold to 3-Bet statistic for a player.
    # 
    # Args:
    #     stat_dict (dict): A dictionary containing player statistics.
    #     player (int): The player for whom the statistic is calculated.
    # 
    # Returns:
    #     tuple: A tuple containing various representations of the Fold to 3-Bet statistic.
    #         The tuple includes the statistic value, percentage, labels, and counts.
    #         If an error occurs during calculation, returns 'NA' values.
    try:
        opp = stat_dict[player]["f3b_opp_0"]
        action = stat_dict[player]["f3b_0"]
        stat = float(action) / opp

        return f"{stat * 100:3.1f}", f"F3B_pf={stat * 100:3.1f}", f"({action}/{opp})", "% fold to 3 bet preflop"
    except Exception:
        return "NA", "F3B_pf=NA", "(0/0)", "% fold to 3 bet preflop"

def f_4bet(stat_dict, player):
    # Calculate and return fold to 4-bet statistics for a player.
    # 
    # Args:
    #     stat_dict (dict): Dictionary containing player statistics.
    #     player (int): Player identifier.
    # 
    # Returns:
    #     tuple: Tuple containing various statistics related to fold to 4-bet.
    try:
        opp = stat_dict[player]["f4b_opp_0"]
        action = stat_dict[player]["f4b_0"]
        stat = float(action) / opp

        return f"{stat * 100:3.1f}", f"F4B_pf={stat * 100:3.1f}", f"({action}/{opp})", "% fold to 4 bet preflop"
    except Exception:
        return "NA", "F4B_pf=NA", "(0/0)", "% fold to 4 bet preflop"

def cb1(stat_dict, player):
    # Calculate the continuation bet statistic for a given player on flop.
    # 
    # Args:
    #     stat_dict (dict): A dictionary containing player statistics.
    #     player (int): The player for whom the statistic is calculated.
    # 
    # Returns:
    #     tuple: A tuple containing various formatted strings representing the continuation bet statistic.
    try:
        opp = stat_dict[player]["cb_opp_1"]
        action = stat_dict[player]["cb_1"]
        stat = float(action) / opp

        return f"{stat * 100:3.1f}", f"cb_1={stat * 100:3.1f}", f"({action}/{opp})", "% continuation bet flop"
    except Exception:
        return "NA", "cb_1=NA", "(0/0)", "% continuation bet flop"

def cb2(stat_dict, player):
    # Calculate the continuation bet statistic for a given player on turn.
    # 
    # Args:
    #     stat_dict (dict): A dictionary containing player statistics.
    #     player (int): The player for whom the statistic is calculated.
    # 
    # Returns:
    #     tuple: A tuple containing various formatted strings representing the continuation bet statistic.
    try:
        opp = stat_dict[player]["cb_opp_2"]
        action = stat_dict[player]["cb_2"]
        stat = float(action) / opp

        return f"{stat * 100:3.1f}", f"cb_2={stat * 100:3.1f}", f"({action}/{opp})", "% continuation bet turn"
    except Exception:
        return "NA", "cb_2=NA", "(0/0)", "% continuation bet turn"

def cb3(stat_dict, player):
    # Calculate the continuation bet statistic for a given player on river.
    # 
    # Args:
    #     stat_dict (dict): A dictionary containing player statistics.
    #     player (int): The player for whom the statistic is calculated.
    # 
    # Returns:
    #     tuple: A tuple containing various formatted strings representing the continuation bet statistic.
    try:
        opp = stat_dict[player]["cb_opp_3"]
        action = stat_dict[player]["cb_3"]
        stat = float(action) / opp

        return f"{stat * 100:3.1f}", f"cb_3={stat * 100:3.1f}", f"({action}/{opp})", "% continuation bet river"
    except Exception:
        return "NA", "cb_3=NA", "(0/0)", "% continuation bet river"

def ffreq1(stat_dict, player):
    # Calculate the fold frequency statistic for a given player on the flop.
    # 
    # Args:
    #     stat_dict (dict): A dictionary containing player statistics.
    #     player (int): The player for whom the statistic is calculated.
    # 
    # Returns:
    #     tuple: A tuple containing various formatted strings representing the fold frequency statistic.
    try:
        opp = stat_dict[player]["was_raised_1"]
        action = stat_dict[player]["f_freq_1"]
        stat = float(action) / opp

        return f"{stat * 100:3.1f}", f"ff_1={stat * 100:3.1f}", f"({action}/{opp})", "% fold frequency flop"
    except Exception:
        return "NA", "ff_1=NA", "(0/0)", "% fold frequency flop"

def ffreq2(stat_dict, player):
    # Calculate the fold frequency statistic for a given player on the turn.
    # 
    # Args:
    #     stat_dict (dict): A dictionary containing player statistics.
    #     player (int): The player for whom the statistic is calculated.
    # 
    # Returns:
    #     tuple: A tuple containing various formatted strings representing the fold frequency statistic.
    try:
        opp = stat_dict[player]["was_raised_2"]
        action = stat_dict[player]["f_freq_2"]
        stat = float(action) / opp

        return f"{stat * 100:3.1f}", f"ff_2={stat * 100:3.1f}", f"({action}/{opp})", "% fold frequency turn"
    except Exception:
        return "NA", "ff_2=NA", "(0/0)", "% fold frequency turn"

def ffreq3(stat_dict, player):
    # Calculate the fold frequency statistic for a given player on the river.
    # 
    # Args:
    #     stat_dict (dict): A dictionary containing player statistics.
    #     player (int): The player for whom the statistic is calculated.
    # 
    # Returns:
    #     tuple: A tuple containing various formatted strings representing the fold frequency statistic.
    try:
        opp = stat_dict[player]["was_raised_3"]
        action = stat_dict[player]["f_freq_3"]
        stat = float(action) / opp

        return f"{stat * 100:3.1f}", f"ff_3={stat * 100:3.1f}", f"({action}/{opp})", "% fold frequency river"
    except Exception:
        return "NA", "ff_3=NA", "(0/0)", "% fold frequency river"

def f_cb1(stat_dict, player):
    # Calculate the fold to continuation bet statistic for a given player on the flop.
    # 
    # Args:
    #     stat_dict (dict): A dictionary containing player statistics.
    #     player (int): The player for whom the statistic is calculated.
    # 
    # Returns:
    #     tuple: A tuple containing various formatted strings representing the fold to continuation bet statistic.
    #           The tuple contains the following elements:
    #           - percent (str): The calculated statistic value formatted as a percentage.
    #           - f_cb_1 (str): The calculated statistic value formatted as a percentage with a specific format.
    #           - count (str): The count of occurrences divided by the count of opponent's continuation bets.
    #           - description (str): A description of the statistic.
    try:
        opp = stat_dict[player]["f_cb_opp_1"]
        action = stat_dict[player]["f_cb_1"]
        stat = float(action) / opp

        return f"{stat * 100:3.1f}", f"f_cb_1={stat * 100:3.1f}", f"({action}/{opp})", "% fold to continuation bet flop"
    except Exception:
        return "NA", "f_cb_1=NA", "(0/0)", "% fold to continuation bet flop"

def f_cb2(stat_dict, player):
    # Calculate the fold to continuation bet statistic for a given player on the turn.
    # 
    # Args:
    #     stat_dict (dict): A dictionary containing player statistics.
    #     player (int): The player for whom the statistic is calculated.
    # 
    # Returns:
    #     tuple: A tuple containing various formatted strings representing the fold to continuation bet statistic.
    #           The tuple contains the following elements:
    #           - stat (float): The calculated statistic value.
    #           - percent (str): The calculated statistic value formatted as a percentage.
    #           - f_cb2 (str): The calculated statistic value formatted as a percentage with a specific format.
    #           - f_cb_2 (str): The calculated statistic value formatted as a percentage with a specific format.
    #           - count (str): The count of occurrences divided by the count of opponent's continuation bets.
    #           - description (str): A description of the statistic.
    try:
        opp = stat_dict[player]["f_cb_opp_2"]
        action = stat_dict[player]["f_cb_2"]
        stat = float(action) / opp

        return f"{stat * 100:3.1f}", f"f_cb_2={stat * 100:3.1f}", f"({action}/{opp})", "% fold to continuation bet turn"
    except Exception:
        return "NA", "f_cb_2=NA", "(0/0)", "% fold to continuation bet turn"

def f_cb3(stat_dict, player):
    # Calculate the fold to continuation bet statistic for a given player on the river.
    # 
    # Args:
    #     stat_dict (dict): A dictionary containing player statistics.
    #     player (int): The player for whom the statistic is calculated.
    # 
    # Returns:
    #     tuple: A tuple containing various formatted strings representing the fold to continuation bet statistic.
    #           The tuple contains the following elements:
    #           - percent (str): The calculated statistic value formatted as a percentage.
    #           - f_cb_3 (str): The calculated statistic value formatted as a percentage with a specific format.
    #           - count (str): The count of occurrences divided by the count of opponent's continuation bets.
    #           - description (str): A description of the statistic.
    try:
        opp = stat_dict[player]["f_cb_opp_3"]
        action = stat_dict[player]["f_cb_3"]
        stat = float(action) / opp

        return f"{stat * 100:3.1f}", f"f_cb_3={stat * 100:3.1f}", f"({action}/{opp})", "% fold to continuation bet river"
    except Exception:
        return "NA", "f_cb_3=NA", "(0/0)", "% fold to continuation bet river"

def cr1(stat_dict, player):
    # Calculate the check-raise flop statistic for a given player.
    # 
    # Args:
    #     stat_dict (dict): A dictionary containing player statistics.
    #     player (int): The player for whom the statistic is calculated.
    # 
    # Returns:
    #     tuple: A tuple containing various formatted strings representing the check-raise flop statistic.
    #           The tuple contains the following elements:
    #           - percent (str): The calculated statistic value formatted as a percentage.
    #           - cr_1 (str): The calculated statistic value formatted with a specific format.
    #           - count (str): The count of occurrences divided by the count of opponent's check-raises.
    #           - description (str): A description of the statistic.
    try:
        opp = stat_dict[player]["cr_opp_1"]
        action = stat_dict[player]["cr_1"]
        stat = float(action) / opp

        return f"{stat * 100:3.1f}", f"cr_1={stat * 100:3.1f}", f"({action}/{opp})", "% check-raise flop"
    except Exception:
        return "NA", "cr_1=NA", "(0/0)", "% check-raise flop"

def cr2(stat_dict, player):
    # Calculates the check-raise turn for a given player.
    # 
    # Args:
    #     stat_dict (dict): A dictionary containing player statistics.
    #     player (int): The player for whom the statistic is calculated.
    # 
    # Returns:
    #     tuple: A tuple containing various formatted strings representing the check-raise to fold ratio.
    #           The tuple contains the following elements:
    #           - percent (str): The calculated statistic value formatted as a percentage.
    #           - cr_2 (str): The calculated statistic value formatted with a specific format.
    #           - count (str): The count of occurrences divided by the count of opponent's check-raises.
    #           - description (str): A description of the statistic.
    try:
        opp = stat_dict[player]["cr_opp_2"]
        action = stat_dict[player]["cr_2"]
        stat = float(action) / opp

        return f"{stat * 100:3.1f}", f"cr_2={stat * 100:3.1f}", f"({action}/{opp})", "% check-raise turn"
    except Exception:
        return "NA", "cr_2=NA", "(0/0)", "% check-raise turn"

def cr3(stat_dict, player):
    # Calculate the river check-raise statistic for a given player.
    # 
    # Args:
    #     stat_dict (dict): A dictionary containing player statistics.
    #     player (int): The player for whom the statistic is calculated.
    # 
    # Returns:
    #     tuple: A tuple containing various formatted strings representing the check-raise to fold ratio.
    #           The tuple contains the following elements:
    #           - percent (str): The calculated statistic value formatted as a percentage.
    #           - cr_3 (str): The calculated statistic value formatted with a specific format.
    #           - count (str): The count of occurrences divided by the count of opponent's check-raises.
    #           - description (str): A description of the statistic.
    try:
        opp = stat_dict[player]["cr_opp_3"]
        action = stat_dict[player]["cr_3"]
        stat = float(action) / opp

        return f"{stat * 100:3.1f}", f"cr_3={stat * 100:3.1f}", f"({action}/{opp})", "% check-raise river"
    except Exception:
        return "NA", "cr_3=NA", "(0/0)", "% check-raise river"

#################################################################################################

STAT_LIST = sorted(dir())
STAT_LIST = [x for x in STAT_LIST if x not in ("do_stat")]
STAT_LIST = [x for x in STAT_LIST if not x.startswith("_")]
