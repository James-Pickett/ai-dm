#!/opt/homebrew/Caskroom/miniconda/base/envs/ai-dm/bin/python
import ollama
import prompts  # Corrected import statement
import chromadb
import logging
import os
import json

NARRARATOR_MODEL = "mistral-small:24b-instruct-2501-q4_K_M"
FACT_ORGANIZER_MODEL = "mistral-small:24b-instruct-2501-q4_K_M"
EMBEDDING_MODEL = "nomic-embed-text:latest"

# Setup logging
os.makedirs("./logs", exist_ok=True)
logging.basicConfig(
    filename="./logs/debug.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_json(message, data):
    try:
        logging.debug(f"{message}: {json.dumps(data, indent=4)}")
    except (TypeError, ValueError):
        logging.debug(f"{message}: {str(data)}")

# Suppress third-party library logs (force them to WARNING)
for logger_name in ["httpx", "requests", "urllib3", "chromadb", "asyncio", "openai", "ollama"]:
    logging.getLogger(logger_name).setLevel(logging.WARNING)

# Additional suppression of `httpx` internal transport logs
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx._client").setLevel(logging.WARNING)
logging.getLogger("httpx._transports").setLevel(logging.WARNING)
logging.getLogger("httpx.transport").setLevel(logging.WARNING)

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="fact_organizer_memory")

class OllamaModel:
    def __init__(self, model_name, system_prompt):
        self.model_name = model_name
        self.system_prompt = system_prompt
        logging.debug(f"Initialized OllamaModel with model: {model_name}")

    def chat(self, user_input, context=None):
        logging.debug(f"User input: {user_input}")
        if context:
            logging.debug(f"Retrieved context: {context}")

        # Construct a single JSON object for the model
        message_payload = {
            "system_prompt": self.system_prompt,
            "context": context if context else [],
            "user_input": user_input
        }

        log_json("Sending message to model", message_payload)
        response = ollama.chat(model=self.model_name, messages=[{"role": "system", "content": json.dumps(message_payload)}])
        log_json("Model response", response.message.content)  # Log only the message content
        return response['message']['content']

    def embed_text(self, text):
        logging.debug(f"Generating embedding for text: {text[:100]}...")
        embedding_response = ollama.embeddings(model=EMBEDDING_MODEL, prompt=text)
        return embedding_response["embedding"]

def retrieve_context(user_input):
    logging.debug(f"Retrieving context for user input: {user_input}")
    embedding = ollama.embeddings(model=EMBEDDING_MODEL, prompt=user_input)["embedding"]
    results = collection.query(query_embeddings=[embedding], n_results=10)

    context = []
    if results["documents"]:
        for doc in results["documents"][0]:
            try:
                context.append(json.loads(doc))  # Parse JSON objects from ChromaDB
            except json.JSONDecodeError:
                logging.warning("Failed to parse a document from ChromaDB as JSON, skipping.")

    logging.debug(f"Context retrieved: {context}")
    return context

def chat():
    narrator_model = OllamaModel(NARRARATOR_MODEL, prompts.NARRATOR_PROMPT)
    fact_organizer_model = OllamaModel(FACT_ORGANIZER_MODEL, prompts.FACT_ORGANIZER_PROMPT)

    logging.info("AI Dungeon Master session started.")
    print("AI Dungeon Master (Type 'exit' to quit)")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            logging.info("Session ended by user.")
            break

        context = retrieve_context(user_input)
        narrative_response = narrator_model.chat(user_input, context)
        print(f"AI DM: {narrative_response}\n")

        fact_summary = fact_organizer_model.chat(narrative_response)

        # Attempt to parse fact summary as a JSON list
        try:
            fact_summary = fact_summary.replace("\\", "")
            fact_summary_clean = json.loads(fact_summary)

            # Generate embedding and store clean JSON in ChromaDB
            embedding = fact_organizer_model.embed_text(json.dumps(fact_summary_clean))
            collection.add(
                documents=[json.dumps(fact_summary_clean)],
                embeddings=[embedding],
                ids=[str(hash(json.dumps(fact_summary_clean)))]  # Use hash to generate a unique ID
            )
            logging.info("Clean JSON Fact summary stored in ChromaDB.")
        except json.JSONDecodeError:
            logging.warning("Fact summary could not be parsed as a JSON list. Discarding.")

if __name__ == "__main__":
    chat()
