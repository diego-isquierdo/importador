Implemente o gerador de payload Movidesk (linha da planilha -> JSON de POST), obedecendo estritamente o template aprovado.
Leia e entenda o template do json com os comentários está na pasta ../tamplante json/tickets_post_comentado.json

REGRAS DO TEMPLATE (fixos):
- type = 2
- category = "Tarefa"
- urgency = "4. Média"
- status = "Novo"
- justification = null
- serviceFull = ["3. Serviços (uso interno da ProJuris)", "Atividades Internas"]
- serviceFirstLevelId = 207551
- serviceFirstLevel = "Atividades Internas"
- serviceSecondLevel = "3. Serviços (uso interno da ProJuris)"
- createdBy e clients são FIXOS e devem permanecer exatamente como no template.
- actions[0].type = 2
- actions[0].createdBy fixo (igual ao template)

CAMPOS DINÂMICOS:
- subject = valor da coluna "Título"
- createdDate (raiz) = datetime atual no formato: YYYY-MM-DDTHH:MM:SS.fffffff (7 casas) sem timezone
- actions[0].createdDate = mesmo valor de createdDate

DESCRIPTION:
- O campo actions[0].description deve ser preenchido com 1 informação por “linha”, usando <br /> ao invés de \n, exatamente como:
  "WorkFlow: {identificador}<br /><br />"
  "Liberado para Serviços Técnicos: {Habilitada_em}<br />"
  "Cliente novo? {Cliente_novo}<br />"
  "Razão Social: {Razão_social}<br />"
  "Nome Fantasia: {Nome_fantasia}<br />"
  "Contato no cliente: {Contato_cliente} - {Email_cliente}<br /><br />"
  "Módulos: {Modulos}<br /><br />"
  "Servicos: {Servico_mensal}<br />"  ==> substituir "/" por "<br />" dentro de Servico_mensal antes de inserir
  "Serviço Técnico: {Servico_tecnico}<br />"
  "Ativação de Hosting? {Ativação_hosting?}<br />"
  "Tem legal? {Tem_legal?}<br /><br />"
  "Observações:<br />{Observacoes_gerais}"

Importante:
- Não gerar htmlDescription.
- Não adicionar campos extras.
- Se algum valor tiver quebra de linha real, converter também para <br />.
- Escape apenas o necessário (não deve quebrar o JSON).
- Garantir que o JSON final seja serializável (dict).

ENTREGA:
- Criar módulo movidesk/payload_builder.py com função build_ticket_payload(row: dict) -> dict.
- Criar teste unitário que compara o description gerado com expected para uma linha de exemplo (use um dict com valores como no PDWEB05708).
