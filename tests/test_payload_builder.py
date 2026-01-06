from __future__ import annotations

from movidesk.payload_builder import build_ticket_payload


def test_description_builder_example_like_pdweb():
    row = {
        "identificador": "PDWEB05708",
        "Habilitada_em": "2025-01-01",
        "Cliente_novo": "Sim",
        "Razão_social": "ACME LTDA",
        "Nome_fantasia": "ACME",
        "Contato_cliente": "João",
        "Email_cliente": "joao@acme.com",
        "Modulos": "M1",
        "Servico_mensal": "A/B",
        "Servico_tecnico": "T1",
        "Ativação_hosting?": "Não",
        "Tem_legal?": "Sim",
        "Observacoes_gerais": "Obs",
        "Título": "Meu título",
    }

    payload = build_ticket_payload(row, platform="enterprise")
    desc = payload["actions"][0]["description"]

    expected = (
        "WorkFlow: PDWEB05708<br /><br />"
        "Liberado para Serviços Técnicos: 2025-01-01<br />"
        "Cliente novo? Sim<br />"
        "Razão Social: ACME LTDA<br />"
        "Nome Fantasia: ACME<br />"
        "Contato no cliente: João - joao@acme.com<br /><br />"
        "Módulos: M1<br /><br />"
        "Servicos: A<br />B<br />"
        "Serviço Técnico: T1<br />"
        "Ativação de Hosting? Não<br />"
        "Tem legal? Sim<br /><br />"
        "Observações:<br />Obs"
    )

    assert desc == expected
