from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from app.settings import get_settings
from importer.log_writer import append_log_line, init_log
from importer.xlsx_reader import read_xlsx_rows
from jobs.repo import JobRepo
from movidesk.payload_builder import build_ticket_payload
from movidesk.sender import MovideskSender, RateLimiter, resolve_platform


def run_import_job(job_id: str) -> None:
    s = get_settings()
    repo = JobRepo(Path(s.job_dir))
    job = repo.get(job_id)

    sender = MovideskSender()
    limiter = RateLimiter(s.rate_limit_seconds)

    headers, rows = read_xlsx_rows(job.xlsx_path)
    total = len(rows)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = (Path(s.log_dir) / f"import_{job_id}_{timestamp}.csv").resolve()
    init_log(log_path)

    artifacts_dir = (Path(s.log_dir) / f"artifacts_{job_id}_{timestamp}").resolve()
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    success = 0
    errors_count = 0
    import_errors: list[dict[str, Any]] = []

    try:
        for idx, row in enumerate(rows, start=1):
            identificador = "" if row.get("identificador") is None else str(row.get("identificador")).strip()
            produto_val = ""
            if "Tipo_produto" in headers:
                produto_val = "" if row.get("Tipo_produto") is None else str(row.get("Tipo_produto")).strip()
            elif "Produto" in headers:
                produto_val = "" if row.get("Produto") is None else str(row.get("Produto")).strip()

            try:
                if not identificador:
                    errors_count += 1
                    msg = "Identificador vazio"
                    append_log_line(log_path, identificador, produto_val, msg)
                    import_errors.append(
                        {
                            "line": int(row.get("__row_number__", 0) or 0),
                            "column": "identificador",
                            "message": msg,
                        }
                    )
                    continue

                if not produto_val:
                    errors_count += 1
                    col = "Tipo_produto" if "Tipo_produto" in headers else "Produto"
                    msg = f"{col} vazio"
                    append_log_line(log_path, identificador, produto_val, msg)
                    import_errors.append(
                        {
                            "line": int(row.get("__row_number__", 0) or 0),
                            "column": col,
                            "message": msg,
                        }
                    )
                    continue

                try:
                    platform = resolve_platform(produto_val)
                except ValueError as e:
                    errors_count += 1
                    col = "Tipo_produto" if "Tipo_produto" in headers else "Produto"
                    msg = str(e)
                    append_log_line(log_path, identificador, produto_val, msg)
                    import_errors.append(
                        {
                            "line": int(row.get("__row_number__", 0) or 0),
                            "column": col,
                            "message": msg,
                        }
                    )
                    continue

                payload = build_ticket_payload(row, platform=platform)

                limiter.wait(platform)
                ok, result, request_url, response_text = sender.send_ticket(payload, platform)

                if ok:
                    success += 1
                    append_log_line(log_path, identificador, produto_val, result)
                else:
                    errors_count += 1

                    safe_id = "".join(ch for ch in identificador if ch.isalnum() or ch in ("-", "_"))
                    safe_id = safe_id or f"row_{idx}"

                    payload_file = artifacts_dir / f"payload_{safe_id}.json"
                    payload_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

                    response_file = artifacts_dir / f"response_{safe_id}.txt"
                    response_file.write_text(response_text or "", encoding="utf-8")

                    payload_ref = f"payload={payload_file} | response={response_file}"
                    append_log_line(log_path, identificador, produto_val, result, request_url, payload_ref)
                    import_errors.append(
                        {
                            "line": int(row.get("__row_number__", 0) or 0),
                            "column": "API",
                            "message": result,
                        }
                    )

            except Exception as e:
                errors_count += 1
                msg = f"Erro inesperado: {e}"
                append_log_line(log_path, identificador, produto_val, msg)
                import_errors.append(
                    {
                        "line": int(row.get("__row_number__", 0) or 0),
                        "column": "Processamento",
                        "message": msg,
                    }
                )

            if idx % 1 == 0:
                repo.update_progress(
                    job_id,
                    total=total,
                    success=success,
                    errors_count=errors_count,
                    import_errors=import_errors,
                )

        repo.update_progress(job_id, total=total, success=success, errors_count=errors_count, import_errors=import_errors)
        repo.finalize(job_id, status="completed", log_path=str(log_path))

    except Exception:
        repo.finalize(job_id, status="failed", log_path=str(log_path))
        raise
