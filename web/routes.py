from __future__ import annotations

import uuid
from threading import Thread
from pathlib import Path

from flask import Blueprint, jsonify, render_template, request, send_file

from app.settings import get_settings
from importer.import_service import run_import_job
from importer.validator import validate_workbook
from jobs.repo import JobNotFoundError, JobRepo
from jobs.query_repo import QueryJobNotFoundError, QueryJobRepo
from query.service import (
    create_single_query_job,
    run_batch_query_job,
    run_single_query_job,
    validate_batch_workbook,
    fetch_ticket_last_actions_descriptions,
)


bp = Blueprint("web", __name__)


@bp.get("/")
def home():
    return render_template("home.html", active_page="importacao")


@bp.get("/consulta")
def consulta_home():
    return render_template("consulta.html", active_page="consulta")


@bp.post("/upload")
def upload():
    s = get_settings()
    if "file" not in request.files:
        return jsonify({"detail": "Arquivo não enviado"}), 400

    f = request.files["file"]
    if not f.filename:
        return jsonify({"detail": "Arquivo inválido"}), 400

    job_id = str(uuid.uuid4())

    upload_dir = Path(s.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    dst = upload_dir / f"{job_id}.xlsx"
    f.save(dst)

    repo = JobRepo(Path(s.job_dir))
    repo.create(job_id=job_id, xlsx_path=str(dst))
    return jsonify({"job_id": job_id})


@bp.post("/validate")
def validate():
    s = get_settings()
    job_id = request.form.get("job_id", "")
    if not job_id:
        return jsonify({"detail": "job_id é obrigatório"}), 400

    repo = JobRepo(Path(s.job_dir))
    try:
        job = repo.get(job_id)
    except JobNotFoundError as e:
        return jsonify({"detail": str(e)}), 404

    errors = validate_workbook(job.xlsx_path)
    repo.set_validation(job_id, validated=True, validation_errors=errors)
    return jsonify({"ok": True, "errors": errors})


@bp.post("/import")
def start_import():
    s = get_settings()
    job_id = request.form.get("job_id", "")
    if not job_id:
        return jsonify({"detail": "job_id é obrigatório"}), 400

    repo = JobRepo(Path(s.job_dir))
    try:
        job = repo.get(job_id)
    except JobNotFoundError as e:
        return jsonify({"detail": str(e)}), 404

    if not job.validated:
        return jsonify({"detail": "Arquivo ainda não validado"}), 400

    if job.status == "running":
        return jsonify({"ok": True, "job_id": job_id})

    repo.mark_running(job_id)
    Thread(target=run_import_job, args=(job_id,), daemon=True).start()
    return jsonify({"ok": True, "job_id": job_id})


@bp.get("/job/<job_id>")
def job_status(job_id: str):
    s = get_settings()
    repo = JobRepo(Path(s.job_dir))
    try:
        job = repo.get(job_id)
    except JobNotFoundError as e:
        return jsonify({"detail": str(e)}), 404

    return jsonify(job.to_dict())


@bp.get("/download-log/<job_id>")
def download_log(job_id: str):
    s = get_settings()
    repo = JobRepo(Path(s.job_dir))
    try:
        job = repo.get(job_id)
    except JobNotFoundError as e:
        return jsonify({"detail": str(e)}), 404

    if not job.log_path:
        return jsonify({"detail": "Log ainda não gerado"}), 404

    raw_path = Path(job.log_path)
    candidates: list[Path] = []
    if raw_path.is_absolute():
        candidates.append(raw_path)
    else:
        candidates.append((Path.cwd() / raw_path).resolve())
        candidates.append((Path(s.log_dir) / raw_path).resolve())
        candidates.append((Path(s.log_dir) / raw_path.name).resolve())

    path = next((p for p in candidates if p.exists()), None)
    if path is None:
        return jsonify({"detail": "Arquivo de log não encontrado"}), 404

    return send_file(str(path), mimetype="text/csv", as_attachment=True, download_name=path.name)


@bp.post("/consulta/search")
def consulta_search_single():
    workflow = (request.form.get("workflow") or "").strip()
    base = (request.form.get("base") or "").strip()
    if not workflow:
        return jsonify({"detail": "workflow é obrigatório"}), 400
    if base not in ("enterprise", "empresas"):
        return jsonify({"detail": "base é obrigatória"}), 400

    job_id = create_single_query_job(workflow=workflow, base=base)
    Thread(target=run_single_query_job, args=(job_id, workflow, base), daemon=True).start()
    return jsonify({"ok": True, "job_id": job_id})


@bp.post("/consulta/upload")
def consulta_upload_batch():
    s = get_settings()
    if "file" not in request.files:
        return jsonify({"detail": "Arquivo não enviado"}), 400

    f = request.files["file"]
    if not f.filename:
        return jsonify({"detail": "Arquivo inválido"}), 400

    job_id = str(uuid.uuid4())
    upload_dir = Path(s.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    dst = upload_dir / f"query_{job_id}.xlsx"
    f.save(dst)

    repo = QueryJobRepo(Path(s.job_dir))
    repo.create(job_id=job_id, xlsx_path=str(dst))
    return jsonify({"job_id": job_id})


@bp.post("/consulta/validate")
def consulta_validate_batch():
    s = get_settings()
    job_id = (request.form.get("job_id") or "").strip()
    if not job_id:
        return jsonify({"detail": "job_id é obrigatório"}), 400

    repo = QueryJobRepo(Path(s.job_dir))
    try:
        job = repo.get(job_id)
    except QueryJobNotFoundError as e:
        return jsonify({"detail": str(e)}), 404

    if not job.xlsx_path:
        return jsonify({"detail": "Arquivo do job não encontrado"}), 400

    errors = validate_batch_workbook(job.xlsx_path)
    repo.set_validation(job_id, validated=True, validation_errors=errors)
    return jsonify({"ok": True, "errors": errors})


@bp.post("/consulta/run")
def consulta_run_batch():
    s = get_settings()
    job_id = (request.form.get("job_id") or "").strip()
    if not job_id:
        return jsonify({"detail": "job_id é obrigatório"}), 400

    repo = QueryJobRepo(Path(s.job_dir))
    try:
        job = repo.get(job_id)
    except QueryJobNotFoundError as e:
        return jsonify({"detail": str(e)}), 404

    if not job.validated:
        return jsonify({"detail": "Arquivo ainda não validado"}), 400

    if job.status == "running":
        return jsonify({"ok": True, "job_id": job_id})

    if not job.xlsx_path:
        return jsonify({"detail": "Arquivo do job não encontrado"}), 400

    Thread(target=run_batch_query_job, args=(job_id, job.xlsx_path), daemon=True).start()
    return jsonify({"ok": True, "job_id": job_id})


@bp.get("/consulta/job/<job_id>")
def consulta_job_status(job_id: str):
    s = get_settings()
    repo = QueryJobRepo(Path(s.job_dir))
    try:
        job = repo.get(job_id)
    except QueryJobNotFoundError as e:
        return jsonify({"detail": str(e)}), 404

    return jsonify(job.to_dict())


@bp.get("/consulta/ticket-detail")
def consulta_ticket_detail():
    ticket_id = (request.args.get("id") or "").strip()
    platform = (request.args.get("platform") or "").strip()
    if not ticket_id:
        return jsonify({"detail": "id é obrigatório"}), 400
    if platform not in ("enterprise", "empresas"):
        return jsonify({"detail": "platform inválida"}), 400

    ok, descriptions, detail = fetch_ticket_last_actions_descriptions(platform=platform, ticket_id=ticket_id)
    if not ok:
        return jsonify({"detail": detail}), 502

    return jsonify({"ok": True, "descriptions": descriptions})
