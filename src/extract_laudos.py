import argparse
import json
import logging
from pathlib import Path

import pandas as pd
from ollama import chat
from pydantic import BaseModel, Field


MODEL_NAME = "qwen2.5:3b"


class LaudoEstruturado(BaseModel):
    """Formato obrigatório de saída para cada laudo."""

    tipo_imovel: str | None = None
    endereco: str | None = None
    area_privativa: str | None = None
    area_total: str | None = None
    area_terreno: str | None = None
    area_construida: str | None = None
    ano_construcao: str | None = None
    valor_avaliacao: str | None = None
    matricula: str | None = None
    onus: str | None = None
    data_vistoria: str | None = None
    responsavel_tecnico: str | None = None
    alertas: list[str] = Field(default_factory=list)


def get_arguments() -> argparse.Namespace:
    """Lê parâmetros do terminal."""

    parser = argparse.ArgumentParser(
        description="Extrai dados estruturados de laudos imobiliários."
    )

    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/laudos_avaliacao"),
        help="Pasta que contém os arquivos .txt dos laudos.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports"),
        help="Pasta onde os arquivos estruturados serão salvos.",
    )

    return parser.parse_args()


def configure_logging() -> logging.Logger:
    """Registra a execução no terminal e em logs/extract_laudos.log."""

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(
                log_dir / "extract_laudos.log",
                encoding="utf-8",
            ),
            logging.StreamHandler(),
        ],
    )

    return logging.getLogger(__name__)


def build_prompt(document_text: str) -> str:
    """Constrói instruções para o modelo local."""

    return f"""
Extraia dados do laudo imobiliário abaixo.

Regras obrigatórias:
- Use exclusivamente o texto fornecido.
- Não invente, complete ou estime informações.
- Se o campo não existir, retorne null.
- Preserve o valor como aparece no texto, quando possível.
- Se o documento apresentar informações contraditórias, mantenha os
  valores encontrados nos campos mais adequados e descreva a divergência
  na lista alertas.
- Se matrícula, ônus ou qualquer campo não puder ser verificado,
  registre isso em alertas.
- Retorne apenas o objeto no formato solicitado.

LAUDO:
{document_text}
"""


def extract_laudo(
    path: Path,
    logger: logging.Logger,
) -> dict:
    """Envia um laudo ao modelo e retorna um dicionário validado."""

    document_text = path.read_text(encoding="utf-8")

    response = chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": build_prompt(document_text),
            }
        ],
        format=LaudoEstruturado.model_json_schema(),
        options={
            "temperature": 0,
        },
    )

    extracted = LaudoEstruturado.model_validate_json(
        response.message.content
    )

    result = extracted.model_dump()
    result["arquivo"] = path.name
    result["status_extracao"] = "sucesso"

    logger.info("Laudo extraído: %s", path.name)

    return result


def create_error_result(path: Path, error: Exception) -> dict:
    """Cria registro rastreável caso a extração de um laudo falhe."""

    return {
        "arquivo": path.name,
        "tipo_imovel": None,
        "endereco": None,
        "area_privativa": None,
        "area_total": None,
        "area_terreno": None,
        "area_construida": None,
        "ano_construcao": None,
        "valor_avaliacao": None,
        "matricula": None,
        "onus": None,
        "data_vistoria": None,
        "responsavel_tecnico": None,
        "alertas": [f"Falha técnica na extração: {error}"],
        "status_extracao": "erro",
    }


def calculate_coverage(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula cobertura, que mede preenchimento e não veracidade."""

    fields = [
        "tipo_imovel",
        "endereco",
        "area_privativa",
        "area_total",
        "area_terreno",
        "area_construida",
        "ano_construcao",
        "valor_avaliacao",
        "matricula",
        "onus",
        "data_vistoria",
        "responsavel_tecnico",
    ]

    coverage = []

    for field in fields:
        filled = df[field].notna().sum()

        coverage.append(
            {
                "campo": field,
                "preenchidos": int(filled),
                "total_laudos": len(df),
                "cobertura": filled / len(df),
            }
        )

    return pd.DataFrame(coverage)


def main() -> None:
    arguments = get_arguments()
    logger = configure_logging()

    if not arguments.input.exists():
        raise FileNotFoundError(
            f"Pasta de laudos não encontrada: {arguments.input}"
        )

    laudo_files = sorted(arguments.input.glob("*.txt"))

    if not laudo_files:
        raise ValueError(
            "Nenhum arquivo .txt foi encontrado na pasta informada."
        )

    results = []

    for path in laudo_files:
        try:
            results.append(extract_laudo(path, logger))
        except Exception as error:
            logger.exception("Falha ao extrair: %s", path.name)
            results.append(create_error_result(path, error))

    arguments.output.mkdir(exist_ok=True)

    result_df = pd.DataFrame(results)
    coverage_df = calculate_coverage(result_df)

    result_df.to_csv(
        arguments.output / "laudos_estruturados.csv",
        index=False,
        encoding="utf-8-sig",
    )

    (arguments.output / "laudos_estruturados.json").write_text(
        json.dumps(
            results,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    coverage_df.to_csv(
        arguments.output / "cobertura_extracao.csv",
        index=False,
        encoding="utf-8-sig",
    )

    successful = result_df["status_extracao"].eq("sucesso").sum()

    logger.info(
        "Extração concluída: %s de %s laudos processados com sucesso.",
        successful,
        len(result_df),
    )

    print(f"\nLaudos processados: {len(result_df)}")
    print(f"Extrações bem-sucedidas: {successful}")
    print("\nCobertura por campo:")
    print(coverage_df.to_string(index=False))


if __name__ == "__main__":
    main()