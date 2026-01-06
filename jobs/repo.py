from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jobs.models import JobModel


class JobNotFoundError(Exception):
    pass


class JobRepo:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, job_id: str) -> Path:
        return self.base_dir / f"{job_id}.json"

    def create(self, job_id: str, xlsx_path: str) -> JobModel:
        job = JobModel(job_id=job_id, xlsx_path=xlsx_path)
        self.save(job)
        return job

    def get(self, job_id: str) -> JobModel:
        p = self._path(job_id)
        if not p.exists():
            raise JobNotFoundError(f"Job não encontrado: {job_id}")
        data = json.loads(p.read_text(encoding="utf-8"))
        return JobModel.from_dict(data)

    def save(self, job: JobModel) -> None:
        p = self._path(job.job_id)
        p.write_text(json.dumps(job.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    def set_validation(self, job_id: str, validated: bool, validation_errors: list[dict[str, Any]]):
        job = self.get(job_id)
        job.validated = validated
        job.validation_errors = validation_errors
        job.status = "validated" if validated else "uploaded"
        self.save(job)

    def mark_running(self, job_id: str):
        job = self.get(job_id)
        job.status = "running"
        job.import_errors = []
        job.success = 0
        job.errors_count = 0
        self.save(job)

    def update_progress(
        self,
        job_id: str,
        *,
        total: int,
        success: int,
        errors_count: int,
        import_errors: list[dict[str, Any]] | None = None,
    ) -> None:
        job = self.get(job_id)
        job.total = total
        job.success = success
        job.errors_count = errors_count
        if import_errors is not None:
            job.import_errors = import_errors
        self.save(job)

    def finalize(self, job_id: str, *, status: str, log_path: str | None):
        job = self.get(job_id)
        job.status = status  # type: ignore[assignment]
        job.log_path = log_path
        self.save(job)
