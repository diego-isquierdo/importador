from __future__ import annotations

from typing import Any

import httpx

from app.settings import get_settings


SELECT_FIELDS = "id,subject,category,status,ownerTeam,serviceFirstLevel,serviceFirstLevel,actionCount,serviceSecondLevel,serviceFirstLevelId,lastUpdate,lastActionDate"


def _escape_odata_string(s: str) -> str:
    return s.replace("'", "''")


class MovideskQueryClient:
    def __init__(self) -> None:
        s = get_settings()
        self.base_url = s.movidesk_base_url.rstrip("/")
        self.enterprise_token = s.enterprise_token
        self.empresas_token = s.empresas_token
        self.enterprise_workflow_custom_field_id = s.enterprise_workflow_custom_field_id
        self.empresas_workflow_custom_field_id = s.empresas_workflow_custom_field_id

    def _token_and_field(self, platform: str) -> tuple[str, int]:
        if platform == "enterprise":
            return self.enterprise_token, self.enterprise_workflow_custom_field_id
        if platform == "empresas":
            return self.empresas_token, self.empresas_workflow_custom_field_id
        raise ValueError(f"Plataforma inválida: {platform}")

    def search_by_workflow(self, *, platform: str, workflow: str) -> tuple[bool, list[dict[str, Any]], str]:
        token, cf_id = self._token_and_field(platform)
        url = f"{self.base_url}/tickets"

        safe_workflow = _escape_odata_string(workflow.strip())
        filter_expr = f"customFieldValues/any(cf: cf/customFieldId eq {cf_id} and cf/value eq '{safe_workflow}')"

        params = {
            "token": token,
            "$select": SELECT_FIELDS,
            "$filter": filter_expr,
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                resp = client.get(url, params=params)
        except Exception as e:
            return False, [], f"Erro ao chamar API: {e}"

        if 200 <= resp.status_code < 300:
            try:
                data = resp.json()
                if isinstance(data, list):
                    return True, data, ""
                return True, [], "Resposta inesperada da API"
            except Exception:
                return True, [], "Sucesso sem JSON"

        reason = (resp.text or "").strip() or resp.reason_phrase
        return False, [], f"Erro Status Code {resp.status_code} - {reason}"

    def get_ticket_by_id(self, *, platform: str, ticket_id: str) -> tuple[bool, dict[str, Any] | None, str]:
        token, _ = self._token_and_field(platform)
        url = f"{self.base_url}/tickets"
        params = {"token": token, "id": ticket_id}

        try:
            with httpx.Client(timeout=30.0) as client:
                resp = client.get(url, params=params)
        except Exception as e:
            return False, None, f"Erro ao chamar API: {e}"

        if 200 <= resp.status_code < 300:
            try:
                data = resp.json()
                if isinstance(data, list):
                    if not data:
                        return True, None, ""
                    if isinstance(data[0], dict):
                        return True, data[0], ""
                    return True, None, "Resposta inesperada da API"
                if isinstance(data, dict):
                    return True, data, ""
                return True, None, "Resposta inesperada da API"
            except Exception:
                return True, None, "Sucesso sem JSON"

        reason = (resp.text or "").strip() or resp.reason_phrase
        return False, None, f"Erro Status Code {resp.status_code} - {reason}"


def extract_last_action_description(ticket: dict[str, Any]) -> str:
    actions = ticket.get("actions")
    if not isinstance(actions, list) or not actions:
        return ""

    best = None
    best_id = None
    for a in actions:
        if not isinstance(a, dict):
            continue
        a_id = a.get("id")
        try:
            a_id_int = int(a_id)
        except Exception:
            continue
        if best_id is None or a_id_int > best_id:
            best_id = a_id_int
            best = a

    if not isinstance(best, dict):
        return ""

    desc = best.get("description")
    if desc is None:
        return ""
    return str(desc)


def extract_last_actions_descriptions(ticket: dict[str, Any], *, limit: int = 5) -> list[str]:
    actions = ticket.get("actions")
    if not isinstance(actions, list) or not actions:
        return []

    items: list[tuple[int, str]] = []
    for a in actions:
        if not isinstance(a, dict):
            continue
        a_id = a.get("id")
        try:
            a_id_int = int(a_id)
        except Exception:
            continue

        desc = a.get("description")
        if desc is None:
            continue
        desc_str = str(desc)
        if not desc_str.strip():
            continue

        items.append((a_id_int, desc_str))

    items.sort(key=lambda x: x[0], reverse=True)
    return [d for _, d in items[: max(0, int(limit))]]
