Você é um desenvolvedor sênior Python. Crie um aplicativo web (acesso via browser) chamado “Importador Movidesk”.

OBJETIVO:
- Upload de planilha XLSX (nome do arquivo irrelevante).
- Botão “Validar” (valida cabeçalhos e obrigatórios).
- Botão “Enviar” (somente habilitado após validação OK).
- Área de mensagens/erros na tela.
- Importação cria tickets via API Movidesk.
- Rate limit: máximo 10 requisições por minuto (por plataforma).
- Ao final: gerar log CSV (delimitador ;), salvar localmente e oferecer download.

MULTI-PLATAFORMA via coluna “Produto”:
- Produto == "ProJuris para Empresas" => token Empresas = e04c1f7e-f477-480b-8803-e2766624761e
- Produto == "ProJuris Enterprise"    => token Enterprise = 63d11b3a-b64a-48ac-8ab1-62fc12ebcb90
Endpoint único: POST https://api.movidesk.com/public/v1/tickets?token={token}

ARQUITETURA (escalável e substituível):
- Separar camadas:
  - Web/UI (rotas, templates)
  - Leitura/Validação XLSX
  - Mapeamento linha->payload
  - Sender (interface plugável): TicketSender + MovideskSender
  - Serviço de Importação (orquestra fluxo)
  - Log/Relatórios
- Preparar para autenticação futura (estrutura com “auth placeholder”, sem implementar login agora).
- Ser escalável (fácil adicionar menus/abas).

STACK RECOMENDADA:
- Backend: FastAPI (preferencial) + Jinja2 templates OU FastAPI servindo frontend simples.
- Alternativa: Flask, mas preferir FastAPI.
- XLSX: openpyxl.
- HTTP: httpx.
- Config: pydantic-settings + .env.
- Logs: logging padrão + pasta /logs.

ENTREGA DESTA ETAPA:
1) Estrutura de pastas do projeto.
2) App web rodando com uma página única (home) contendo:
   - upload input
   - botão Validar (desabilitado até ter arquivo carregado)
   - botão Enviar (desabilitado até validação ok)
   - área de mensagens
3) Endpoints básicos:
   - GET /
   - POST /upload (armazenar arquivo temporariamente)
   - POST /validate (valida o arquivo carregado)
   - POST /import (executa importação)
   - GET /download-log/{job_id} (placeholder agora)

IMPORTANTE:
- Não implemente ainda regras profundas de payload nesta etapa: apenas scaffold + upload + estado mínimo.
- Use uma entidade “job_id” para representar uma importação e permitir futuro escalonamento.
- Documente como executar: criação de venv, instalar deps, rodar uvicorn.
Gere o código completo.
