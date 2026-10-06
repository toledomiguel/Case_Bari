from pathlib import Path

import pandas as pd


def format_currency(value: float) -> str:
    """Formata um número como moeda brasileira."""

    formatted = f"{value:,.2f}"
    formatted = formatted.replace(",", "X")
    formatted = formatted.replace(".", ",")
    formatted = formatted.replace("X", ".")

    return f"R$ {formatted}"


def format_percentage(value: float) -> str:
    """Formata decimal como porcentagem."""

    return f"{value:.1%}".replace(".", ",")


def dataframe_to_html(df: pd.DataFrame) -> str:
    """Transforma DataFrame em tabela HTML legível."""

    return df.to_html(
        index=False,
        border=0,
        classes="data-table",
    )


def create_executive_report(
    overall: dict,
    channel_metrics: pd.DataFrame,
    lost_value_metrics: pd.DataFrame,
    monthly_metrics: pd.DataFrame,
    ltv_metrics: pd.DataFrame,
    score_metrics: pd.DataFrame,
    output_dir: Path,
) -> None:
    """Cria um relatório HTML com conclusões e evidências."""

    output_dir.mkdir(exist_ok=True)

    worst_channel = channel_metrics.iloc[0]
    largest_loss = lost_value_metrics.iloc[0]

    latest_three_months = monthly_metrics.tail(3)
    previous_three_months = monthly_metrics.iloc[-6:-3]

    latest_conversion = (
        latest_three_months["contratadas"].sum()
        / latest_three_months["propostas"].sum()
    )

    previous_conversion = (
        previous_three_months["contratadas"].sum()
        / previous_three_months["propostas"].sum()
    )

    conversion_difference = latest_conversion - previous_conversion

    ltv_above_policy = ltv_metrics.loc[
        ltv_metrics["faixa_ltv"].eq("Acima de 60%")
    ].iloc[0]

    low_score = score_metrics.loc[
        score_metrics["faixa_score"].eq("Abaixo de 600")
    ].iloc[0]

    high_score = score_metrics.loc[
        score_metrics["faixa_score"].eq("800 ou mais")
    ].iloc[0]

    html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Relatório semanal do funil de crédito</title>

    <style>
        body {{
            font-family: Arial, sans-serif;
            color: #1f2937;
            max-width: 1100px;
            margin: 40px auto;
            padding: 0 20px;
            line-height: 1.5;
        }}

        h1, h2 {{
            color: #1f4e79;
        }}

        .cards {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
        }}

        .card {{
            background: #f1f5f9;
            border-radius: 8px;
            padding: 16px;
        }}

        .metric {{
            display: block;
            font-size: 24px;
            font-weight: bold;
            color: #1f4e79;
            margin-top: 8px;
        }}

        .data-table {{
            border-collapse: collapse;
            width: 100%;
            margin: 16px 0 24px;
        }}

        .data-table th,
        .data-table td {{
            border-bottom: 1px solid #d1d5db;
            padding: 10px;
            text-align: left;
        }}

        .data-table th {{
            background: #e5e7eb;
        }}

        img {{
            width: 100%;
            max-width: 900px;
            margin: 16px 0 30px;
        }}

        .warning {{
            background: #fef3c7;
            padding: 14px;
            border-left: 4px solid #d97706;
        }}

        .recommendation {{
            background: #f8fafc;
            padding: 14px;
            margin: 12px 0;
            border-left: 4px solid #1f4e79;
        }}
    </style>
</head>

