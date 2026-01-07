from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any

from app.settings import get_settings


_TEMPLATE: dict[str, Any] = {
    "type": 2,
    "subject": "",
    "category": "Tarefa",
    "urgency": "4. Média",
    "status": "Novo",
    "createdDate": "",
    "justification": None,
    "serviceFull": ["3. Serviços (uso interno da ProJuris)", "Atividades Internas"],
    "serviceFirstLevelId": 207551,
    "serviceFirstLevel": "Atividades Internas",
    "serviceSecondLevel": "3. Serviços (uso interno da ProJuris)",
    "createdBy": {"id": "1592146388", "personType": 1, "profileType": 3},
    "clients": [
        {
            "id": "1592146388",
            "personType": 1,
            "profileType": 3,
            "businessName": "Diego de Mesquita Isquierdo",
            "email": "diego.isquierdo@projuris.com.br",
            "phone": None,
            "isDeleted": False,
            "organization": {
                "id": "1419498004",
                "personType": 2,
                "profileType": 2,
                "businessName": "ProJuris",
                "email": None,
                "phone": None,
            },
            "address": None,
            "complement": None,
            "cep": None,
            "city": None,
            "bairro": None,
            "number": None,
            "reference": None,
        }
    ],
    "actions": [
        {
            "type": 1,
            "description": "",
            "createdDate": "",
            "createdBy": {"id": "1592146388", "personType": 1, "profileType": 3},
        }
    ],
}


def _now_created_date() -> str:
    # 7 casas decimais sem timezone
    base = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
    return base + "0"


def _norm(v: Any) -> str:
    if v is None:
        return ""
    s = str(v)
    return s.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br />")


def build_ticket_payload(row: dict[str, Any], platform: str = "enterprise") -> dict[str, Any]:
    payload = deepcopy(_TEMPLATE)

    s = get_settings()
    if platform == "empresas":
        created_by_id = s.empresas_created_by_id
        client_id = s.empresas_client_id
        client_person_type = s.empresas_client_person_type
        client_profile_type = s.empresas_client_profile_type
        client_business_name = s.empresas_client_business_name
        client_email = s.empresas_client_email
        service_first_level_id = s.empresas_service_first_level_id
        service_first_level = s.empresas_service_first_level
        service_second_level = s.empresas_service_second_level
        service_third_level = s.empresas_service_third_level
        service_full_0 = s.empresas_service_full_0
        service_full_1 = s.empresas_service_full_1
        organization_id = s.empresas_organization_id
        organization_business_name = s.empresas_organization_business_name
    else:
        created_by_id = s.enterprise_created_by_id
        client_id = s.enterprise_client_id
        client_person_type = s.enterprise_client_person_type
        client_profile_type = s.enterprise_client_profile_type
        client_business_name = s.enterprise_client_business_name
        client_email = s.enterprise_client_email
        service_first_level_id = s.enterprise_service_first_level_id
        service_first_level = s.enterprise_service_first_level
        service_second_level = s.enterprise_service_second_level
        service_third_level = s.enterprise_service_third_level
        service_full_0 = s.enterprise_service_full_0
        service_full_1 = s.enterprise_service_full_1
        organization_id = s.enterprise_organization_id
        organization_business_name = s.enterprise_organization_business_name

    payload["createdBy"]["id"] = created_by_id
    payload["clients"][0]["id"] = client_id
    payload["clients"][0]["personType"] = client_person_type
    payload["clients"][0]["profileType"] = client_profile_type
    payload["clients"][0]["businessName"] = client_business_name
    payload["clients"][0]["email"] = client_email
    payload["actions"][0]["createdBy"]["id"] = created_by_id

    payload["clients"][0]["organization"]["id"] = organization_id
    payload["clients"][0]["organization"]["businessName"] = organization_business_name

    payload["serviceFirstLevelId"] = service_first_level_id
    payload["serviceFirstLevel"] = service_first_level
    payload["serviceSecondLevel"] = service_second_level
    if service_third_level:
        payload["serviceThirdLevel"] = service_third_level
    payload["serviceFull"] = [service_full_0, service_full_1]

    created_date = _now_created_date()
    payload["createdDate"] = created_date
    subject = _norm(row.get("Título"))
    identificador = "" if row.get("identificador") is None else str(row.get("identificador")).strip()
    if "PCDE-" in identificador:
        subject = "[CANCELAMENTO] " + subject
    payload["subject"] = subject

    servico_mensal = _norm(row.get("Servico_mensal")).replace("/", "<br />")

    observacoes = row.get("Observacoes_gerais")
    if observacoes is None:
        observacoes = row.get("Descrição_motivo")

    prefix = ""
    atividade = "" if row.get("Atividade") is None else str(row.get("Atividade")).strip()
    if atividade:
        prefix += f"Atividade: {_norm(atividade)}<br />"

    tipo_cancelamento = "" if row.get("Tipo_cancelamento") is None else str(row.get("Tipo_cancelamento")).strip()
    if tipo_cancelamento:
        prefix += f"Tipo de Cancelamento: {_norm(tipo_cancelamento)}<br />"

    description = (
        prefix
        + f"WorkFlow: {_norm(row.get('identificador'))}<br /><br />"
        f"Liberado para Serviços Técnicos: {_norm(row.get('Habilitada_em'))}<br />"
        f"Cliente novo? {_norm(row.get('Cliente_novo'))}<br />"
        f"Razão Social: {_norm(row.get('Razão_social'))}<br />"
        f"Nome Fantasia: {_norm(row.get('Nome_fantasia'))}<br />"
        f"Contato no cliente: {_norm(row.get('Contato_cliente'))} - {_norm(row.get('Email_cliente'))}<br /><br />"
        f"Módulos: {_norm(row.get('Modulos'))}<br /><br />"
        f"Servicos: {servico_mensal}<br />"
        f"Serviço Técnico: {_norm(row.get('Servico_tecnico'))}<br />"
        f"Ativação de Hosting? {_norm(row.get('Ativação_hosting?'))}<br />"
        f"Tem legal? {_norm(row.get('Tem_legal?'))}<br /><br />"
        f"Observações:<br />{_norm(observacoes)}"
    )

    payload["actions"][0]["description"] = description
    payload["actions"][0]["createdDate"] = created_date
    return payload
