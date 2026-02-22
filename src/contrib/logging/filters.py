"""Filters for the Django logging system."""

import logging


class LoggingNoErrorFilter(logging.Filter):
    """Skip only logs below ERROR (DEBUG, INFO, WARNING)."""

    def filter(self, record: logging.LogRecord) -> bool:
        """True for DEBUG/INFO/WARNING, False for ERROR/CRITICAL."""
        if record.levelno == logging.ERROR:
            return False
        return True
