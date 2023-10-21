import re
import time
#import datetime

def clean_team_name(name):
    # This regex pattern will match any character outside the regular ASCII range
    cleaned_name = re.sub(r'[^\x00-\x7F]+', '', name)
    return cleaned_name.strip()

# Step 1: Basic Data Extraction

def extract_teams_standings(league):
    """
    Extract all teams and their standings.
    
    Args:
    - league (League): The league object.
    
    Returns:
    - List[Team]: List of teams in order of their standings.
    """
    return league.standings()


def extract_players_weekly_scores(league, week):
    """
    Extract all players and their weekly scores for a given week.
    
    Args:
    - league (League): The league object.
    - week (int): The week number.
    
    Returns:
    - List[BoxScore]: List of box scores containing player scores for the given week.
    """
    return league.box_scores(week)


def extract_recent_activities(league, size=25, msg_type=None):
    """
    Extract all recent league activities.
    
    Args:
    - league (League): The league object.
    - size (int): Number of recent activities to fetch.
    - msg_type (str): Type of message ('FA', 'WAIVER', 'TRADED').
    
    Returns:
    - List[Activity]: List of recent league activities.
    """
    return league.recent_activity(size=size, msg_type=msg_type)


def extract_match_results(league, week):
    """
    Extract match results for a given week.
    
    Args:
    - league (League): The league object.
    - week (int): The week number.
    
    Returns:
    - List[Matchup]: List of matchups for the given week.
    """
    return league.scoreboard(week)

# Step 2: Top/Bottom Stats

def top_three_teams(league):
    """
    Determines the top 3 teams based on standings.
    
    Args:
    - league (League): The league object.
    
    Returns:
    - List[Team]: List of top 3 teams.
    """
    standings = extract_teams_standings(league)
    # Return the top 3 teams from the standings
    return standings[:3]


def top_scorer_of_week(league, week):
    """
    Determines the top scoring player of a given week.
    
    Args:
    - league (League): The league object.
    - week (int): The week number.
    
    Returns:
    - Tuple(Player, float): Top scoring player and their score.
    """
    box_scores = extract_players_weekly_scores(league, week)
    
    max_score = float('-inf')
    top_player = None
    
    for box_score in box_scores:
        # Checking players from both home and away teams
        for player in box_score.home_lineup + box_score.away_lineup:
            if player.points > max_score:
                max_score = player.points
                top_player = player
                
    return top_player, max_score

def worst_scorer_of_week(league, week):
    """
    Determines the worst scoring player of a given week.
    
    Args:
    - league (League): The league object.
    - week (int): The week number.
    
    Returns:
    - Tuple(Player, float): Worst scoring player and their score.
    """
    box_scores = extract_players_weekly_scores(league, week)
    
    min_score = float('inf')
    worst_player = None
    
    for box_score in box_scores:
        # Checking players from both home and away teams
        for player in box_score.home_lineup + box_score.away_lineup:
            # Ignore players in the IR slot
            if player.slot_position == 'IR':
                continue
            if player.points < min_score:
                min_score = player.points
                worst_player = player
                
    return worst_player, min_score



def top_scorer_of_season(league):
    """
    Determines the top scoring player of the season using the total_points attribute.
    
    Args:
    - league (League): The league object.
    
    Returns:
    - Tuple(Player, float): Top scoring player and their score for the season.
    """
    
    max_score = float('-inf')
    top_player = None
    
    # Iterating over all teams in the league
    for team in league.teams:
        # Iterating over each player in the team's roster
        for player in team.roster:
            if player.total_points > max_score:
                max_score = player.total_points
                top_player = player
                
    return top_player, max_score


def worst_scorer_of_season(league):
    """
    Determines the worst scoring player of the season using the total_points attribute.
    
    Args:
    - league (League): The league object.
    
    Returns:
    - Tuple(Player, float): Worst scoring player and their score for the season.
    """
    
    min_score = float('inf')
    worst_player = None
    
    # Iterating over all teams in the league
    for team in league.teams:
        # Iterating over each player in the team's roster
        for player in team.roster:
            if player.total_points < min_score:
                min_score = player.total_points
                worst_player = player
                
    return worst_player, min_score

# Step 3: Team-Specific Stats

# Optimized version of the team_with_most_transactions function
def team_with_most_transactions(league):
    # Extract all recent league activities
    activities = extract_recent_activities(league, size=100)  # Reduced size to fetch recent activities

    # Define a direct mapping for action types
    action_types = {
        "FA ADDED": "Claims",
        "WAIVER ADDED": "Claims",
        "TRADED": "Trades"
    }
    
    # Count transactions for each team
    transaction_counts = {}
    for activity in activities:
        for action in activity.actions:
            team = action[0]
            action_type = action[1]
            if team not in transaction_counts:
                transaction_counts[team] = {"Claims": 0, "Trades": 0}
            
            # Use direct mapping for action types
            if action_type in action_types:
                transaction_counts[team][action_types[action_type]] += 1
    
    # Get team with most combined transactions
    team_with_most_transactions = max(transaction_counts, key=lambda k: transaction_counts[k]["Claims"] + transaction_counts[k]["Trades"])
    
    return team_with_most_transactions, transaction_counts[team_with_most_transactions]["Claims"], transaction_counts[team_with_most_transactions]["Trades"]


