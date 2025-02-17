# Setup logging
import os
import logging

class MyModelLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False

        # Create a file handler
        handler = logging.FileHandler(f"./debug/{name}.log")
        formatter = logging.Formatter("")
        handler.setFormatter(formatter)

        # Add the handler to the logger
        self.logger.addHandler(handler)

    def log(self, model_input, model_output):
        self.logger.debug(f"{model_input}\n\n++++++++++\n")
        self.logger.debug(f"{model_output}\n\n@@@@@@@@@@\n")

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
