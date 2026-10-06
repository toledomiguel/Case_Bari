from pathlib import Path
import logging
import pandas as pd
import argparse
import sys
from dados_limpos import clean_data
from charts import create_charts
from report import create_executive_report


from metrics import (
    calculate_channel_metrics,
    calculate_lost_value_by_status,
    calculate_ltv_metrics,
    calculate_monthly_conversion,
    calculate_overall_metrics,
    calculate_score_metrics,
)

# Caminhos usados pelo projeto
INPUT_FILE = Path("data/propostas_credito.csv")
OUTPUT_DIR = Path("reports")
LOG_DIR = Path("logs")

def get_arguments() -> argparse.Namespace:
    """Lê os parâmetros passados no terminal."""

    parser = argparse.ArgumentParser(
        description="Gera o relatório semanal do funil de crédito."
    )

    parser.add_argument(
        "--input",
        type=Path,
        default=INPUT_FILE,
        help="Caminho do CSV bruto de propostas.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_DIR,
        help="Pasta em que relatórios e gráficos serão salvos.",
    )

    return parser.parse_args()


# Colunas exigidas para a análise
REQUIRED_COLUMNS = {
    "id_proposta",
    "data_entrada",
    "canal_origem",
    "cidade",
    "uf",
    "tipo_imovel",
    "valor_imovel",
    "valor_solicitado",
    "prazo_meses",
    "score_credito",
    "idade_cliente",
    "renda_mensal_declarada",
    "flag_cliente_recorrente",
    "consultor_id",
    "etapa_max_funil",
    "status_final",
    "tempo_analise_dias",
    "data_assinatura_contrato",
    "taxa_juros_aa",
}


def configure_logging() -> logging.Logger:
    """Configura mensagens de execução no terminal e em arquivo."""

    LOG_DIR.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(LOG_DIR / "pipeline.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )

    return logging.getLogger(__name__)


def load_raw_data(path: Path, logger: logging.Logger) -> pd.DataFrame:
    """Lê o CSV e valida condições mínimas antes da análise."""

    if not path.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {path}. "
            "Confirme se o CSV está na pasta data/."
        )

    # dtype=str preserva o conteúdo original nesta primeira leitura.
    df = pd.read_csv(path, dtype=str)

    missing_columns = REQUIRED_COLUMNS - set(df.columns)
    if missing_columns:
        missing_list = ", ".join(sorted(missing_columns))
        raise ValueError(
            f"O arquivo está sem colunas obrigatórias: {missing_list}"
        )

    if df["id_proposta"].duplicated().any():
        duplicates = df["id_proposta"].duplicated().sum()
        raise ValueError(
            f"Foram encontrados {duplicates} id_proposta duplicados. "
            "A rotina foi interrompida para evitar contagem dupla."
        )

    logger.info("Arquivo lido com sucesso.")
    logger.info("Linhas recebidas: %s", f"{len(df):,}")
    logger.info("Colunas recebidas: %s", len(df.columns))

    return df


def main() -> None:
    arguments = get_arguments()
    logger = configure_logging()

    try:
        raw_df = load_raw_data(arguments.input, logger)
        clean_df = clean_data(raw_df, logger)

        arguments.output.mkdir(exist_ok=True)

        clean_df.to_csv(
            arguments.output / "propostas_tratadas.csv",
            index=False,
        )

        overall = calculate_overall_metrics(clean_df)
        channel_metrics = calculate_channel_metrics(clean_df)
        lost_value_metrics = calculate_lost_value_by_status(clean_df)
        monthly_metrics = calculate_monthly_conversion(clean_df)
        ltv_metrics = calculate_ltv_metrics(clean_df)
        score_metrics = calculate_score_metrics(clean_df)

        create_charts(
            monthly_metrics=monthly_metrics,
            channel_metrics=channel_metrics,
            lost_value_metrics=lost_value_metrics,
            ltv_metrics=ltv_metrics,
            score_metrics=score_metrics,
            output_dir=arguments.output,
        )

        create_executive_report(
            overall=overall,
            channel_metrics=channel_metrics,
            lost_value_metrics=lost_value_metrics,
            monthly_metrics=monthly_metrics,
            ltv_metrics=ltv_metrics,
            score_metrics=score_metrics,
            output_dir=arguments.output,
        )

        logger.info("Execução concluída com sucesso.")
        logger.info("Arquivos salvos em: %s", arguments.output)

    except (FileNotFoundError, ValueError, pd.errors.ParserError) as error:
        logger.exception("Execução interrompida por erro de entrada.")
        print(f"\nERRO: {error}")
        print("Consulte logs/pipeline.log para mais detalhes.")
        sys.exit(1)

if __name__ == "__main__":
    main()