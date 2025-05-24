"""Logging configuration."""

import logging
import logging.config
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from config.settings import settings


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ["name", "msg", "args", "created", "filename", "funcName",
                          "levelname", "levelno", "lineno", "module", "exc_info",
                          "exc_text", "stack_info", "pathname", "processName",
                          "process", "threadName", "thread", "taskName"]:
                log_data[key] = value
        
        return json.dumps(log_data)


def setup_logging(level: str = "INFO") -> None:
    """
    Setup logging configuration.
    
    Args:
        level: Logging level
    """
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Logging configuration
    config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": JSONFormatter,
            },
            "standard": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": level,
                "formatter": "standard" if settings.DEBUG else "json",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": level,
                "formatter": "json",
                "filename": log_dir / "plantcare.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf-8",
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "json",
                "filename": log_dir / "errors.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf-8",
            },
        },
        "loggers": {
            "plantcare_agent": {
                "level": level,
                "handlers": ["console", "file", "error_file"],
                "propagate": False,
            },
            "telegram": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "sqlalchemy": {
                "level": "WARNING",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "httpx": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False,
            },
        },
        "root": {
            "level": level,
            "handlers": ["console", "file"],
        },
    }
    
    # Apply configuration
    logging.config.dictConfig(config)
    
    # Log startup
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured with level: {level}")
    logger.info(f"Log files stored in: {log_dir.absolute()}")


def get_logger(name: str) -> logging.Logger:
    """
    Get logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
