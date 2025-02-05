import os
import json
import logging

# Ensure game data directory exists
os.makedirs("./game_data", exist_ok=True)

INTERACTIONS_FILE = "./game_data/interactions.json"

def save_interaction(user_input, assistant_response):
    """ Saves the latest interaction to a file """
    if os.path.exists(INTERACTIONS_FILE):
        with open(INTERACTIONS_FILE, "r", encoding="utf-8") as f:
            interactions = json.load(f)
    else:
        interactions = []

    interactions.append({"user": user_input, "assistant": assistant_response})

    with open(INTERACTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(interactions, f, indent=4)

def get_previous_interactions():
    """ Retrieves last N utterances for better model context """
    if os.path.exists(INTERACTIONS_FILE):
        with open(INTERACTIONS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data[-10:]  # Get last 5 utterances for context
    return []
