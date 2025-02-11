import os
import json
import logging
import uuid
from types import GeneratorType  # For checking generators
import chromadb  # ChromaDB client

# Ensure game data directory exists
os.makedirs("./game_data", exist_ok=True)

# File paths for local storage
INTERACTIONS_FILE = "./game_data/interactions.json"
SCENE_SUMMARY_FILE = "./game_data/current_scene_summary.txt"

# Initialize ChromaDB persistent storage
CHROMA_DB_PATH = "./game_data/chroma_db"
try:
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    # Use (or create) a collection named "game_data"
    collection = client.get_or_create_collection(name="game_data")
except Exception as e:
    logging.error(f"Failed to initialize ChromaDB: {e}")
    collection = None  # In case ChromaDB is not available

def save_text_to_chroma(text):
    # Generate a unique document ID internally.
    doc_id = str(uuid.uuid4())

    collection.add(
        documents=[text],
        ids=[doc_id]
    )

    logging.debug(f"texted saved to chroma db: {text}")

def search_chroma_db(user_utterance, scene_summary, n_results=5):
    try:
        if not collection:
            logging.error("ChromaDB collection is not initialized.")
            return []
        # The query_texts parameter is used here. This assumes an embedding function has been provided,
        # which is required for similarity search. Without it, the query may not work as expected.
        results = collection.query(query_texts=[user_utterance, scene_summary], n_results=n_results)
        return results
    except Exception as e:
        logging.error(f"Failed to search ChromaDB: {e}")
        return []

def save_interaction(user_input, assistant_response):
    if os.path.exists(INTERACTIONS_FILE):
        with open(INTERACTIONS_FILE, "r", encoding="utf-8") as f:
            interactions = json.load(f)
    else:
        interactions = []

    interactions.append({"user": user_input, "assistant": assistant_response})

    with open(INTERACTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(interactions, f, indent=4)

def get_previous_interactions():
    if os.path.exists(INTERACTIONS_FILE):
        with open(INTERACTIONS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data[-10:]  # Return the last 10 interactions
    return []

def save_scene_summary(summary):
    try:
        # Ensure summary is a string
        if isinstance(summary, GeneratorType):
            summary = "".join(summary)

        if hasattr(summary, "message") and isinstance(summary.message, dict):
            summary = summary.message.get("content", "")

        if not isinstance(summary, str):
            summary = str(summary)

        # ---- Save to file ----
        os.makedirs(os.path.dirname(SCENE_SUMMARY_FILE), exist_ok=True)
        with open(SCENE_SUMMARY_FILE, "w", encoding="utf-8") as f:
            f.write(summary)

        # Removed saving to ChromaDB for scene summaries.
    except Exception as e:
        logging.error(f"Failed to save scene summary: {e}")

def get_scene_summary():
    if not os.path.exists(SCENE_SUMMARY_FILE):
        return ""

    try:
        with open(SCENE_SUMMARY_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        logging.error(f"Failed to read scene summary: {e}")
        return ""
