from yfpy.query import YahooFantasySportsQuery
from streamlit.logger import get_logger
LOGGER = get_logger(__name__)

def get_most_recent_week(sc):
    """
    Retrieves the most recently completed week in the fantasy league.
    
    Parameters:
    - sc (object): The YahooFantasySportsQuery object.
    
    Returns:
    - int: The most recently completed week.
    """
    try:
        league_info = sc.get_league_info()
        completed_week = league_info.current_week - 1
        LOGGER.info(f"Most recent week retrieved successfully: {completed_week}")
        return completed_week
    except Exception as e:
        LOGGER.exception("Failed to get the most recent week")
        raise e  # Reraise the exception after logging it


def extract_team_ids(teams):
    """
    Extracts team ids and names from the provided teams data.
    
    Parameters:
    - teams (list): A list of Team instances.
    
    Returns:
    - dict: A dictionary mapping team ids to team names.
    """
    try:
        return {team.team_id: team.name for team in teams}
    except Exception as e:
        LOGGER.exception("Failed to get the most recent week")
        raise e  # Reraise the exception after logging it


def find_extreme_scorers_and_banged_up_team(sc, team_ids, week=3):
    """
    Finds the highest and lowest scoring players of the week, 
    highest-scoring player on the bench, lowest-scoring player that started,
    and the team with the most 'banged up' players.
    
    Parameters:
    - sc (object): The YahooFantasySportsQuery object.
    - team_ids (dict): A dictionary mapping team ids to team names.
    - week (int): The week for which to retrieve player stats.
    
    Returns:
    - tuple: A tuple containing the highest and lowest scoring players,
             highest-scoring player on the bench, lowest-scoring player that started,
             and the team with the most 'banged up' players.
    """
    highest_scorer = None
    lowest_scorer = None
    highest_scorer_bench = None
    lowest_scorer_started = None
    most_banged_up_team = None
    most_banged_up_count = 0
    
    for team_id, team_name in team_ids.items():
        # Get player stats for the team
        players_stats = sc.get_team_roster_player_stats_by_week(team_id, chosen_week=week)
        
        banged_up_count = 0  # Counter for the number of 'banged up' players in the current team
        
        for player in players_stats:
            # Check if this player has the highest score so far
            if (highest_scorer is None) or (player.player_points.total > highest_scorer[0].player_points.total):
                highest_scorer = (player, team_name)
            
            # Check if this player has the lowest score so far
            if (lowest_scorer is None) or (player.player_points.total < lowest_scorer[0].player_points.total):
                lowest_scorer = (player, team_name)
            
            # Check if this player is on the bench and has the highest score among benched players
            if player.selected_position.position == "BN" and \
               (highest_scorer_bench is None or player.player_points.total > highest_scorer_bench[0].player_points.total):
                highest_scorer_bench = (player, team_name)
            
            # Check if this player is started and has the lowest score among started players
            if player.selected_position.position != "BN" and \
               (lowest_scorer_started is None or player.player_points.total < lowest_scorer_started[0].player_points.total):
                lowest_scorer_started = (player, team_name)
            
            # Check if this player is 'banged up'
            if player.status in ["IR", "PUP", "O", "Q"]:
                banged_up_count += 1
        
        # Check if this team has the most 'banged up' players so far
        if banged_up_count > most_banged_up_count:
            most_banged_up_count = banged_up_count
            most_banged_up_team = (team_name, banged_up_count)
    
    return highest_scorer, lowest_scorer, highest_scorer_bench, lowest_scorer_started, most_banged_up_team

def team_with_most_moves(teams):
    """
    Finds and prints the team with the most number of moves.
    
    Parameters:
    - teams (list): A list of Team instances.
    
    Returns:
    - str: A string containing the name of the team with the most moves and the number of moves.
    """
    # Initialize variables to keep track of the team with the most moves
    most_moves = 0
    team_name = ""
    
    # Iterate through the teams
    for team in teams:
        # Check if this team has more moves than the current highest
        if int(team.number_of_moves) > most_moves:
            most_moves = int(team.number_of_moves)
            team_name = team.name
    
    # Return a message with the team name and number of moves
    return f"The team with the greatest number of moves/transactions is {team_name.decode('utf-8')} with {most_moves} moves!"

