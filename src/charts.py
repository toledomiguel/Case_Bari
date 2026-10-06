from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def format_percentage_axis(axis) -> None:
    """Exibe valores do eixo como porcentagem."""

    axis.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda value, _: f"{value:.0%}")
    )


def plot_monthly_conversion(
    monthly_metrics: pd.DataFrame,
    output_dir: Path,
) -> None:
    """Cria gráfico de conversão por mês."""

    fig, axis = plt.subplots(figsize=(11, 5))

    axis.plot(
        monthly_metrics["mes"],
        monthly_metrics["conversao"],
        marker="o",
        color="#1f4e79",
    )

    axis.set_title("Conversão mensal do funil")
    axis.set_xlabel("Mês de entrada")
    axis.set_ylabel("Conversão")
    axis.tick_params(axis="x", rotation=45)

    format_percentage_axis(axis)

    fig.tight_layout()
    fig.savefig(
        output_dir / "conversao_mensal.png",
        dpi=150,
    )
    plt.close(fig)


def plot_channel_conversion(
    channel_metrics: pd.DataFrame,
    output_dir: Path,
) -> None:
    """Cria gráfico de conversão por canal."""

    chart_data = channel_metrics.sort_values("conversao")

    fig, axis = plt.subplots(figsize=(9, 5))

    axis.barh(
        chart_data["canal_origem"],
        chart_data["conversao"],
        color="#1f4e79",
    )

    axis.set_title("Conversão por canal de origem")
    axis.set_xlabel("Conversão")

    axis.xaxis.set_major_formatter(
        plt.FuncFormatter(lambda value, _: f"{value:.0%}")
    )

    fig.tight_layout()
    fig.savefig(
        output_dir / "conversao_por_canal.png",
        dpi=150,
    )
    plt.close(fig)


def plot_lost_value(
    lost_value_metrics: pd.DataFrame,
    output_dir: Path,
) -> None:
    """Cria gráfico de valor potencial perdido por status."""

    chart_data = lost_value_metrics.sort_values(
        "valor_potencial_perdido",
    )

    fig, axis = plt.subplots(figsize=(10, 5))

    axis.barh(
        chart_data["status_final"],
        chart_data["valor_potencial_perdido"] / 1_000_000,
        color="#c0504d",
    )

    axis.set_title("Valor potencial perdido por status")
    axis.set_xlabel("Valor solicitado perdido (R$ milhões)")

    fig.tight_layout()
    fig.savefig(
        output_dir / "valor_perdido_por_status.png",
        dpi=150,
    )
    plt.close(fig)


def plot_ltv_conversion(
    ltv_metrics: pd.DataFrame,
    output_dir: Path,
) -> None:
    """Cria gráfico de conversão por faixa de LTV."""

    fig, axis = plt.subplots(figsize=(9, 5))

    colors = [
        "#1f4e79",
        "#1f4e79",
        "#1f4e79",
        "#c0504d",
    ]

    axis.bar(
        ltv_metrics["faixa_ltv"].astype(str),
        ltv_metrics["conversao"],
        color=colors,
    )

    axis.set_title("Conversão por faixa de LTV")
    axis.set_xlabel("Faixa de LTV")
    axis.set_ylabel("Conversão")

    format_percentage_axis(axis)

    fig.tight_layout()
    fig.savefig(
        output_dir / "conversao_por_ltv.png",
        dpi=150,
    )
    plt.close(fig)


def plot_score_conversion(
    score_metrics: pd.DataFrame,
    output_dir: Path,
) -> None:
    """Cria gráfico de conversão por faixa de score."""

    fig, axis = plt.subplots(figsize=(9, 5))

    axis.bar(
        score_metrics["faixa_score"].astype(str),
        score_metrics["conversao"],
        color="#1f4e79",
    )

    axis.set_title("Conversão por faixa de score")
    axis.set_xlabel("Faixa de score")
    axis.set_ylabel("Conversão")

    format_percentage_axis(axis)

    fig.tight_layout()
    fig.savefig(
        output_dir / "conversao_por_score.png",
        dpi=150,
    )
    plt.close(fig)


def create_charts(
    monthly_metrics: pd.DataFrame,
    channel_metrics: pd.DataFrame,
    lost_value_metrics: pd.DataFrame,
    ltv_metrics: pd.DataFrame,
    score_metrics: pd.DataFrame,
    output_dir: Path,
) -> None:
    """Gera todos os gráficos do relatório."""

    output_dir.mkdir(exist_ok=True)

    plot_monthly_conversion(monthly_metrics, output_dir)
    plot_channel_conversion(channel_metrics, output_dir)
    plot_lost_value(lost_value_metrics, output_dir)
    plot_ltv_conversion(ltv_metrics, output_dir)
    plot_score_conversion(score_metrics, output_dir)

