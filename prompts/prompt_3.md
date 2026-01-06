Implemente o mecanismo de envio para a API Movidesk com arquitetura substituível.

REQUISITOS:
- Criar interface TicketSender com método send_ticket(payload: dict, platform: str) -> result (success/id ou erro).
- Implementar MovideskSender usando httpx.
- Endpoint:
  POST https://api.movidesk.com/public/v1/tickets?token={{token}}
- Token depende do Produto:
  - "ProJuris para Empresas" => O toke a ser utilizado é "e04c1f7e-f477-480b-8803-e2766624761e"
  - "ProJuris Enterprise" => O toke a ser utilizado é "63d11b3a-b64a-48ac-8ab1-62fc12ebcb90"
- Implementar função resolve_platform(row["Produto"]) -> ("empresas"|"enterprise") e resolve_token(platform)->token.

RATE LIMIT:
- Não enviar mais de 10 requests por minuto POR PLATAFORMA.
- Implementar rate limiter simples e confiável:
  - A cada request, garantir intervalo mínimo de 6 segundos (60/10) para aquela plataforma.
  - Se o import processar linhas alternadas de plataformas, manter rate limiter independente.
- Tratar respostas:
  - Sucesso: API retorna um id (no body). Parsear.
  - Erro: capturar status code e mensagem do corpo.

ENTREGA:
- movidesk/sender.py (TicketSender + MovideskSender)
- importer/import_service.py (orquestra envio de uma lista de rows):
  - Para cada row:
    - build payload
    - resolve platform/token
    - enviar respeitando rate limit
    - coletar resultado
- Retornar progress/status para UI (pode ser simples: após concluir, exibir resumo).
- Configurar BASE_URL via env (default https://api.movidesk.com/public/v1) mesmo que hoje seja igual.

