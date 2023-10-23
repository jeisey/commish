# fetch_players.py
from sleeper_wrapper import Players
import json

def save_players_data():
    players = Players()
    all_players = players.get_all_players()
    
    with open('players_data.json', 'w') as f:
        json.dump(all_players, f)

if __name__ == "__main__":
    save_players_data()
