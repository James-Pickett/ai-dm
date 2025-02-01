#!/opt/homebrew/Caskroom/miniconda/base/envs/ai-dm/bin/python

from langchain_ollama import OllamaLLM
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

def main():
    # Create an OllamaLLM with streaming enabled
    # Provide the callback in the constructor so we don't run into "multiple values" for callbacks
    llm = OllamaLLM(
        model="mistral:7b-instruct-v0.3-q4_0",  # Replace with the exact model name from `ollama list`
        streaming=True,
        callbacks=[StreamingStdOutCallbackHandler()],
    )

    print("Continuous interactive session. Type 'exit' to quit.\n")
    while True:
        question = input("You: ")
        if question.strip().lower() == "exit":
            print("Exiting. Goodbye!")
            break

        # Invoke the model directly; tokens will stream out as they are generated
        _ = llm.invoke(question)

        # Print a newline after the streaming finishes
        print()
        print("-" * 10, "End of Response", "-" * 10, "\n")

if __name__ == "__main__":
    main()
