import os
import logging
import json
from enum import Enum

class Component(Enum):
    VECTOR_DB = "vector_db"
    GAME_MASTER_RAW = "game_master_raw"
    GAME_MASTER = "game_master"
    NOTE_TAKER_RAW = "note_taker_raw"

class JSONFormatter(logging.Formatter):
    """Custom JSON log formatter that dynamically includes all extra key-value pairs."""

    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "filename": record.filename,
            "lineno": record.lineno
        }

        for key in record.__dict__.keys():
            if key not in log_record and not key.startswith('_'):
                log_record[key] = getattr(record, key, None)

        return json.dumps(log_record, ensure_ascii=False)

os.makedirs("./debug", exist_ok=True)
LOG_FILE_PATH = "./debug/log.json"
file_handler = logging.FileHandler(LOG_FILE_PATH, mode="a", encoding="utf-8")
file_handler.setFormatter(JSONFormatter())

class ContextAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        extra = {**self.extra, **kwargs.pop("extra", {})}
        return msg, {"extra": extra}

def get_logger(component: Component, level=logging.DEBUG):
    if not isinstance(component, Component):
        raise ValueError(f"invalid component, must be one of: {[c.value for c in Component]}")

    logger_name = component.value
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    if not logger.handlers:
        logger.addHandler(file_handler)

    return ContextAdapter(logger, {"component": component.value})
