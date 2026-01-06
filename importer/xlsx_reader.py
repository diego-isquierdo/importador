from __future__ import annotations

from typing import Any

from openpyxl import load_workbook


def read_xlsx_rows(path: str) -> tuple[list[str], list[dict[str, Any]]]:
    wb = load_workbook(filename=path, data_only=True)
    ws = wb.active

    header_cells = list(ws[1])
    headers = [str(c.value).strip() if c.value is not None else "" for c in header_cells]

    rows: list[dict[str, Any]] = []
    for row_idx, row_cells in enumerate(ws.iter_rows(min_row=2), start=2):
        values = [(c.value if c.value is not None else "") for c in row_cells[: len(headers)]]

        # ignorar linhas totalmente vazias
        if all((str(v).strip() == "") for v in values):
            continue

        row: dict[str, Any] = {}
        for col_idx, header in enumerate(headers):
            row[header] = values[col_idx] if col_idx < len(values) else ""

        row["__row_number__"] = row_idx
        rows.append(row)

    return headers, rows
