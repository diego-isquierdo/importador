from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Protocol

import httpx

from app.settings import get_settings


class TicketSender(Protocol):
    def send_ticket(self, payload: dict[str, Any], platform: str) -> tuple[bool, str, str, str]:
        ...


TOKENS = {
    "empresas": "e04c1f7e-f477-480b-8803-e2766624761e",
    "enterprise": "63d11b3a-b64a-48ac-8ab1-62fc12ebcb90",
}


def resolve_platform(produto: Any) -> str:
    raw = "" if produto is None else str(produto)
    p = " ".join(raw.strip().split()).lower()
    if not p:
        raise ValueError("Produto vazio")

    has_enterprise = "enterprise" in p
    has_empresas = ("empresa" in p) or ("empresas" in p)

    if has_enterprise and has_empresas:
        raise ValueError(f"Produto ambíguo: {raw.strip()}")
    if has_empresas:
        return "empresas"
    if has_enterprise:
        return "enterprise"

    raise ValueError(f"Produto inválido: {raw.strip()}")


def resolve_token(platform: str) -> str:
    if platform not in TOKENS:
        raise ValueError(f"Plataforma inválida: {platform}")
    return TOKENS[platform]


@dataclass
class RateLimiter:
    min_interval_seconds: int
    last_sent_at: dict[str, float]

    def __init__(self, min_interval_seconds: int):
        self.min_interval_seconds = int(min_interval_seconds)
        self.last_sent_at = {}

    def wait(self, platform: str) -> None:
        now = time.monotonic()
        last = self.last_sent_at.get(platform)
        if last is None:
            self.last_sent_at[platform] = now
            return

        elapsed = now - last
        if elapsed < self.min_interval_seconds:
            time.sleep(self.min_interval_seconds - elapsed)

        self.last_sent_at[platform] = time.monotonic()


class MovideskSender:
    def __init__(self) -> None:
        self.base_url = get_settings().movidesk_base_url.rstrip("/")

    def send_ticket(self, payload: dict[str, Any], platform: str) -> tuple[bool, str, str, str]:
        token = resolve_token(platform)
        url = f"{self.base_url}/tickets"
        params = {"token": token}

        request_url = str(httpx.URL(url, params=params))

        try:
            with httpx.Client(timeout=30.0) as client:
                resp = client.post(url, params=params, json=payload)
        except Exception as e:
            return False, f"Erro ao chamar API: {e}", request_url, ""

        if 200 <= resp.status_code < 300:
            try:
                data = resp.json()
                ticket_id = data.get("id")
                if ticket_id is None:
                    return True, "(sem id no retorno)", request_url, resp.text
                return True, str(ticket_id), request_url, resp.text
            except Exception:
                return True, "(sucesso sem JSON)", request_url, resp.text

        try:
            body = resp.text
        except Exception:
            body = ""

        reason = body.strip() or resp.reason_phrase
        return False, f"Erro Status Code {resp.status_code} - {reason}", request_url, resp.text
