import logging
import re
import unicodedata

import pandas as pd


def normalize_text(value: object) -> str:
    """Remove espaços, acentos e diferenças de maiúsculas/minúsculas."""

    text = str(value).strip()
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ASCII", "ignore").decode("ASCII")

    return text.lower()


def parse_number(value: object) -> float:
    """Converte números em formatos como 1234.56 ou R$ 1.234,56."""

    if pd.isna(value) or str(value).strip() == "":
        return float("nan")

    text = re.sub(r"[^0-9,.-]", "", str(value))

    if "," in text:
        text = text.replace(".", "").replace(",", ".")

    return float(text)


def clean_data(df: pd.DataFrame, logger: logging.Logger) -> pd.DataFrame:
    """Aplica as regras de tratamento documentadas no desafio."""

    clean_df = df.copy()

    channel_map = {
        "correspondente": "Correspondente",
        "organico": "Organico",
        "midia paga": "Mídia paga",
        "indicacao": "Indicação",
        "parceria": "Parceria",
    }

    clean_df["canal_origem"] = clean_df["canal_origem"].apply(normalize_text)
    clean_df["canal_origem"] = clean_df["canal_origem"].map(channel_map)

    if clean_df["canal_origem"].isna().any():
        raise ValueError(
            "Foram encontrados canais desconhecidos. "
            "Atualize o channel_map antes de continuar."
        )

    numeric_columns = [
        "valor_imovel",
        "valor_solicitado",
        "prazo_meses",
        "score_credito",
        "idade_cliente",
        "renda_mensal_declarada",
        "flag_cliente_recorrente",
        "etapa_max_funil",
        "tempo_analise_dias",
        "taxa_juros_aa",
    ]

    for column in numeric_columns:
        clean_df[column] = clean_df[column].apply(parse_number)

    clean_df["data_entrada"] = pd.to_datetime(
    clean_df["data_entrada"],
    format="mixed",
    dayfirst=True,
    errors="coerce",
)

    clean_df["data_assinatura_contrato"] = pd.to_datetime(
        clean_df["data_assinatura_contrato"],
        format="mixed",
        dayfirst=True,
        errors="coerce",
)

    if clean_df["data_entrada"].isna().any():
        invalid_dates = clean_df["data_entrada"].isna().sum()
        raise ValueError(
            f"{invalid_dates} propostas têm data_entrada inválida."
        )

    is_terreno = (
        clean_df["tipo_imovel"]
        .str.strip()
        .str.casefold()
        .eq("terreno")
    )

    removed_terrenos = is_terreno.sum()
    clean_df = clean_df.loc[~is_terreno].copy()

    invalid_stage = clean_df["etapa_max_funil"] > 6
    corrected_stages = invalid_stage.sum()
    clean_df.loc[invalid_stage, "etapa_max_funil"] = 6

    clean_df["ltv"] = (
        clean_df["valor_solicitado"] / clean_df["valor_imovel"]
    )

    clean_df["contratada"] = (
        clean_df["status_final"].eq("Contratada")
    )

    logger.info("Registros removidos por tipo Terreno: %s", removed_terrenos)
    logger.info("Etapas acima de 6 corrigidas: %s", corrected_stages)
    logger.info("Propostas elegíveis após tratamento: %s", f"{len(clean_df):,}")

    return clean_df