<body>
    <h1>Relatório semanal do funil de crédito</h1>

    <p>
        Base analisada: propostas recebidas entre
        {monthly_metrics["mes"].min()} e {monthly_metrics["mes"].max()}.
        Registros com tipo de imóvel Terreno foram excluídos conforme o enunciado.
    </p>

    <div class="cards">
        <div class="card">
            Propostas elegíveis
            <span class="metric">{overall["total_propostas"]:,}</span>
        </div>

        <div class="card">
            Contratações
            <span class="metric">{overall["propostas_contratadas"]:,}</span>
        </div>

        <div class="card">
            Conversão geral
            <span class="metric">{format_percentage(overall["conversao"])}</span>
        </div>

        <div class="card">
            Valor contratado
            <span class="metric">{format_currency(overall["valor_contratado"])}</span>
        </div>
    </div>

    <h2>Principais conclusões</h2>

    <p>
        O maior valor potencial perdido está em
        <strong>{largest_loss["status_final"]}</strong>:
        {format_currency(largest_loss["valor_potencial_perdido"])}
        distribuídos em {int(largest_loss["propostas"]):,} propostas.
        Esta métrica usa valor solicitado como proxy de valor potencial,
        pois a base não contém informação de margem ou receita.
    </p>

    <p>
        O canal <strong>{worst_channel["canal_origem"]}</strong>
        apresenta a menor conversão, de
        {format_percentage(worst_channel["conversao"])}.
        A conversão geral é de {format_percentage(overall["conversao"])}.
        Isso confirma o sinal agregado da liderança, mas não prova que
        o canal seja a causa do resultado: o perfil das propostas pode ser diferente.
    </p>

    <p>
        Nos últimos três meses, a conversão foi de
        {format_percentage(latest_conversion)}, contra
        {format_percentage(previous_conversion)} nos três meses anteriores.
        A variação é de {conversion_difference:.1%}.
        Há oscilação relevante, portanto a tendência deve ser acompanhada
        antes de concluir uma queda estrutural.
    </p>

    <div class="warning">
        Propostas acima de 60% de LTV representam
        {int(ltv_above_policy["propostas"]):,} registros e têm conversão de
        {format_percentage(ltv_above_policy["conversao"])}.
        Essa faixa está acima da política interna descrita no desafio.
    </div>

    <h2>Características associadas à contratação</h2>

    <p>
        A conversão aumenta de {format_percentage(low_score["conversao"])}
        para propostas com score abaixo de 600 para
        {format_percentage(high_score["conversao"])}
        na faixa de score 800 ou mais. Score e LTV são associações
        descritivas nesta análise, não estimativas causais.
    </p>

    <img src="conversao_por_score.png" alt="Conversão por faixa de score">
    <img src="conversao_por_ltv.png" alt="Conversão por faixa de LTV">
    <img src="conversao_por_canal.png" alt="Conversão por canal">
    <img src="valor_perdido_por_status.png" alt="Valor potencial perdido por status">
    <img src="conversao_mensal.png" alt="Conversão mensal">

    <h2>Recomendações priorizadas</h2>

    <div class="recommendation">
        <strong>1. Criar uma triagem antecipada para LTV acima de 60%.</strong><br>
        O grupo está fora da política e apresenta conversão inferior à média.
        Ação proposta: verificar exceções e documentação antes de consumir
        tempo de análise completa.
    </div>

    <div class="recommendation">
        <strong>2. Abrir a análise de Correspondentes por parceiro e perfil.</strong><br>
        O canal possui volume relevante e a menor conversão agregada.
        Ação proposta: comparar parceiros por LTV, score, ticket e motivo de perda.
    </div>

    <div class="recommendation">
        <strong>3. Criar uma cadência de retorno para propostas sem retorno e documentação pendente.</strong><br>
        Esses status concentram grande valor solicitado.
        Ação proposta: definir proprietário, prazo de contato e motivo padronizado
        para encerramento.
    </div>

    <h2>Tabelas de apoio</h2>

    <h3>Conversão por canal</h3>
    {dataframe_to_html(channel_metrics)}

    <h3>Perda potencial por status</h3>
    {dataframe_to_html(lost_value_metrics)}

    <h3>Conversão por LTV</h3>
    {dataframe_to_html(ltv_metrics)}

    <h3>Conversão por score</h3>
    {dataframe_to_html(score_metrics)}

</body>
</html>
"""

    report_path = output_dir / "relatorio_semanal.html"
    report_path.write_text(html, encoding="utf-8")