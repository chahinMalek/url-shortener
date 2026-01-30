from dataclasses import dataclass, field


@dataclass
class ClassificationBatchResult:
    """Result of a batch classification operation."""

    # total number of URLs processed in the batch
    total_processed: int = 0

    # number of URLs classified as safe
    safe_count: int = 0

    # number of URLs classified as malicious
    malicious_count: int = 0

    # number of URLs that failed to classify
    error_count: int = 0

    # total processing time in milliseconds
    processing_time_ms: float = 0.0

    # list of errors that occurred during processing
    errors: list[dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "total_processed": self.total_processed,
            "safe_count": self.safe_count,
            "malicious_count": self.malicious_count,
            "error_count": self.error_count,
            "processing_time_ms": self.processing_time_ms,
            "errors": self.errors,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ClassificationBatchResult":
        return cls(
            total_processed=data.get("total_processed", 0),
            safe_count=data.get("safe_count", 0),
            malicious_count=data.get("malicious_count", 0),
            error_count=data.get("error_count", 0),
            processing_time_ms=data.get("processing_time_ms", 0.0),
            errors=data.get("errors", []),
        )

    def add_error(self, short_code: str, error: str) -> None:
        self.errors.append({"short_code": short_code, "error": error})
        self.error_count += 1

    @property
    def success_rate(self) -> float:
        if self.total_processed == 0:
            return 0.0
        successful = self.total_processed - self.error_count
        return (successful / self.total_processed) * 100
