from pathlib import Path

import pandas as pd


INPUT_FILE = Path("reports/laudos_estruturados.csv")
OUTPUT_FILE = Path("reports/amostra_validacao.csv")

FIELDS_TO_VALIDATE = [
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


def main() -> None:
    """Cria uma amostra de laudos para conferência manual."""

    df = pd.read_csv(INPUT_FILE)

    successful_df = df.loc[
        df["status_extracao"].eq("sucesso")
    ].copy()

    sample_files = successful_df["arquivo"].sample(
        n=min(5, len(successful_df)),
        random_state=42,
    )

    sample_df = successful_df.loc[
        successful_df["arquivo"].isin(sample_files)
    ]

    validation_rows = []

    for _, row in sample_df.iterrows():
        for field in FIELDS_TO_VALIDATE:
            validation_rows.append(
                {
                    "arquivo": row["arquivo"],
                    "campo": field,
                    "valor_extraido": row[field],
                    "valor_gabarito": "",
                    "acerto": "",
                    "observacao": "",
                }
            )

    validation_df = pd.DataFrame(validation_rows)

    validation_df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    print(f"Amostra criada: {OUTPUT_FILE}")
    print(f"Laudos selecionados: {sample_df['arquivo'].nunique()}")
    print(f"Campos a validar: {len(validation_df)}")


if __name__ == "__main__":
    main()