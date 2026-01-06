from __future__ import annotations

import uuid
from threading import Thread
from pathlib import Path

from flask import Blueprint, jsonify, render_template, request, send_file

from app.settings import get_settings
from importer.import_service import run_import_job
from importer.validator import validate_workbook
from jobs.repo import JobNotFoundError, JobRepo


bp = Blueprint("web", __name__)


@bp.get("/")
def home():
    return render_template("home.html")


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
