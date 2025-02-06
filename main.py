#!/opt/homebrew/Caskroom/miniconda/base/envs/ai-dm/bin/python
import os
import sys
import time
import threading
import logging
import prompts
import model
import storage

# Model identifiers
NARRATOR_MODEL = "openhermes:7b-mistral-v2.5-fp16"
SCENE_SUMMARIZER_MODEL = "openhermes:7b-mistral-v2.5-fp16"

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
    narrator_model = model.OllamaModel(NARRATOR_MODEL, prompts.NARRATOR_PROMPT)
    summarizer_model = model.OllamaModel(SCENE_SUMMARIZER_MODEL, prompts.SUMMARIZER_PROMPT)

    logging.info("AI Dungeon Master session started.")
    print("AI Dungeon Master (Type 'exit' to quit)")

    while True:
        # Get user input
        user_input = input("You:\n")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            logging.info("Session ended by user.")
            break

        try:
            start_time = time.time()
            # Retrieve the current scene summary from storage
            current_scene_summary = storage.get_scene_summary()

            # Get a streaming response from the narrator model,
            # passing the current scene summary
            response_stream = narrator_model.chat_stream(
                user_input, scene_summary=current_scene_summary
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
            narrative_response = "".join(response_chunks)

        except Exception as e:
            logging.error(f"Model error: {e}")
            narrative_response = (
                "I'm having trouble processing that. Let's continue the adventure!"
            )
            print(narrative_response)

        # Save the interaction for later context
        storage.save_interaction(user_input, narrative_response)

        # Update Scene Summary with a spinner animation while waiting
        try:
            previous_summary = storage.get_scene_summary()
            summary_input = (
                f"Previous Summary:\n{previous_summary}\n\n"
                f"Player Utterance:\n{user_input}\n\n"
                f"Narrator Utterance:\n{narrative_response}"
            )

            # Print a new line before starting the spinner
            print()

            # Create an event to control the spinner thread
            stop_spinner = threading.Event()
            spinner_thread = threading.Thread(target=spinner, args=(stop_spinner,))
            spinner_thread.start()

            # Call the summarizer model
            new_summary = summarizer_model.chat(summary_input)

            # Stop the spinner animation
            stop_spinner.set()
            spinner_thread.join()

            # Print a new line after the spinner is done to clear the spinner output
            print()

            storage.save_scene_summary(new_summary)
            logging.info("Scene summary updated successfully.")
        except Exception as e:
            logging.error(f"Scene summarization error: {e}")

if __name__ == "__main__":
    chat()
