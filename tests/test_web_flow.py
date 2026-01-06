from __future__ import annotations

from pathlib import Path
import io

from openpyxl import Workbook

from app.main import create_app
from importer.validator import EXPECTED_HEADERS


def _make_valid_xlsx(path: Path):
    wb = Workbook()
    ws = wb.active
    ws.append(EXPECTED_HEADERS)
    ws.append(["x"] * len(EXPECTED_HEADERS))
    ws[2][EXPECTED_HEADERS.index("Produto")].value = "Projuris Enterprise"
    wb.save(path)


def test_validate_enables_send(tmp_path: Path, monkeypatch):
    upload_dir = tmp_path / "uploads"
    job_dir = tmp_path / "jobs"
    log_dir = tmp_path / "logs"

    monkeypatch.setenv("UPLOAD_DIR", str(upload_dir))
    monkeypatch.setenv("JOB_DIR", str(job_dir))
    monkeypatch.setenv("LOG_DIR", str(log_dir))

    app = create_app()
    app.testing = True
    client = app.test_client()

    xlsx = tmp_path / "t.xlsx"
    _make_valid_xlsx(xlsx)

    raw = xlsx.read_bytes()
    data = {
        "file": (io.BytesIO(raw), "t.xlsx"),
    }
    r = client.post("/upload", data=data, content_type="multipart/form-data")
    assert r.status_code == 200
    job_id = r.get_json()["job_id"]

    r2 = client.post("/validate", data={"job_id": job_id})
    assert r2.status_code == 200
    assert r2.get_json()["ok"] is True

    r3 = client.get(f"/job/{job_id}")
    assert r3.status_code == 200
    job = r3.get_json()
    assert job["validated"] is True
    assert job["status"] == "validated"
