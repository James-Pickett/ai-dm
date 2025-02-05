#!/opt/homebrew/Caskroom/miniconda/base/envs/ai-dm/bin/python
import prompts
import logging
import os
import model
import storage
import time
import sys

NARRARATOR_MODEL = "openhermes:7b-mistral-v2.5-q5_1"

# Setup logging
os.makedirs("./game_data", exist_ok=True)
logging.basicConfig(
    filename="./game_data/debug.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Ensure game data directory exists
os.makedirs("./game_data", exist_ok=True)
utterances_file = "./game_data/utterances.json"
scene_summary_file = "./game_data/current_scene_summary.txt"

# Suppress third-party library logs
for logger_name in ["httpx", "requests", "urllib3", "chromadb", "asyncio", "openai", "ollama"]:
    logging.getLogger(logger_name).setLevel(logging.WARNING)

logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx._client").setLevel(logging.WARNING)
logging.getLogger("httpx._transports").setLevel(logging.WARNING)
logging.getLogger("httpx.transport").setLevel(logging.WARNING)

def chat():
    narrator_model = model.OllamaModel(NARRARATOR_MODEL, prompts.NARRATOR_PROMPT)

    logging.info("AI Dungeon Master session started.")
    print("AI Dungeon Master (Type 'exit' to quit)")

    while True:
        user_input = input("You:\n")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            logging.info("Session ended by user.")
            break

        try:
            start_time = time.time()  # Start timing
            response_stream = narrator_model.chat(user_input, storage.get_previous_interactions())

            print("\nDM:\n", end="", flush=True)  # Print without newline, flush buffer
            narrative_response = ""

            for chunk in response_stream:
                text_chunk = chunk.get("message", {}).get("content", "")
                narrative_response += text_chunk
                print(text_chunk, end="", flush=True)  # Stream text as it arrives

            end_time = time.time()  # End timing
            response_time = end_time - start_time  # Calculate duration

            logging.info(f"Response time: {response_time:.2f} seconds")  # Log time
            print("\n")  # Ensure newline at the end of response
        except Exception as e:
            logging.error(f"Model error: {e}")
            narrative_response = "I'm having trouble processing that. Let's continue the adventure!"
            print(narrative_response)

        storage.save_interaction(user_input, narrative_response)

if __name__ == "__main__":
    chat()
