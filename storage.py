import os
import chromadb
import uuid
import my_logging
import ollama
import re
import unicodedata
import emoji
from collections import deque
import json

GAME_NOTES_PATH = './game_data/game_notes.txt'
VECTOR_DB_PATH = './game_data/vector_db'
VECTOR_DB_COLLECTION_NAME = 'game_data'
VECTOR_DB_LOGGER = logger = my_logging.get_logger(my_logging.Component.VECTOR_DB)

def save_game_notes(notes):
    os.makedirs(os.path.dirname(GAME_NOTES_PATH), exist_ok=True)
    with open(GAME_NOTES_PATH, 'w') as file:
        file.write(notes)

def load_scene_notes():
    if not os.path.exists(GAME_NOTES_PATH):
        return ""

    with open(GAME_NOTES_PATH, 'r') as file:
        return file.read()

def chunksplitter(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines

def sanatize_embedding_text(text):
    orgText = text

    # lower case
    text = text.lower()

    # normalize unicode characters
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')

    # Remove any non-ASCII characters
    text = re.sub(r'[^\x00-\x7F]+', '', text)

    # Remove any punctuation
    text = re.sub(r'[^\w\s]', '', text)

    # Remove any newlines
    text = text.replace('\n', ' ')

    # Remove any tabs
    text = text.replace('\t', ' ')

    # change any emojis to text
    text = emoji.demojize(text)

    # Remove any extra whitespace
    text = re.sub(r'\s+', ' ', text)

    # Remove any leading or trailing whitespace
    text = text.strip()

    return text

def getembedding(chunks, prefix):
    # copy array to avoid modifying the original
    chunks = chunks.copy()

    # iterate over chunks, sanatize them and add prefix
    for i in range(len(chunks)):
        sanatized_chuck = sanatize_embedding_text(chunks[i])
        chunks[i] = prefix + sanatized_chuck

    embeds = ollama.embed(model="nomic-embed-text", input=chunks)
    return embeds.get('embeddings', [])

def save_to_vector_db(text):
    client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
    collection = client.get_or_create_collection(name=VECTOR_DB_COLLECTION_NAME, metadata={"hnsw:space": "cosine"})
    starting_count = collection.count()

    chunks = chunksplitter(text)

    embeddings = getembedding(chunks, "search_document:")
    ids = [str(uuid.uuid4()) for _ in range(len(chunks))]
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=ids
    )

    VECTOR_DB_LOGGER.debug(
        "saving to vector db",
        extra={
            "chunks": chunks,
            "chunk_count": len(chunks),
            "starting_count": starting_count,
            "ending_count": collection.count(),
            "added_count": collection.count() - starting_count,
        }
)

def search_vector_db(query, max_results=10):
    client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
    collection = client.get_or_create_collection(name=VECTOR_DB_COLLECTION_NAME, metadata={"hnsw:space": "cosine"})

    num_indexed = collection.count()
    max_results = min(max_results, num_indexed)

    if max_results == 0:
        return ""

    query_embedding = getembedding([query], "search_query:")
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=max_results,
        include=["documents"]
    )

    # Join the list of documents into a single string separated by newlines
    if results['documents'] and results['documents'][0]:
        returnString = "\n".join(results['documents'][0])
    else:
        returnString = ""

    VECTOR_DB_LOGGER.debug(
        "searching vector db",
        extra={
            "query": query,
            "results": results['documents'],
        }
    )

    return returnString

class TranscriptSaver:
    def __init__(self, component: my_logging.Component, data_dir):
        self.logger = my_logging.get_logger(component)

        # Ensure directory exists
        os.makedirs(data_dir, exist_ok=True)
        self.file_path = os.path.join(data_dir, f"{component}_transcript.json")

        # Initialize in-memory pairs with previously saved pairs
        self.in_memory_pairs = deque(self.load_transcript(), maxlen=50)

    def load_transcript(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []

    def save_to_transcript(self, model_input, model_output):
        self.in_memory_pairs.append((model_input, model_output))

        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(list(self.in_memory_pairs), f, ensure_ascii=False, indent=2)

        self.logger.debug(
            "saving to transcript",
            extra={
                "model_input": model_input,
                "model_output": model_output,
                "file_path": self.file_path,
            }
        )

    def get_last_n_pairs(self, n=10):
        if n > len(self.in_memory_pairs):
            n = len(self.in_memory_pairs)
        return list(self.in_memory_pairs)[:n]
