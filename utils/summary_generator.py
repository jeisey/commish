from espn_api.football import League
from yfpy.query import YahooFantasySportsQuery
from utils import espn_helper, yahoo_helper
import openai
import datetime


# Lateny troubleshooting: https://platform.openai.com/docs/guides/production-best-practices/improving-latencies
def generate_gpt4_summary_streaming(summary, character_choice, trash_talk_level):
    # Construct the instruction for GPT-4 based on user inputs
    instruction = f"You will be provided a summary below containing the most recent weekly stats for a fantasy football league. \
    Create a weekly recap in the style of {character_choice}. You should include trash talk with a level of {trash_talk_level} based on \
    a scale of 1-10 (1 being no trash talk, 10 being excessive trash talk); feel free to make fun of (or praise) team names and performances.\
    Keep your summary under 800 characters. Only respond in character and do not reply with anything other than your recap. Begin by introducing \
    your character. Here is the weekly fantasy summary: {summary}"
    
    # Create the messages array
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": instruction}
    ]
    
    try:
        # Send the messages to OpenAI's GPT-4 for analysis
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", #options: gpt-4, gpt-3.5-turbo
            messages=messages,
            max_tokens=600,  # Control response lnegth
            stream=True
        )
        # Extract and return the GPT-4 generated message
        for chunk in response:
            # Check if 'content' key exists
            if 'content' in chunk.choices[0].delta:
                yield chunk.choices[0].delta['content']
            else:
                print("End of stream or unexpected structure detected.")
                break
    except Exception as e:
        print("Error details:", e)
        return "Failed to get response from GPT-4"

