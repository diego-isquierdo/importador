from __future__ import annotations

import json
from pathlib import Path

from jobs.query_models import QueryJobModel


class QueryJobNotFoundError(Exception):
    pass


class QueryJobRepo:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, job_id: str) -> Path:
        return self.base_dir / f"query_{job_id}.json"

    def create(self, job_id: str, *, xlsx_path: str | None = None) -> QueryJobModel:
        job = QueryJobModel(job_id=job_id, xlsx_path=xlsx_path)
        self.save(job)
        return job

    def get(self, job_id: str) -> QueryJobModel:
        p = self._path(job_id)
        if not p.exists():
            raise QueryJobNotFoundError(f"Job não encontrado: {job_id}")
        data = json.loads(p.read_text(encoding="utf-8"))
        return QueryJobModel.from_dict(data)

    def save(self, job: QueryJobModel) -> None:
        p = self._path(job.job_id)
        p.write_text(json.dumps(job.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    def set_validation(self, job_id: str, *, validated: bool, validation_errors: list[dict]):
        job = self.get(job_id)
        job.validated = validated
        job.validation_errors = validation_errors
        job.status = "validated" if validated else "uploaded"
        self.save(job)

    def mark_running(self, job_id: str, *, total: int | None = None):
        job = self.get(job_id)
        job.status = "running"
        job.total = total
        job.processed = 0
        job.results = []
        job.line_errors = []
        job.detail = None
        self.save(job)

    def update_progress(
        self,
        job_id: str,
        *,
        processed: int,
        results: list[dict] | None = None,
        line_errors: list[dict] | None = None,
        detail: str | None = None,
        total: int | None = None,
    ) -> None:
        job = self.get(job_id)
        if total is not None:
            job.total = total
        job.processed = processed
        if results is not None:
            job.results = results
        if line_errors is not None:
            job.line_errors = line_errors
        if detail is not None:
            job.detail = detail
        self.save(job)

    def finalize(self, job_id: str, *, status: str, detail: str | None = None):
        job = self.get(job_id)
        job.status = status  # type: ignore[assignment]
        job.detail = detail
        self.save(job)
