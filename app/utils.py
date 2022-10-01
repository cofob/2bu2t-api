"""Small utilities used across all project."""

from time import time


def int_time() -> int:
    """Get `time()`, but as integer, not float.

    Returns:
        int: Current timestamp.
    """
    return int(time())
