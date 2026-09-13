import logging

from attr import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DatabaseException(Exception):
    message: str
    original_error: Exception | None = None

    def __post_init__(self):
        super.__init__(self.message)
