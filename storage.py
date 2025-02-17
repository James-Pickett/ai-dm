import os
import chromadb
import uuid
import logging
import ollama
import re
import unicodedata
import emoji

GAME_NOTES_PATH = './game_data/game_notes.txt'
VECTOR_DB_PATH = './game_data/vector_db'
VECTOR_DB_COLLECTION_NAME = 'game_data'
VECTOR_DB_LOGGER_FILEPATH = './debug/vector_db.log'

vector_db_logger = logging.getLogger("storage")
vector_db_logger.setLevel(logging.DEBUG)
vector_db_logger.propagate = False

os.makedirs(os.path.dirname(VECTOR_DB_LOGGER_FILEPATH), exist_ok=True)
handler = logging.FileHandler(VECTOR_DB_LOGGER_FILEPATH)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
vector_db_logger.addHandler(handler)

def save_game_notes(notes):
    os.makedirs(os.path.dirname(GAME_NOTES_PATH), exist_ok=True)
    with open(GAME_NOTES_PATH, 'w') as file:
        file.write(notes)

def load_game_notes():
    if not os.path.exists(GAME_NOTES_PATH):
        return ""

    with open(GAME_NOTES_PATH, 'r') as file:
        return file.read()

def chunksplitter(text, chunk_size=1000):
    words = re.findall(r'\S+', text)

    chunks = []
    current_chunk = []
    word_count = 0

    for word in words:
        current_chunk.append(word)
        word_count += 1

        if word_count >= chunk_size:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            word_count = 0

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks

def sanatize_embedding_text(text):
    # Remove any non-ASCII characters
    text = re.sub(r'[^\x00-\x7F]+', '', text)

    # Remove any extra whitespace
    text = re.sub(r'\s+', ' ', text)

    # Remove any punctuation
    text = re.sub(r'[^\w\s]', '', text)

    # Remove any leading or trailing whitespace
    text = text.strip()

    # Remove any newlines
    text = text.replace('\n', ' ')

    # Remove any tabs
    text = text.replace('\t', ' ')

    # change any emojis to text
    text = emoji.demojize(text)

    # normalize unicode characters
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')

    # lower case
    text = text.lower()

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

    chunks = chunksplitter(text)
    embeddings = getembedding(chunks, "search_document:")
    ids = [str(uuid.uuid4()) for _ in range(len(chunks))]
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=ids
    )

def search_vector_db(query):
    client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
    collection = client.get_or_create_collection(name=VECTOR_DB_COLLECTION_NAME, metadata={"hnsw:space": "cosine"})

    query_embedding = getembedding([query], "search_query:")
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=10,
        include=["documents"]
    )

    # Join the list of documents into a single string separated by newlines
    if results['documents'] and results['documents'][0]:
        returnString = "\n".join(results['documents'][0])
    else:
        returnString = ""

    vector_db_logger.debug(f"search results from vector db:\n{returnString}")

    return returnString
