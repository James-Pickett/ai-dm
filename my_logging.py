# Setup logging
import os
import logging
import json
from collections import deque


class ModelLogger:
    def __init__(self, name, data_dir):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False

        # Create a file handler for log output
        handler = logging.FileHandler(f"./debug/{name}.log")
        formatter = logging.Formatter("")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        # Ensure directory exists
        os.makedirs(data_dir, exist_ok=True)
        self.file_path = os.path.join(data_dir, f"{name}_pairs.json")

        # Initialize in-memory pairs with previously saved pairs
        self.in_memory_pairs = deque(self.load_pairs(), maxlen=10)

    def save_pairs(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(list(self.in_memory_pairs), f, ensure_ascii=False, indent=2)

    def load_pairs(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []

    def log(self, model_input, model_output):
        self.in_memory_pairs.append((model_input, model_output))
        self.logger.debug(f"{model_input}\n\n++++++++++\n")
        self.logger.debug(f"{model_output}\n\n@@@@@@@@@@\n")

        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(list(self.in_memory_pairs), f, ensure_ascii=False, indent=2)

    def get_last_n_pairs(self, n=10):
        if n > len(self.in_memory_pairs):
            n = len(self.in_memory_pairs)
        return list(self.in_memory_pairs)[:n]

def setup():
    os.makedirs("./debug", exist_ok=True)
    logging.basicConfig(
        filename="./debug/debug.log",
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Suppress noisy logs from third-party libraries
    for logger_name in [
        "httpx", "requests", "urllib3", "chromadb",
        "asyncio", "openai", "ollama"
        ]:logging.getLogger(logger_name).setLevel(logging.WARNING)

    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx._client").setLevel(logging.WARNING)
    logging.getLogger("httpx._transports").setLevel(logging.WARNING)
    logging.getLogger("httpx.transport").setLevel(logging.WARNING)
