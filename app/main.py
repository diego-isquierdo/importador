from __future__ import annotations

import logging
from pathlib import Path

from flask import Flask
from dotenv import load_dotenv

from app.settings import get_settings
from web.routes import bp as web_bp


def _ensure_dirs() -> None:
    s = get_settings()
    for p in (s.upload_dir, s.job_dir, s.log_dir):
        Path(p).mkdir(parents=True, exist_ok=True)


def create_app() -> Flask:
    load_dotenv()
    _ensure_dirs()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

    base_dir = Path(__file__).resolve().parent.parent
    templates_dir = base_dir / "web" / "templates"
    static_dir = base_dir / "web" / "static"

    app = Flask(
        __name__,
        template_folder=str(templates_dir),
        static_folder=str(static_dir),
        static_url_path="/static",
    )

    app.register_blueprint(web_bp)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
