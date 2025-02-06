import os
import json
import logging
from types import GeneratorType  # ✅ Import GeneratorType for checking generators

# Ensure game data directory exists
os.makedirs("./game_data", exist_ok=True)

INTERACTIONS_FILE = "./game_data/interactions.json"
SCENE_SUMMARY_FILE = "./game_data/current_scene_summary.txt"

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
            return data[-10:]  # Get last 10 utterances for context
    return []

def save_scene_summary(summary):
    """ Saves the latest scene summary to a text file. Creates file if it doesn't exist. """
    try:
        # Ensure summary is converted to a string
        if isinstance(summary, GeneratorType):
            summary = "".join(summary)  # Convert generator to string

        # If summary is a ChatResponse object, extract text
        if hasattr(summary, "message") and isinstance(summary.message, dict):
            summary = summary.message.get("content", "")

        # If summary is still not a string, force conversion
        if not isinstance(summary, str):
            summary = str(summary)

        # Ensure directory exists
        os.makedirs(os.path.dirname(SCENE_SUMMARY_FILE), exist_ok=True)

        # Write summary to file
        with open(SCENE_SUMMARY_FILE, "w", encoding="utf-8") as f:
            f.write(summary)  # Save the extracted text
    except Exception as e:
        logging.error(f"Failed to save scene summary: {e}")

def get_scene_summary():
    """ Retrieves the last saved scene summary, returning an empty string if the file does not exist. """
    if not os.path.exists(SCENE_SUMMARY_FILE):
        return ""  # Return empty string if file does not exist

    try:
        with open(SCENE_SUMMARY_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        logging.error(f"Failed to read scene summary: {e}")
        return ""
