#!/opt/homebrew/Caskroom/miniconda/base/envs/ai-dm/bin/python
import os
import sys
import time
import threading
import logging
import prompts
import models
import storage

# Model identifiers
NARRATOR_MODEL = "hf.co/DavidAU/L3.2-Rogue-Creative-Instruct-Uncensored-Abliterated-7B-GGUF:Q8_0"
SUMMARIZER_MODEL = "hf.co/DavidAU/L3.2-Rogue-Creative-Instruct-Uncensored-Abliterated-7B-GGUF:Q8_0"
FACTUALIZER_MODEL = "hf.co/DavidAU/L3.2-Rogue-Creative-Instruct-Uncensored-Abliterated-7B-GGUF:Q8_0"

# Setup logging
os.makedirs("./game_data", exist_ok=True)
logging.basicConfig(
    filename="./game_data/debug.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Suppress noisy logs from third-party libraries
for logger_name in [
    "httpx", "requests", "urllib3", "chromadb",
    "asyncio", "openai", "ollama"
]:
    logging.getLogger(logger_name).setLevel(logging.WARNING)

logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx._client").setLevel(logging.WARNING)
logging.getLogger("httpx._transports").setLevel(logging.WARNING)
logging.getLogger("httpx.transport").setLevel(logging.WARNING)


def spinner(stop_event):
    """A simple spinner animation running until stop_event is set."""
    spinner_chars = "|/-\\"
    idx = 0
    while not stop_event.is_set():
        sys.stdout.write(spinner_chars[idx % len(spinner_chars)])
        sys.stdout.flush()
        time.sleep(0.1)
        sys.stdout.write("\b")
        idx += 1


def chat():
    """Main function for running the AI Dungeon Master session."""
    narrator = models.Narrator(NARRATOR_MODEL, prompts.NARRATOR_PROMPT)
    summarizer = models.Summarizer(SUMMARIZER_MODEL, prompts.SUMMARIZER_PROMPT)
    factualizer = models.Factualizer(FACTUALIZER_MODEL, prompts.FACTUALIZER_PROMPT)

    logging.info("AI Dungeon Master session started.")
    print("AI Dungeon Master (Type 'exit' to quit)")

    while True:
        # Get user input
        user_utterance = input("You:\n")
        if user_utterance.lower() in ["exit", "quit"]:
            print("Goodbye!")
            logging.info("Session ended by user.")
            break

        # Retrieve the current scene summary from storage
        current_scene_summary = storage.get_scene_summary()

        # serach for facts in chroma db
        facts = storage.search_chroma_db(user_utterance, current_scene_summary)

        start_time = time.time()

        # Get a streaming response from the narrator model,
        # passing the current scene summary
        response_stream = narrator.chat_stream(
            user_utterance, scene_summary=current_scene_summary, facts=facts
        )

        # Print DM label once
        print("\nDM:\n", end="", flush=True)

        # Initialize a list to store response chunks for saving
        response_chunks = []
        for chunk in response_stream:
            # Determine text chunk from the chunk data
            if isinstance(chunk, dict):
                text_chunk = chunk.get("message", {}).get("content", "")
            else:
                text_chunk = chunk  # In case chunk is already a string

            response_chunks.append(text_chunk)
            # Print each chunk in real-time as it's received
            print(text_chunk, end="", flush=True)

        # Ensure a clean newline after the response
        print()

        # Log response time
        end_time = time.time()
        response_time = end_time - start_time
        logging.info(f"Response time: {response_time:.2f} seconds")

        # Combine chunks into a single narrative response for storage
        narrator_utterance = "".join(response_chunks)

        # Save the interaction for later context
        storage.save_interaction(user_utterance, narrator_utterance)

        # Update Scene Summary with a spinner animation while waiting
        previous_summary = storage.get_scene_summary()

        # Print a new line before starting the spinner
        print()

        # Create an event to control the spinner thread
        stop_spinner = threading.Event()
        spinner_thread = threading.Thread(target=spinner, args=(stop_spinner,))
        spinner_thread.start()

        # Call the summarizer model
        new_summary = summarizer.update_scene_summary(user_utterance, narrator_utterance, previous_summary)

        # Print a new line after the spinner is done to clear the spinner output
        print()

        storage.save_scene_summary(new_summary)
        logging.info("Scene summary updated successfully.")

        # Print a new line before starting the spinner
        print()

        # Call the summarizer model
        new_facts = factualizer.update_facts(narrator_utterance)

        storage.save_text_to_chroma(new_facts)

        # Stop the spinner animation
        stop_spinner.set()
        spinner_thread.join()

        # Print a new line after the spinner is done to clear the spinner output
        print()

        logging.info("Facts updated successfully.")

if __name__ == "__main__":
    chat()
