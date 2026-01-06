Finalize o fluxo completo com geração de log e download ao final.

LOG:
- Para cada linha (ticket):
  - Escrever no CSV: Identificador;ID
  - Se sucesso: Identificador;{ticket_id}
  - Se erro: Identificador;Erro Status Code {code} - {reason} (ou mensagem equivalente)
- O log deve ser salvo localmente em uma pasta /logs com nome incluindo job_id e timestamp:
  ex: logs/import_{job_id}_{YYYYMMDD_HHMMSS}.csv

UI:
- Após a importação:
  - Mostrar resumo: total, sucesso, erros
  - Exibir lista de erros (linha -> mensagem)
  - Exibir botão “Baixar log” apontando para GET /download-log/{job_id}

ARQUITETURA PARA ESCALA:
- Persistir o job state de forma simples (arquivo JSON local em /jobs ou sqlite) para permitir múltiplas instâncias no futuro.
- Evitar depender de variáveis globais em memória.
- Preparar uma estrutura de menu/abas (ex.: layout base + sidebar), mesmo que haja apenas “Importação” por enquanto.
- Preparar ponto de integração para autenticação (middleware placeholder, configuração, sem login).

ENTREGA:
- Código completo + instruções de execução.
- Inclua tratamento de erros e mensagens amigáveis.
- Inclua testes mínimos:
  - geração de log
  - fluxo de validação habilitar Enviar
  - roteamento de plataforma por Produto
