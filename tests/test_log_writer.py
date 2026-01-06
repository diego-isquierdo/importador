from __future__ import annotations

from pathlib import Path

from importer.log_writer import append_log_line, init_log


def test_log_generation(tmp_path: Path):
    p = tmp_path / "log.csv"
    init_log(p)
    append_log_line(p, "ID1", "Projuris Enterprise", "123")
    append_log_line(p, "ID2", "Projuris Empresas", "Erro Status Code 400 - x", "https://api.example/test", "{\"a\":1}")

    content = p.read_text(encoding="utf-8-sig")
    assert "Identificador;Produto;ID;URL;Payload" in content
    assert "ID1;Projuris Enterprise;123;;" in content
    assert "ID2;Projuris Empresas;Erro Status Code 400 - x;https://api.example/test" in content
