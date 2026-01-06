# Importador Movidesk

App web para importar tickets no Movidesk a partir de uma planilha XLSX.

## Requisitos

- Python 3.10+

## Instalação

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Configuração

Crie um arquivo `.env` (ou use os defaults) baseado em `.env.example`.

## Executar

```bash
python app/main.py
```

Acesse:

- http://127.0.0.1:8000

## Testes

```bash
pytest -q
```
