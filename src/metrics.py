import pandas as pd


def calculate_overall_metrics(df: pd.DataFrame) -> dict:
    """Calcula os indicadores gerais do funil."""

    total_proposals = len(df)
    contracted_proposals = int(df["contratada"].sum())

    conversion_rate = (
        contracted_proposals / total_proposals
        if total_proposals > 0
        else 0
    )

    requested_value = df["valor_solicitado"].sum()

    contracted_value = df.loc[
        df["contratada"],
        "valor_solicitado",
    ].sum()

    lost_value = df.loc[
        ~df["contratada"],
        "valor_solicitado",
    ].sum()

    return {
        "total_propostas": total_proposals,
        "propostas_contratadas": contracted_proposals,
        "conversao": conversion_rate,
        "valor_solicitado": requested_value,
        "valor_contratado": contracted_value,
        "valor_potencial_perdido": lost_value,
    }


def calculate_channel_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula volume, contratação e conversão por canal."""

    channel_metrics = (
        df.groupby("canal_origem")
        .agg(
            propostas=("id_proposta", "size"),
            contratadas=("contratada", "sum"),
            valor_solicitado=("valor_solicitado", "sum"),
        )
        .reset_index()
    )

    channel_metrics["conversao"] = (
        channel_metrics["contratadas"] / channel_metrics["propostas"]
    )

    return channel_metrics.sort_values(
        "conversao",
        ascending=True,
    )


def calculate_lost_value_by_status(df: pd.DataFrame) -> pd.DataFrame:
    """Mostra em qual status está concentrado o valor potencial perdido."""

    lost_metrics = (
        df.loc[~df["contratada"]]
        .groupby("status_final")
        .agg(
            propostas=("id_proposta", "size"),
            valor_potencial_perdido=("valor_solicitado", "sum"),
        )
        .reset_index()
    )

    return lost_metrics.sort_values(
        "valor_potencial_perdido",
        ascending=False,
    )


def calculate_monthly_conversion(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula conversão por mês de entrada da proposta."""

    monthly_metrics = df.copy()

    monthly_metrics["mes"] = (
        monthly_metrics["data_entrada"]
        .dt.to_period("M")
        .astype(str)
    )

    monthly_metrics = (
        monthly_metrics.groupby("mes")
        .agg(
            propostas=("id_proposta", "size"),
            contratadas=("contratada", "sum"),
        )
        .reset_index()
    )

    monthly_metrics["conversao"] = (
        monthly_metrics["contratadas"]
        / monthly_metrics["propostas"]
    )

    return monthly_metrics.sort_values("mes")

def calculate_ltv_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Compara a conversão por faixa de LTV."""

    ltv_metrics = df.copy()

    ltv_metrics["faixa_ltv"] = pd.cut(
        ltv_metrics["ltv"],
        bins=[0, 0.40, 0.50, 0.60, float("inf")],
        labels=[
            "Até 40%",
            "40% a 50%",
            "50% a 60%",
            "Acima de 60%",
        ],
        include_lowest=True,
    )

    result = (
        ltv_metrics.groupby("faixa_ltv", observed=False)
        .agg(
            propostas=("id_proposta", "size"),
            contratadas=("contratada", "sum"),
            conversao=("contratada", "mean"),
            valor_solicitado=("valor_solicitado", "sum"),
        )
        .reset_index()
    )

    return result

def calculate_score_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Compara a conversão por faixa de score de crédito."""

    score_metrics = df.copy()

    score_metrics["faixa_score"] = pd.cut(
        score_metrics["score_credito"],
        bins=[0, 600, 700, 800, float("inf")],
        labels=[
            "Abaixo de 600",
            "600 a 699",
            "700 a 799",
            "800 ou mais",
        ],
        include_lowest=True,
    )

    result = (
        score_metrics.groupby("faixa_score", observed=False)
        .agg(
            propostas=("id_proposta", "size"),
            contratadas=("contratada", "sum"),
            conversao=("contratada", "mean"),
            valor_solicitado=("valor_solicitado", "sum"),
        )
        .reset_index()
    )

    return result