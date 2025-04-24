from enum import Enum


class ReportStatusType(str, Enum):
    CLASSIFICATION = "classification"
    COMPLETED = "completed"
    GENERATION = "generation"
    LOCALIZATION = "localization"
    PENDING = "pending"
    READ = "read"
    UPDATING = "updating"

    def __str__(self) -> str:
        return str(self.value)
