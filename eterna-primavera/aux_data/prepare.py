import pandas as pd


def main():
    """Loads population data from the DANE website."""
    url = "https://www.dane.gov.co/files/censo2018/proyecciones-de-poblacion/Municipal/DCD-area-proypoblacion-Mun-2020-2035-ActPostCOVID-19.xlsx"
    (
        pd.read_excel(url, sheet_name="Hoja1", skiprows=8, usecols="A:G")
        .query("`ÁREA GEOGRÁFICA` == 'Total'")
        .assign(
            MPIO=lambda df: df["MPIO"].astype(int).astype(str).str.zfill(5),
            YEAR=lambda df: df["AÑO"].astype(int),
            POPULATION=lambda df: df["Población"].astype(int),
        )
        .pivot_table(values="POPULATION", index=["MPIO", "DPMP"], columns="YEAR",)
        .filter([2023, 2035])
        .add_prefix("population_")
        .reset_index("DPMP")
        .rename(columns={"DPMP": "NOMBRE"})
        .to_parquet("eterna-primavera/aux_data/cities.parquet")
    )


if __name__ == "__main__":
    main()
