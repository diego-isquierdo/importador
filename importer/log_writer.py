from __future__ import annotations

import csv
from pathlib import Path


def _sanitize_field(value: str, *, max_len: int = 20000) -> str:
    s = "" if value is None else str(value)
    s = s.replace("\r\n", " ").replace("\r", " ").replace("\n", " ")
    if len(s) > max_len:
        s = s[: max_len - 12] + "...[TRUNCADO]"
    return s


def init_log(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Identificador", "Produto", "ID", "URL", "Payload"])


def append_log_line(
    path: Path,
    identificador: str,
    produto: str,
    value: str,
    url: str = "",
    payload: str = "",
) -> None:
    with path.open("a", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(
            [
                _sanitize_field(identificador, max_len=500),
                _sanitize_field(produto, max_len=200),
                _sanitize_field(value),
                _sanitize_field(url, max_len=4000),
                _sanitize_field(payload),
            ]
        )
