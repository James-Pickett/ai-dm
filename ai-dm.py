#!/opt/homebrew/Caskroom/miniconda/base/envs/ai-dm/bin/python

import logging
import os

from langchain_ollama import OllamaLLM
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

# Set up local logs directory
logs_dir = "./logs"
os.makedirs(logs_dir, exist_ok=True)

# Configure logging
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

model = "mistral:7b-instruct-v0.3-q4_0"

def build_prompt(conversation_history, new_question):
    """
    Build a prompt that includes the entire conversation history
    plus the latest user question. This is a simple example:
    """
    prompt = "You are a helpful AI assistant. The conversation so far is:\n"

    for entry in conversation_history:
        role = entry["role"]
        content = entry["content"]
        if role == "human":
            prompt += f"Human: {content}\n"
        else:  # role == "ai"
            prompt += f"AI: {content}\n"

    prompt += f"Human: {new_question}"
    return prompt

def main():
    logging.debug("Starting main function")

    # Create the OllamaLLM instance
    llm = OllamaLLM(
        model=model,
        streaming=True,
        callbacks=[StreamingStdOutCallbackHandler()],
    )
    logging.debug(f"{model} OllamaLLM initialized.")

    # Initialize a list to store the conversation history
    conversation_history = []

    print("Continuous interactive session with chat history. Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ")

        if user_input.strip().lower() == "exit":
            print("Exiting. Goodbye!")
            logging.debug("User requested exit. Exiting program.")
            break

        # Build a prompt that contains the entire conversation so far + the new user input
        prompt = build_prompt(conversation_history, user_input)
        logging.debug(f"\n-----[Full Prompt]-----\n\n{prompt}\n\n----- END OF PROMPT -----\n")

        # Invoke the model with the prompt
        response = llm.invoke(prompt)
        logging.debug(f"\n-----[AI Response]-----\n\n{response}\n\n----- END OF AI RESPONSE -----\n")

        # Print a newline after streaming finishes
        print()
        print("-" * 10, "End of Response", "-" * 10, "\n")

        # Update conversation history
        conversation_history.append({"role": "human", "content": user_input})
        conversation_history.append({"role": "ai", "content": response})

    logging.debug("Main function complete.")

if __name__ == "__main__":
    main()
