from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

from app.settings import get_settings
from importer.xlsx_reader import read_xlsx_rows
from jobs.query_repo import QueryJobRepo
from movidesk.sender import resolve_platform
from query.movidesk_client import MovideskQueryClient, extract_last_action_description, extract_last_actions_descriptions
from query.rate_limit import GlobalRateLimiter


_limiter = GlobalRateLimiter(max_requests=10, per_seconds=60)


def create_single_query_job(*, workflow: str, base: str) -> str:
    job_id = str(uuid.uuid4())
    s = get_settings()
    repo = QueryJobRepo(Path(s.job_dir))
    repo.create(job_id=job_id, xlsx_path=None)
    repo.set_validation(job_id, validated=True, validation_errors=[])
    return job_id


def run_single_query_job(job_id: str, workflow: str, base: str) -> None:
    s = get_settings()
    repo = QueryJobRepo(Path(s.job_dir))
    repo.mark_running(job_id, total=1)

    client = MovideskQueryClient()
    try:
        _limiter.wait()
        ok, tickets, detail = client.search_by_workflow(platform=base, workflow=workflow)
        results: list[dict[str, Any]] = []
        if ok:
            for t in tickets:
                if isinstance(t, dict):
                    t2 = dict(t)
                    t2["platform"] = base
                    t2["workflow"] = workflow
                    results.append(t2)

        repo.update_progress(job_id, processed=1, results=results, line_errors=[], detail=detail, total=1)

        if not ok:
            repo.finalize(job_id, status="failed", detail=detail)
            return

        repo.finalize(job_id, status="completed", detail=None)
    except Exception as e:
        repo.finalize(job_id, status="failed", detail=str(e))


def validate_batch_workbook(path: str) -> list[dict[str, Any]]:
    headers, rows = read_xlsx_rows(path)
    errors: list[dict[str, Any]] = []

    headers_set = set(headers)

    if "workflow" not in headers_set:
        errors.append({"line": 1, "column": "workflow", "message": "Coluna obrigatória ausente"})
    if "Produto" not in headers_set:
        errors.append({"line": 1, "column": "Produto", "message": "Coluna obrigatória ausente"})

    for row in rows:
        line = int(row.get("__row_number__", 0) or 0)
        wf = "" if row.get("workflow") is None else str(row.get("workflow")).strip()
        prod = "" if row.get("Produto") is None else str(row.get("Produto")).strip()

        if not wf:
            errors.append({"line": line, "column": "workflow", "message": "Campo obrigatório vazio"})
        if not prod:
            errors.append({"line": line, "column": "Produto", "message": "Campo obrigatório vazio"})
        else:
            try:
                resolve_platform(prod)
            except ValueError as e:
                errors.append({"line": line, "column": "Produto", "message": str(e)})

    return errors


def run_batch_query_job(job_id: str, xlsx_path: str) -> None:
    s = get_settings()
    repo = QueryJobRepo(Path(s.job_dir))

    headers, rows = read_xlsx_rows(xlsx_path)
    repo.mark_running(job_id, total=len(rows))

    client = MovideskQueryClient()
    results: list[dict[str, Any]] = []
    line_errors: list[dict[str, Any]] = []

    processed = 0
    try:
        for row in rows:
            processed += 1
            line = int(row.get("__row_number__", 0) or 0)
            wf = "" if row.get("workflow") is None else str(row.get("workflow")).strip()
            prod = "" if row.get("Produto") is None else str(row.get("Produto")).strip()

            if not wf:
                line_errors.append({"line": line, "column": "workflow", "message": "Campo obrigatório vazio"})
                repo.update_progress(job_id, processed=processed, results=results, line_errors=line_errors)
                continue

            if not prod:
                line_errors.append({"line": line, "column": "Produto", "message": "Campo obrigatório vazio"})
                repo.update_progress(job_id, processed=processed, results=results, line_errors=line_errors)
                continue

            try:
                platform = resolve_platform(prod)
            except ValueError as e:
                line_errors.append({"line": line, "column": "Produto", "message": str(e)})
                repo.update_progress(job_id, processed=processed, results=results, line_errors=line_errors)
                continue

            _limiter.wait()
            ok, tickets, detail = client.search_by_workflow(platform=platform, workflow=wf)
            if not ok:
                line_errors.append({"line": line, "column": "API", "message": detail})
                repo.update_progress(job_id, processed=processed, results=results, line_errors=line_errors)
                continue

            for t in tickets:
                if isinstance(t, dict):
                    t2 = dict(t)
                    t2["platform"] = platform
                    t2["workflow"] = wf
                    results.append(t2)

            repo.update_progress(job_id, processed=processed, results=results, line_errors=line_errors)

        repo.finalize(job_id, status="completed", detail=None)
    except Exception as e:
        repo.finalize(job_id, status="failed", detail=str(e))


def fetch_ticket_last_actions_descriptions(*, platform: str, ticket_id: str) -> tuple[bool, list[str], str]:
    client = MovideskQueryClient()
    ok, ticket, detail = client.get_ticket_by_id(platform=platform, ticket_id=ticket_id)
    if not ok:
        return False, [], detail
    if ticket is None:
        return True, [], ""

    descriptions = extract_last_actions_descriptions(ticket, limit=5)
    if descriptions:
        return True, descriptions, ""

    single = extract_last_action_description(ticket)
    if single:
        return True, [single], ""

    return True, [], ""


def fetch_ticket_last_action_description(*, platform: str, ticket_id: str) -> tuple[bool, str, str]:
    ok, descriptions, detail = fetch_ticket_last_actions_descriptions(platform=platform, ticket_id=ticket_id)
    if not ok:
        return False, "", detail
    return True, "\n\n---\n\n".join(descriptions), ""
