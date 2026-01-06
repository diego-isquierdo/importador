Agora implemente a leitura e validação da planilha XLSX.

REGRAS:
- Nome do arquivo não importa.
- A validação deve ocorrer ao clicar “Validar”:
  1) Validar que existe uma aba (usar a primeira aba ativa se não houver nome fixo).
  2) Ler a primeira linha como cabeçalhos.
  3) Validar que os cabeçalhos são exatamente estes (ordem pode ser exigida ou não; definir como: mesma lista, mesma grafia):
     Status, Time/Equipe, identificador, Título, Habilitada_em, Prazo, Iniciador, Cliente_novo, Setor, Produto, Tem_migração, Razão_social, Nome_fantasia, Contato_cliente, Email_cliente, Modulos, Servico_mensal, Servico_tecnico, Gerar_licenca?, Ativação_hosting?, Tem_legal?, Observacoes_gerais
  4) Todos esses campos são obrigatórios:
     - Para cada linha de dados, garantir que nenhum desses campos esteja vazio/nulo.
     - Se houver vazio, retornar erro indicando linha e coluna.
  5) Validar a coluna Produto:
     - Deve ser "ProJuris Enterprise" ou "ProJuris para Empresas".
     - Se não, erro por linha.

- Resultado da validação:
  - Se OK: liberar botão “Enviar”.
  - Se erro: mostrar lista de erros na UI.

ENTREGA:
- Criar módulo importer/xlsx_reader.py para ler o arquivo e retornar uma lista de dicts (uma por linha).
- Criar módulo importer/validator.py que recebe headers e linhas e retorna lista de erros.
- Atualizar endpoints /validate para usar isso.
- Atualizar UI para mostrar erros de validação.
Inclua testes unitários básicos para validator (pytest) com casos: header faltando, produto inválido, campo vazio.
