from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from importer.xlsx_reader import read_xlsx_rows


EXPECTED_HEADERS: list[str] = [
    "Status",
    "Responsavel",
    "Time/Equipe",
    "identificador",
    "Título",
    "Habilitada_em",
    "Prazo",
    "Iniciador",
    "Cliente_novo",
    "Setor",
    "Produto",
    "Tem_migração",
    "Razão_social",
    "Nome_fantasia",
    "Contato_cliente",
    "Email_cliente",
    "Modulos",
    "Servico_mensal",
    "Servico_tecnico",
    "Gerar_licenca?",
    "Ativação_hosting?",
    "Tem_legal?",
    "Observacoes_gerais",
]

REQUIRED_FIELDS = {
    "Status",
    "Time/Equipe",
    "identificador",
    "Título",
    "Habilitada_em",
    "Prazo",
    "Cliente_novo",
    "Setor",
    "Tem_migração",
    "Razão_social",
    "Nome_fantasia",
    "Contato_cliente",
    "Email_cliente",
    "Modulos",
    "Servico_mensal",
    "Servico_tecnico",
    "Gerar_licenca?",
    "Ativação_hosting?",
    "Tem_legal?",
}

OPTIONAL_FIELDS = {
    "Responsavel",
    "Iniciador",
    "Atividade",
    "Tipo_cancelamento",
}

ALLOWED_PRODUCTS = {"Projuris Enterprise", "Projuris Empresas"}


@dataclass(frozen=True)
class ValidationErrorItem:
    line: int
    column: str
    message: str

    def to_dict(self) -> dict[str, Any]:
        return {"line": self.line, "column": self.column, "message": self.message}


def validate_headers(headers: list[str]) -> list[ValidationErrorItem]:
    errors: list[ValidationErrorItem] = []

    headers_set = set(headers)

    for col in REQUIRED_FIELDS:
        if col not in headers_set:
            errors.append(ValidationErrorItem(line=1, column=col, message="Coluna obrigatória ausente"))

    produto_in = "Produto" in headers_set
    tipo_produto_in = "Tipo_produto" in headers_set
    if produto_in and tipo_produto_in:
        errors.append(
            ValidationErrorItem(
                line=1,
                column="Tipo_produto",
                message='A planilha deve conter apenas "Produto" ou "Tipo_produto" (nunca ambas)',
            )
        )
    if (not produto_in) and (not tipo_produto_in):
        errors.append(ValidationErrorItem(line=1, column="Produto", message="Coluna ausente"))
        errors.append(ValidationErrorItem(line=1, column="Tipo_produto", message="Coluna ausente"))

    obs_in = "Observacoes_gerais" in headers_set
    motivo_in = "Descrição_motivo" in headers_set
    if obs_in and motivo_in:
        errors.append(
            ValidationErrorItem(
                line=1,
                column="Descrição_motivo",
                message='A planilha deve conter apenas "Observacoes_gerais" ou "Descrição_motivo" (nunca ambas)',
            )
        )
    if (not obs_in) and (not motivo_in):
        errors.append(ValidationErrorItem(line=1, column="Observacoes_gerais", message="Coluna ausente"))
        errors.append(ValidationErrorItem(line=1, column="Descrição_motivo", message="Coluna ausente"))

    return errors


def _is_empty(v: Any) -> bool:
    if v is None:
        return True
    if isinstance(v, str):
        return v.strip() == ""
    return str(v).strip() == ""


def validate_rows(headers: list[str], rows: list[dict[str, Any]]) -> list[ValidationErrorItem]:
    errors: list[ValidationErrorItem] = []
    headers_set = set(headers)

    for row in rows:
        line = int(row.get("__row_number__", 0) or 0)
        for field in REQUIRED_FIELDS:
            if field in headers_set and _is_empty(row.get(field)):
                errors.append(ValidationErrorItem(line=line, column=field, message="Campo obrigatório vazio"))

        if "identificador" in headers_set and _is_empty(row.get("identificador")):
            errors.append(ValidationErrorItem(line=line, column="identificador", message="Campo obrigatório vazio"))

        produto_col = None
        if "Tipo_produto" in headers_set:
            produto_col = "Tipo_produto"
        elif "Produto" in headers_set:
            produto_col = "Produto"

        if produto_col is not None:
            produto_str = "" if row.get(produto_col) is None else str(row.get(produto_col)).strip()
            if _is_empty(produto_str):
                errors.append(ValidationErrorItem(line=line, column=produto_col, message="Campo obrigatório vazio"))
            elif produto_str not in ALLOWED_PRODUCTS:
                errors.append(
                    ValidationErrorItem(
                        line=line,
                        column=produto_col,
                        message='Produto inválido (deve ser "Projuris Enterprise" ou "Projuris Empresas")',
                    )
                )

    return errors


def validate_workbook(path: str) -> list[dict[str, Any]]:
    headers, rows = read_xlsx_rows(path)
    errors: list[ValidationErrorItem] = []
    errors.extend(validate_headers(headers))
    errors.extend(validate_rows(headers, rows))
    return [e.to_dict() for e in errors]
