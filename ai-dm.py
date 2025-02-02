#!/opt/homebrew/Caskroom/miniconda/base/envs/ai-dm/bin/python

import logging
import os
import json
import time

from langchain_ollama import OllamaLLM
from langchain.callbacks.base import BaseCallbackHandler  # We'll create a custom callback

# ANSI color codes
BLUE = "\033[94m"
RESET = "\033[0m"

# --------------------------------------------------------------------------
# Logging Configuration
# --------------------------------------------------------------------------

logs_dir = "./logs"
os.makedirs(logs_dir, exist_ok=True)

logging.basicConfig(
    filename="logs/debug.log",
    filemode="a",
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] (%(name)s:%(lineno)d) %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Suppress debug logs from httpx and httpcore
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

# --------------------------------------------------------------------------
# Model / Prompt Setup
# --------------------------------------------------------------------------

model = "mistral:7b-instruct-v0.3-q4_0"

def build_prompt(conversation_history, new_question):
    """
    Build a prompt that includes the entire conversation history
    plus the latest user question, instructing the AI to return
    a JSON object with fields "response", "summary", and "tags".

    Note: For AI messages, we only store summary/tags in conversation_history,
    so 'entry["content"]' might look like:
       "Summary: <...>\nTags: <...>"
    """
    prompt = "You are a helpful AI assistant. The conversation so far is:\n\n"

    for entry in conversation_history:
        role = entry["role"]
        content = entry["content"]
        if role == "human":
            prompt += f"Human: {content}\n"
        else:  # role == "ai"
            prompt += f"AI: {content}\n"

    prompt += f"\nHuman: {new_question}\n\n"
    prompt += (
        "Please provide your answer in **valid JSON** with exactly these fields:\n"
        "  \"response\": string,\n"
        "  \"summary\": string,\n"
        "  \"tags\": array of strings.\n\n"
        "Example:\n"
        "{\n"
        "  \"response\": \"Detailed answer here\",\n"
        "  \"summary\": \"Short summary here\",\n"
        "  \"tags\": [\"keyword1\", \"keyword2\"]\n"
        "}\n\n"
        "Do not include any additional text or keys outside of this JSON.\n"
        "The summary should be a summarization of the response and include details\n"
        "It should include details that may be asked about later.\n"
    )
    return prompt

# --------------------------------------------------------------------------
# Custom Callback: Stream Only the "response" Field (in Blue)
# --------------------------------------------------------------------------

class StreamOnlyResponseCallback(BaseCallbackHandler):
    """
    A naive parser that waits for the substring '"response": "'
    and then prints characters (in blue) until the next quote.
    It ignores everything else (including 'summary' or 'tags').
    """

    def __init__(self):
        self.target_str = '"response": "'
        self.target_idx = 0
        self.found_response = False
        self.response_done = False
        self.full_output = []  # Accumulate the entire output for JSON parsing

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """
        Called whenever a new token is streamed from the model.
        We parse it character by character, and stream only the response text in real time.
        """
        self.full_output.append(token)  # store raw tokens for full JSON

        for ch in token:
            if not self.found_response:
                # We're matching '"response": "'
                if ch == self.target_str[self.target_idx]:
                    self.target_idx += 1
                    if self.target_idx == len(self.target_str):
                        self.found_response = True
                        self.response_done = False
                        self.target_idx = 0
                        print(BLUE, end='', flush=True)  # Start printing in blue
                else:
                    # Mismatch: reset the match index
                    if self.target_idx > 0:
                        self.target_idx = 0
                        # Check if the current char might start a new match
                        if ch == self.target_str[0]:
                            self.target_idx = 1
                    else:
                        if ch == self.target_str[0]:
                            self.target_idx = 1
            else:
                # We've found "response": ", print characters until the closing quote
                if not self.response_done:
                    if ch == '"':
                        self.response_done = True
                        print(RESET, flush=True)  # Reset color
                    else:
                        print(ch, end='', flush=True)

    def get_full_response(self) -> str:
        """Return the entire text (in JSON form) as a single string."""
        return "".join(self.full_output)

# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    logging.debug("Starting main function")

    # Create the OllamaLLM instance with our custom callback
    callback = StreamOnlyResponseCallback()
    llm = OllamaLLM(
        model=model,
        streaming=True,
        callbacks=[callback],
    )
    logging.debug(f"{model} OllamaLLM initialized.")

    conversation_history = []
    print("Continuous interactive session. Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ")

        if user_input.strip().lower() == "exit":
            print("Exiting. Goodbye!")
            logging.debug("User requested exit. Exiting program.")
            break

        # Build a prompt containing the full conversation + new user input
        prompt = build_prompt(conversation_history, user_input)
        logging.debug(
            f"\n-----[Full Prompt]-----\n{prompt}\n----- END OF PROMPT -----\n"
        )

        # Measure time before and after model invocation
        start_time = time.time()
        _ = llm.invoke(prompt)
        elapsed = time.time() - start_time

        # After streaming completes, retrieve the full JSON output
        full_json_str = callback.get_full_response()
        logging.debug(
            f"\n-----[AI Raw JSON]-----\n{full_json_str}\n----- END OF AI RAW JSON -----\n"
            f"{elapsed:.2f} seconds\n"
        )

        # ------------------------------------------------------------------
        # Extract just "summary" and "tags" from the JSON, ignoring "response"
        # ------------------------------------------------------------------
        try:
            parsed = json.loads(full_json_str)
            summary = parsed.get("summary", "")
            tags = parsed.get("tags", [])
        except json.JSONDecodeError:
            logging.warning("AI did not return valid JSON or parse failed.")
            summary = "N/A"
            tags = []

        # Add to conversation history
        # Human turn: store full user input
        conversation_history.append({"role": "human", "content": user_input})

        # AI turn: only keep summary and tags in conversation history
        # We'll store them in a single string or you can structure them differently.
        ai_content = f"Summary: {summary}\nTags: {', '.join(tags)}"
        conversation_history.append({"role": "ai", "content": ai_content})

        # Reset the callback for the next user turn
        callback.__init__()

    logging.debug("Main function complete.")

if __name__ == "__main__":
    main()
