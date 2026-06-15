"""
Structured JSON Logger for FilaVaga engine.

Formats log records as single-line JSON structures and routes them to stderr.

Author: Kalyel N. Laurindo / Software Engineer
"""

import json
import logging
import sys
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    """
    Custom logging formatter to output single-line JSON structures.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record as a JSON string.
        """
        # Convert timestamp to ISO-8601 UTC format
        timestamp = datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat()
        
        log_data = {
            "timestamp": timestamp,
            "level": record.levelname,
            "message": record.getMessage(),
        }
        
        # Include formatted exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        # Include extra fields if added to the record
        if hasattr(record, "extra"):
            log_data.update(record.extra)  # type: ignore

        return json.dumps(log_data, ensure_ascii=False)


def configure_logging(level: int = logging.INFO) -> None:
    """
    Configure the default FilaVaga logger to output JSON to stderr.
    """
    logger = logging.getLogger("filavaga")
    logger.setLevel(level)
    
    # Remove any existing handlers to prevent duplicates
    if logger.handlers:
        logger.handlers.clear()
        
    # Create stderr handler
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)
    
    # Attach custom JSON formatter
    formatter = JsonFormatter()
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
