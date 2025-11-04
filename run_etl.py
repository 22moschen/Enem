import sys
import os
sys.path.append('ETL/Extract')
sys.path.append('ETL/Transform')
sys.path.append('ETL/Load')

from ETL.Extract.extract import extract_enem_data
from ETL.Transform.transform import transform_enem_data
from ETL.Load.load import load_to_sqlite

def main():
    print("Iniciando ETL com arquivos tratados de Altamira...")

    # Usar os arquivos tratados de Altamira
    participantes_path = "DataSources/tratados_altamira/PARTICIPANTES__ALTAMIRA_2024.csv.xlsx"
    resultados_path = "DataSources/tratados_altamira/RESULTADOS_ALTAMIRA_2024corrigido.csv"

    # Como os arquivos não têm chaves comuns, vamos processar o arquivo de resultados diretamente
    # e adicionar dados demográficos se possível
    import pandas as pd

    df_resultados = pd.read_csv(resultados_path, sep=';', encoding='latin1')
    df_participantes = pd.read_excel(participantes_path)

    # Merge on CO_MUNICIPIO_PROVA (ambos têm Altamira)
    df = pd.merge(df_participantes, df_resultados, on='CO_MUNICIPIO_PROVA', how='inner')

    transformed_data = transform_enem_data(df)
    load_to_sqlite(transformed_data, 'enem_analysis.db')

    print("ETL concluído!")

if __name__ == "__main__":
    main()