def team_with_most_injured_players(league):
    """
    Identify the team currently rostering the most injured players.
    
    Args:
    - league (League): The league object.
    
    Returns:
    - Tuple(Team, int, List[str]): Team with the most injured players, number of injured players, and a list of the injured players' names.
    """
    # Dictionary to keep track of injured player counts for each team
    injured_counts = {}
    
    # Iterate over all teams and count their injured players
    for team in league.teams:
        injured_players = [player.name for player in team.roster if player.injured]
        injured_counts[team] = len(injured_players)
    
    # Get the team with the most injured players
    team_with_most_injured = max(injured_counts, key=injured_counts.get)
    
    return team_with_most_injured, injured_counts[team_with_most_injured], [player.name for player in team_with_most_injured.roster if player.injured]

# Step 4: Player Bench/Starting Stats.

def highest_scoring_benched_player(league, current_week):
    """
    Identify the benched player who scored the most points for a given week and the team that rosters them.
    
    Args:
    - league (League): The league object.
    - current_week (int): The week number.
    
    Returns:
    - Tuple: Player object representing the highest scoring benched player and the Team object representing the team that rosters them.
    """
    box_scores = league.box_scores(current_week)
    benched_highest_player = None
    benched_highest_points = float('-inf')

    for box_score in box_scores:
        for player in box_score.home_lineup + box_score.away_lineup:
            if player.slot_position == 'BE' and player.points > benched_highest_points:
                benched_highest_points = player.points
                benched_highest_player = (player, box_score.home_team if player in box_score.home_lineup else box_score.away_team)

    return benched_highest_player

def lowest_scoring_starting_player(league, current_week):
    """
    Identify the starting player who scored the least points for a given week and the team that rosters them.
    
    Args:
    - league (League): The league object.
    - current_week (int): The week number.
    
    Returns:
    - Tuple: Player object representing the lowest scoring starting player and the Team object representing the team that rosters them.
    """
    box_scores = league.box_scores(current_week)
    current_week_lowest_player = None
    current_week_lowest_points = float('inf')

    for box_score in box_scores:
        for player in box_score.home_lineup + box_score.away_lineup:
            if player.slot_position != 'BE' and player.points < current_week_lowest_points:
                current_week_lowest_points = player.points
                current_week_lowest_player = (player, box_score.home_team if player in box_score.home_lineup else box_score.away_team)

    return current_week_lowest_player

# Step 5: Match Stats

def biggest_blowout_match(league, week):
    """
    Identifies the biggest blowout match of the current week.
    
    Args:
    - league (League): The league object.
    - week (int): The week number.
    
    Returns:
    - BoxScore: Box score of the match with the largest score difference.
    """
    box_scores = league.box_scores(week)
    max_diff = float('-inf')
    blowout_match = None

    for match in box_scores:
        diff = abs(match.home_score - match.away_score)
        if diff > max_diff:
            max_diff = diff
            blowout_match = match

    if blowout_match:
        return blowout_match
        # return f"Box Score({blowout_match.home_team.team_name} ({blowout_match.home_score}) at {blowout_match.away_team.team_name} ({blowout_match.away_score}))"
    return None


def closest_game_match(league, week):
    """
    Identifies the closest game of the current week.
    
    Args:
    - league (League): The league object.
    - week (int): The week number.
    
    Returns:
    - BoxScore: Box score of the match with the smallest score difference.
    """
    box_scores = league.box_scores(week)
    min_diff = float('inf')
    closest_match = None

    for match in box_scores:
        diff = abs(match.home_score - match.away_score)
        if diff < min_diff:
            min_diff = diff
            closest_match = match

    if closest_match:
        # return f"Box Score({closest_match.home_team.team_name} ({closest_match.home_score}) at {closest_match.away_team.team_name} ({closest_match.away_score}))"
        return closest_match
    return None


def highest_scoring_team(league: int, week: int) -> str:
    """
    Returns a formatted string with the top scoring team's name and their score for a given league.
    
    Parameters:
    - league: An instance of the League class and week number
    
    Returns:
    - str: Formatted string "Team Name (Score)"
    """
    # Get the matchups for the specified week
    matchups = league.scoreboard(week)
    
    # Determine the team with the highest score for the week
    max_score = 0
    top_team = None
    for matchup in matchups:
        if matchup.home_score > max_score:
            max_score = matchup.home_score
            top_team = matchup.home_team
        if matchup.away_score > max_score:
            max_score = matchup.away_score
            top_team = matchup.away_team
    
    # Return the team name and score in the desired format
    return f"{top_team.team_name} ({max_score})"





