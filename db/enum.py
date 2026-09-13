from enum import Enum


class ReportStatus(str, Enum):
    PENDING = "pending"
    ACCEPTANCE = "acceptance"
    REJECTED = "rejected"
    IN_PROGRESS = "in progress"