def analyze_weekly_performance(sc, chosen_week):
    """
    Analyzes the weekly performance of teams and matches in the league.
    
    Parameters:
    - sc (object): The YahooFantasySportsQuery object.
    - chosen_week (int): The week for which to retrieve and analyze data.
    
    Returns:
    - dict: A dictionary containing the analysis results.
    """
    matchups = sc.get_league_matchups_by_week(chosen_week)
    
    highest_scoring_team = None
    biggest_blowout = {"teams": None, "point_diff": 0}
    closest_match = {"teams": None, "point_diff": float('inf')}
    biggest_bust = {"team": None, "point_diff": 0}
    
    for matchup in matchups:
        teams = matchup.teams
        
        # 1. Find the highest-scoring team of the week
        for team in teams:
            if (highest_scoring_team is None) or (team.team_points.total > highest_scoring_team.team_points.total):
                highest_scoring_team = team
        
        # 2. Find the biggest blowout match of the week
        point_diff = round(abs(teams[0].team_points.total - teams[1].team_points.total), 2)
        if point_diff > biggest_blowout["point_diff"]:
            biggest_blowout = {"teams": teams, "point_diff": point_diff}
        
        # 3. Find the closest match of the week
        if point_diff < closest_match["point_diff"]:
            closest_match = {"teams": teams, "point_diff": point_diff}
        
        # 4. Find the biggest bust of the week
        for team in teams:
            projected_diff = round(team.team_projected_points.total - team.team_points.total, 2)
            if projected_diff > biggest_bust["point_diff"]:
                biggest_bust = {"team": team, "point_diff": projected_diff}

    
    # Creating a result dictionary
    result = {
        "highest_scoring_team": {
            "name": highest_scoring_team.name.decode('utf-8'),
            "score": highest_scoring_team.team_points.total
        },
        "biggest_blowout": {
            "team_1_name": biggest_blowout["teams"][0].name.decode('utf-8'),
            "team_1_score": biggest_blowout["teams"][0].team_points.total,
            "team_2_name": biggest_blowout["teams"][1].name.decode('utf-8'),
            "team_2_score": biggest_blowout["teams"][1].team_points.total,
            "point_diff": biggest_blowout["point_diff"]
        },
        "closest_match": {
            "team_1_name": closest_match["teams"][0].name.decode('utf-8'),
            "team_1_score": closest_match["teams"][0].team_points.total,
            "team_2_name": closest_match["teams"][1].name.decode('utf-8'),
            "team_2_score": closest_match["teams"][1].team_points.total,
            "point_diff": closest_match["point_diff"]
        },
        "biggest_bust": {
            "name": biggest_bust["team"].name.decode('utf-8'),
            "point_diff": biggest_bust["point_diff"]
        }
    }

    
    return result


def generate_weekly_recap(sc, week):
    """
    Generates a weekly recap string for the fantasy league.
    
    Parameters:
    - sc (object): The YahooFantasySportsQuery object.
    - week (int): The week for which to generate the recap.
    
    Returns:
    - str: A string containing the weekly recap.
    """
    # Get relevant data
    teams = sc.get_league_teams()
    team_ids = extract_team_ids(teams)
    highest_scorer, lowest_scorer, highest_scorer_bench, lowest_scorer_started, most_banged_up_team = find_extreme_scorers_and_banged_up_team(sc, team_ids, week)
    analysis_result = analyze_weekly_performance(sc, week)
    
    # Generate the recap string
    recap = (
        f"Highest Scoring Team: {analysis_result['highest_scoring_team']['name']} with {analysis_result['highest_scoring_team']['score']} points\n"
        f"Current Standings: {get_top_teams_string(sc)}\n"
        f"Highest Scoring Player: {highest_scorer[0].name.full} (rostered by: {highest_scorer[1].decode('utf-8')}) with {highest_scorer[0].player_points.total} points\n"
        f"Lowest Scoring Player: {lowest_scorer[0].name.full} (rostered by: {lowest_scorer[1].decode('utf-8')}) with {lowest_scorer[0].player_points.total} points\n"
        f"Highest Scoring Player on Bench: {highest_scorer_bench[0].name.full} (rostered by: {highest_scorer_bench[1].decode('utf-8')}) with {highest_scorer_bench[0].player_points.total} points\n"
        f"Lowest Scoring Player that Started: {lowest_scorer_started[0].name.full} (rostered by: {lowest_scorer_started[1].decode('utf-8')}) with {lowest_scorer_started[0].player_points.total} points\n"
        f"Most Banged Up Team: {most_banged_up_team[0].decode('utf-8')} with {most_banged_up_team[1]} injured players\n"
        f"{team_with_most_moves(teams)}\n"
        f"Closest Match: {analysis_result['closest_match']['team_1_name']} ({analysis_result['closest_match']['team_1_score']} points) vs {analysis_result['closest_match']['team_2_name']} ({analysis_result['closest_match']['team_2_score']} points) with a point differential of {analysis_result['closest_match']['point_diff']}\n"
        f"Biggest Blowout Match: {analysis_result['biggest_blowout']['team_1_name']} ({analysis_result['biggest_blowout']['team_1_score']} points) vs {analysis_result['biggest_blowout']['team_2_name']} ({analysis_result['biggest_blowout']['team_2_score']} points) with a point differential of {analysis_result['biggest_blowout']['point_diff']}\n"
        f"Biggest Team Bust: {analysis_result['biggest_bust']['name']} underperformed by {analysis_result['biggest_bust']['point_diff']} points compared to projections"
    )
    
    return recap

# Helper function to get top teams string
def get_top_teams_string(sc):
    standings_data = sc.get_league_standings()
    top_3_teams = sorted(standings_data.teams, key=lambda x: x.team_standings.rank)[:3]
    top_teams_string = ", ".join([f"{team.name.decode('utf-8')} ({ordinal(team.team_standings.rank)} place - {team.team_points.total} points)" for team in top_3_teams])
    return f"{top_teams_string}"

# Helper function to get ordinal string
def ordinal(n):
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"


