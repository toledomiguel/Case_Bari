# Case Bari - AI & Data Lab

## Objetivo

Este projeto analisa propostas de crédito com garantia de imóvel, automatiza a geração de um relatório semanal do funil e extrai informações estruturadas de laudos imobiliários em texto livre.

Todos os dados utilizados são os materiais sintéticos fornecidos no desafio.

## Estrutura do projeto

```text
Case_Bari/
├── data/
│   ├── propostas_credito.csv
│   └── laudos_avaliacao/
├── src/
│   ├── pipeline.py
│   ├── dados_limpos.py
│   ├── metrics.py
│   ├── charts.py
│   ├── report.py
│   ├── extract_laudos.py
│   └── create_validation_sample.py
├── reports/
├── logs/
├── requirements.txt
├── README.md
└── DIARIO.md


Como criar e ativar o ambiente virtual: 
comando:
python -m venv .venv
.\.venv\Scripts\Activate.ps1

Instalar dependências:
comando:
python -m pip install -r requirements.txt

Gerar o relatório do funil:
comando:
python src/pipeline.py --input data/propostas_credito.csv --output reports

A automação valida o arquivo de entrada, trata os dados, salva a base tratada, gera gráficos, registra logs e cria o relatório em reports/relatorio_semanal.html

Extrair os laudos com IA local(usando ollama com modelo local):
Após instalação do ollama ->
comandos:
ollama pull qwen2.5:3b
python src/extract_laudos.py --input data/laudos_avaliacao --output reports

São gerados arquivos em csv e json

Organização dos scripts:
pipeline.py: coordena a automação do relatório semanal.
dados_limpos.py: valida e trata os dados de propostas.
metrics.py: calcula indicadores do funil.
charts.py: gera gráficos.
report.py: monta o relatório HTML.
extract_laudos.py: extrai campos estruturados dos laudos com IA local.
create_validation_sample.py: cria amostra para revisão manual da extração