from __future__ import annotations

from datetime import datetime
from dataclasses import asdict, dataclass, field
from typing import Any, Literal


JobStatus = Literal["uploaded", "validated", "running", "completed", "failed"]


@dataclass
class JobModel:
    job_id: str
    xlsx_path: str

    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    status: JobStatus = "uploaded"
    validated: bool = False
    validation_errors: list[dict[str, Any]] = field(default_factory=list)

    total: int | None = None
    success: int = 0
    errors_count: int = 0

    import_errors: list[dict[str, Any]] = field(default_factory=list)
    log_path: str | None = None

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "JobModel":
        return JobModel(
            job_id=data["job_id"],
            xlsx_path=data["xlsx_path"],
            created_at=data.get("created_at", datetime.now().isoformat()),
            status=data.get("status", "uploaded"),
            validated=bool(data.get("validated", False)),
            validation_errors=list(data.get("validation_errors", [])),
            total=data.get("total"),
            success=int(data.get("success", 0)),
            errors_count=int(data.get("errors_count", 0)),
            import_errors=list(data.get("import_errors", [])),
            log_path=data.get("log_path"),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
