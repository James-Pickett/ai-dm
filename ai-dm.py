#!/opt/homebrew/Caskroom/miniconda/base/envs/ai-dm/bin/python

import logging
import os

from langchain_ollama import OllamaLLM
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

# Set up local logs directory
logs_dir = "./logs"
os.makedirs(logs_dir, exist_ok=True)

# Set your root logger (or script logger) as before
logging.basicConfig(
    filename="logs/debug.log",
    filemode="a",
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] (%(name)s:%(lineno)d) %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Suppress debug logs from httpx and httpcore by setting their log level higher
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

model = "mistral:7b-instruct-v0.3-q4_0"

def main():
    logging.debug("starting main")

    # Create the OllamaLLM instance
    llm = OllamaLLM(
        model=model,
        streaming=True,
        callbacks=[StreamingStdOutCallbackHandler()],
    )
    logging.debug(f"{model} OllamaLLM initialized.")

    print("Continuous interactive session. Type 'exit' to quit.\n")

    while True:
        question = input("You: ")
        logging.debug(f"[Human] {question}")

        if question.strip().lower() == "exit":
            print("Exiting. Goodbye!")
            logging.debug("user requested exit. exiting program.")
            break

        response = llm.invoke(question)
        logging.debug(f"[AI] {response}")

        print()
        print("-" * 10, "End of Response", "-" * 10, "\n")

    logging.debug("main complete")

if __name__ == "__main__":
    main()
