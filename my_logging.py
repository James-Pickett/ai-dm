# Setup logging
import os
import logging

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
