from __future__ import annotations

from importer.validator import EXPECTED_HEADERS, validate_headers, validate_rows


def test_header_missing():
    headers = [h for h in EXPECTED_HEADERS if h != "Status"]
    errs = validate_headers(headers)
    assert errs


def test_invalid_product():
    headers = EXPECTED_HEADERS
    row = {h: "x" for h in headers}
    row["__row_number__"] = 2
    row["Produto"] = "Outro"
    errs = validate_rows(headers, [row])
    assert any(e.column == "Produto" for e in errs)


def test_empty_required_field_strips_spaces():
    headers = EXPECTED_HEADERS
    row = {h: "x" for h in headers}
    row["__row_number__"] = 2
    row["Título"] = "   "
    errs = validate_rows(headers, [row])
    assert any(e.column == "Título" for e in errs)
