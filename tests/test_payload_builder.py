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


def test_description_builder_steste_model():
    row = {
        "identificador": "STESTE000445",
        "Título": "05/01/2026 - Integração Docusign",
        "Prazo_atv": "07/01/2026 09:30:00",
        "Razão_social": "SANTOS BRASIL PARTICIPAÇÕES S/A",
        "Contato_cliente": "Thalita Pedro",
        "Email_cliente": "thalita.pedro@santosbrasil.com.br",
        "Modulos": "M1",
        "Servico_mensal": "A/B",
        "Ativação_hosting?": "Sim",
        "Iniciador": "Rafael",
        "Data_emissao": "05/01/2026",
    }

    payload = build_ticket_payload(row, platform="enterprise")
    assert payload["subject"].startswith("STESTE ")

    desc = payload["actions"][0]["description"]
    expected = (
        "WorkFlow: STESTE000445<br /><br />"
        "Prazo para Ativação: 07/01/2026 09:30:00<br />"
        "Razão Social: SANTOS BRASIL PARTICIPAÇÕES S/A<br />"
        "Contato no cliente: Thalita Pedro - thalita.pedro@santosbrasil.com.br<br /><br />"
        "Módulos: M1<br /><br />"
        "Servicos: A<br />B<br />"
        "Ativação de Hosting? Sim<br />"
        "Iniciador:<br />Rafael"
    )
    assert desc == expected
