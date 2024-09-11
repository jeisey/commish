from sleeper_wrapper import League
import requests


def map_player_to_team(player_id, rosters, users):
    for roster in rosters:
        if player_id in roster['players']:
            owner_id = roster['owner_id']
            for user in users:
                if user['user_id'] == owner_id:
                    return user['display_name']
    return "Unknown Team"

def map_roster_to_team(roster_id, rosters, users):
    for roster in rosters:
        if roster['roster_id'] == roster_id:
            owner_id = roster['owner_id']
            for user in users:
                if user['user_id'] == owner_id:
                    return user['display_name']
    return "Unknown Team"

def highest_scoring_team_of_week(scoreboards):
    highest_score = -1
    highest_scoring_team = None
    
    for matchup, teams in scoreboards.items():
        for team_name, score in teams:
            if score > highest_score:
                highest_score = score
                highest_scoring_team = team_name
                
    return highest_scoring_team, highest_score

def top_3_teams(standings):
    top_3 = sorted(standings, key=lambda x: (-int(x[1]), -int(x[2]), -int(x[3])))[:3]
    return [(team, wins, losses, points) for team, wins, losses, points in top_3]


def load_player_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def highest_scoring_player_of_week(matchups, players_data, user_team_mapping, roster_owner_mapping):
    highest_score = -1
    highest_scoring_player = None
    highest_scoring_player_team = "Unknown Team"
    
    for matchup in matchups:
        roster_id = matchup['roster_id']
        owner_id = roster_owner_mapping.get(roster_id)
        team_name = user_team_mapping.get(owner_id, "Unknown Team")
        
        for player_id, score in matchup['players_points'].items():
            if score > highest_score:
                highest_score = score
                highest_scoring_player = player_id
                highest_scoring_player_team = team_name
                
    if highest_scoring_player and highest_scoring_player in players_data:
        player_name = players_data[highest_scoring_player].get('full_name', 'Unknown Player')
        return player_name, highest_score, highest_scoring_player_team
    else:
        return None, None, "Unknown Team"

def lowest_scoring_starter_of_week(matchups, players_data, user_team_mapping, roster_owner_mapping):
    lowest_score = float('inf')
    lowest_scoring_player = None
    lowest_scoring_player_team = "Unknown Team"
    
    for matchup in matchups:
        roster_id = matchup['roster_id']
        owner_id = roster_owner_mapping.get(roster_id)
        team_name = user_team_mapping.get(owner_id, "Unknown Team")
        
        for player_id in matchup['starters']:
            score = matchup['players_points'].get(player_id, 0)
            if score < lowest_score:
                lowest_score = score
                lowest_scoring_player = player_id
                lowest_scoring_player_team = team_name
                
    if lowest_scoring_player and lowest_scoring_player in players_data:
        player_name = players_data[lowest_scoring_player].get('full_name', 'Unknown Player')
        return player_name, lowest_score, lowest_scoring_player_team
    else:
        return None, None, "Unknown Team"



def highest_scoring_benched_player_of_week(matchups, players_data, user_team_mapping, roster_owner_mapping):
    highest_score = -1
    highest_scoring_player = None
    highest_scoring_player_team = "Unknown Team"
    
    for matchup in matchups:
        roster_id = matchup['roster_id']
        owner_id = roster_owner_mapping.get(roster_id)
        team_name = user_team_mapping.get(owner_id, "Unknown Team")
        
        for player_id, score in matchup['players_points'].items():
            if player_id not in matchup['starters'] and score > highest_score:
                highest_score = score
                highest_scoring_player = player_id
                highest_scoring_player_team = team_name
                
    if highest_scoring_player and highest_scoring_player in players_data:
        player_name = players_data[highest_scoring_player].get('full_name', 'Unknown Player')
        return player_name, highest_score, highest_scoring_player_team
    else:
        return None, None, "Unknown Team"

def biggest_blowout_match_of_week(scoreboards):
    biggest_blowout = -1
    biggest_blowout_match = None
    
    for matchup, teams in scoreboards.items():
        # Ensure there are two teams in the matchup
        if len(teams) < 2:
            continue
        point_diff = abs(teams[0][1] - teams[1][1])
        if point_diff > biggest_blowout:
            biggest_blowout = point_diff
            biggest_blowout_match = (teams[0], teams[1])
    
    # If no blowout match is found, return placeholders
    if biggest_blowout_match is None:
        return ("No match", "No match"), 0

    return biggest_blowout_match, biggest_blowout


def closest_match_of_week(scoreboards):
    smallest_margin = float('inf')
    closest_match = None
    
    for matchup, teams in scoreboards.items():
        # Ensure there are two teams in the matchup
        if len(teams) < 2:
            continue
        point_diff = abs(teams[0][1] - teams[1][1])
        if point_diff < smallest_margin:
            smallest_margin = point_diff
            closest_match = (teams[0], teams[1])
    
    # If no closest match is found, return placeholders
    if closest_match is None:
        return ("No match", "No match"), 0

    return closest_match, smallest_margin


def team_with_most_moves(rosters, user_team_mapping, roster_owner_mapping):
    most_moves = -1
    team_with_most_moves = "Unknown Team"
    
    for roster in rosters:
        owner_id = roster_owner_mapping.get(roster['roster_id'])
        team_name = user_team_mapping.get(owner_id, "Unknown Team")
        total_moves = roster['settings']['total_moves']
        
        if total_moves > most_moves:
            most_moves = total_moves
            team_with_most_moves = team_name
            
    return team_with_most_moves, most_moves


def team_on_hottest_streak(rosters, user_team_mapping, roster_owner_mapping):
    longest_streak = -1
    team_on_hottest_streak = "Unknown Team"
    
    for roster in rosters:
        owner_id = roster_owner_mapping.get(roster['roster_id'])
        team_name = user_team_mapping.get(owner_id, "Unknown Team")
        streak = roster['metadata'].get('streak', '')
        if 'W' in streak:
            current_streak = int(streak.split('W')[0])
        else:
            current_streak = 0
            
        if current_streak > longest_streak:
            longest_streak = current_streak
            team_on_hottest_streak = team_name
            
    return team_on_hottest_streak, longest_streak


def calculate_scoreboards(matchups, user_team_mapping, roster_owner_mapping):
    matchups_dict = {}
    for matchup in matchups:
        roster_id = matchup['roster_id']
        owner_id = roster_owner_mapping.get(roster_id)
        team_name = user_team_mapping.get(owner_id, "Unknown Team")
        total_points = matchup.get('points', 0)
        matchup_id = matchup.get('matchup_id')
        
        if matchup_id not in matchups_dict:
            matchups_dict[matchup_id] = []
        matchups_dict[matchup_id].append((team_name, total_points))
    
    # Sort the matchups by total points in descending order
    for key in matchups_dict:
        matchups_dict[key] = sorted(matchups_dict[key], key=lambda x: -x[1])
    
    return matchups_dict