def generate_espn_summary(league, cw):
    """
    Generate a human-friendly summary based on the league stats.
    
    Args:
    - league (League): The league object.
    
    Returns:
    - str: A human-friendly summary.
    """
    # Extracting required data using helper functions
    start_time = datetime.datetime.now()
    top_teams = espn_helper.top_three_teams(league)
    print(f"Time for top_three_teams: {(datetime.datetime.now() - start_time).total_seconds()} seconds")
    
    start_time = datetime.datetime.now()
    top_scorer_week = espn_helper.top_scorer_of_week(league, cw)
    print(f"Time for top_scorer_of_week: {(datetime.datetime.now() - start_time).total_seconds()} seconds")
    
    start_time = datetime.datetime.now()
    worst_scorer_week = espn_helper.worst_scorer_of_week(league, cw)
    print(f"Time for worst_scorer_of_week: {(datetime.datetime.now() - start_time).total_seconds()} seconds")
    
    start_time = datetime.datetime.now()
    top_scorer_szn = espn_helper.top_scorer_of_season(league)
    print(f"Time for top_scorer_of_season: {(datetime.datetime.now() - start_time).total_seconds()} seconds")
    
    start_time = datetime.datetime.now()
    worst_scorer_szn = espn_helper.worst_scorer_of_season(league)
    print(f"Time for worst_scorer_of_season: {(datetime.datetime.now() - start_time).total_seconds()} seconds")
    
    start_time = datetime.datetime.now()
    most_trans = espn_helper.team_with_most_transactions(league)
    print(f"Time for team_with_most_transactions: {(datetime.datetime.now() - start_time).total_seconds()} seconds")
    
    start_time = datetime.datetime.now()
    most_injured = espn_helper.team_with_most_injured_players(league)
    print(f"Time for team_with_most_injured_players: {(datetime.datetime.now() - start_time).total_seconds()} seconds")
    
    start_time = datetime.datetime.now()
    highest_bench = espn_helper.highest_scoring_benched_player(league, cw)
    print(f"Time for highest_scoring_benched_player: {(datetime.datetime.now() - start_time).total_seconds()} seconds")
    
    start_time = datetime.datetime.now()
    lowest_start = espn_helper.lowest_scoring_starting_player(league, cw)
    print(f"Time for lowest_scoring_starting_player: {(datetime.datetime.now() - start_time).total_seconds()} seconds")
    
    start_time = datetime.datetime.now()
    biggest_blowout = espn_helper.biggest_blowout_match(league, cw)
    print(f"Time for biggest_blowout_match: {(datetime.datetime.now() - start_time).total_seconds()} seconds")
    
    start_time = datetime.datetime.now()
    closest_game = espn_helper.closest_game_match(league, cw)
    print(f"Time for closest_game_match: {(datetime.datetime.now() - start_time).total_seconds()} seconds")
    
    start_time = datetime.datetime.now()
    top_scoring_team_Week = espn_helper.highest_scoring_team(league, cw)
    print(f"Time for top_scoring_team_string: {(datetime.datetime.now() - start_time).total_seconds()} seconds")
    
    # Formatting the summary
    summary = f"""
    - Top scoring fantasy team this week: {top_scoring_team_Week} 
    - Top 3 fantasy teams: {espn_helper.clean_team_name(top_teams[0].team_name)}, {espn_helper.clean_team_name(top_teams[1].team_name)}, {espn_helper.clean_team_name(top_teams[2].team_name)}
    - Top scoring NFL player of the week: {top_scorer_week[0].name} with {top_scorer_week[1]} points.
    - Worst scoring NFL player of the week: {worst_scorer_week[0].name} with {worst_scorer_week[1]} points.
    - Top scoring NFL player of the season: {top_scorer_szn[0].name} with {top_scorer_szn[1]} points.
    - Worst scoring NFL player of the season: {worst_scorer_szn[0].name} with {worst_scorer_szn[1]} points.
    - Fantasy Team with the most transactions: {espn_helper.clean_team_name(most_trans[0].team_name)} ({most_trans[1]} transactions)
    - Fantasy Team with the most injured players: {espn_helper.clean_team_name(most_injured[0].team_name)} ({most_injured[1]} players: {', '.join(most_injured[2])})
    - Highest scoring benched player: {highest_bench[0].name} with {highest_bench[0].points} points (Rostered by {espn_helper.clean_team_name(highest_bench[1].team_name)})
    - Lowest scoring starting player of the week: {lowest_start[0].name} with {lowest_start[0].points} points (Rostered by {espn_helper.clean_team_name(lowest_start[1].team_name)})
    - Biggest blowout match of the week: {espn_helper.clean_team_name(biggest_blowout.home_team.team_name)} ({biggest_blowout.home_score} points) vs {espn_helper.clean_team_name(biggest_blowout.away_team.team_name)} ({biggest_blowout.away_score} points)
    - Closest game of the week: {espn_helper.clean_team_name(closest_game.home_team.team_name)} ({closest_game.home_score} points) vs {espn_helper.clean_team_name(closest_game.away_team.team_name)} ({closest_game.away_score} points)
    """
    
    return summary.strip()


def get_espn_league_summary(league_id, espn2, SWID):
    # Fetch data from ESPN Fantasy API and compute statistics   
    start_time_league_connect = datetime.datetime.now() 
    league_id = league_id
    year = 2023
    espn_s2 = espn2
    swid = SWID
    # Initialize league & current week
    try:
        league = League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)
    except Exception as e:
        return str(e), "Error occurred during validation"
    end_time_league_connect = datetime.datetime.now()
    league_connect_duration = (end_time_league_connect - start_time_league_connect).total_seconds()
    cw = league.current_week-1
    # Generate summary
    start_time_summary = datetime.datetime.now()
    summary = generate_espn_summary(league, cw)
    end_time_summary = datetime.datetime.now()
    summary_duration = (end_time_summary - start_time_summary).total_seconds()
    # Generage debugging information, placeholder for now
    debug_info = "Summary: " + summary + " ~~~Timings~~~ " + f"League Connect Duration: {league_connect_duration} seconds " + f"Summary Duration: {summary_duration} seconds "
    return summary, debug_info



def generate_yahoo_summary(league_id, auth_path):
    league_id = league_id
    auth_directory = auth_path
    sc = YahooFantasySportsQuery(
        auth_dir=auth_directory,
        league_id=league_id,
        game_code="nfl"
    )
    mrw = yahoo_helper.get_most_recent_week(sc)
    recap = yahoo_helper.generate_weekly_recap(sc, week=mrw)
    return recap
