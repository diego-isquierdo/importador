from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Literal


QueryJobStatus = Literal["uploaded", "validated", "running", "completed", "failed"]


@dataclass
class QueryJobModel:
    job_id: str
    xlsx_path: str | None = None

    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    status: QueryJobStatus = "uploaded"
    validated: bool = False
    validation_errors: list[dict[str, Any]] = field(default_factory=list)

    total: int | None = None
    processed: int = 0
    results: list[dict[str, Any]] = field(default_factory=list)
    line_errors: list[dict[str, Any]] = field(default_factory=list)

    detail: str | None = None

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "QueryJobModel":
        return QueryJobModel(
            job_id=data["job_id"],
            xlsx_path=data.get("xlsx_path"),
            created_at=data.get("created_at", datetime.now().isoformat()),
            status=data.get("status", "uploaded"),
            validated=bool(data.get("validated", False)),
            validation_errors=list(data.get("validation_errors", [])),
            total=data.get("total"),
            processed=int(data.get("processed", 0)),
            results=list(data.get("results", [])),
            line_errors=list(data.get("line_errors", [])),
            detail=data.get("detail"),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
