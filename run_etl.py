import sys
import os
sys.path.append('ETL/Extract')
sys.path.append('ETL/Transform')
sys.path.append('ETL/Load')

from ETL.Extract.extract import extract_from_altamira_files
from ETL.Transform.transform import transform_enem_data
from ETL.Load.load import load_to_sqlite, load_quality_metrics_to_sqlite

def main():
    print("Iniciando ETL com arquivos tratados de Altamira...")

    # Usar os arquivos tratados de Altamira (corrigir caminho)
    participantes_path = "DataSources/tratados_altamira/PARTICIPANTES__ALTAMIRA_2024.csv.xlsx"
    resultados_path = "DataSources/tratados_altamira/RESULTADOS_ALTAMIRA_2024corrigido.csv"

    # Extrair dados usando função validada
    df = extract_from_altamira_files(participantes_path, resultados_path)

    # Transformar com qualidade e validações, passando ano 2024
    transformed_data = transform_enem_data(df, ano=2024)

    # Carregar dados principais
    load_to_sqlite(transformed_data, 'DWStorage/enem_analysis.db')

    # Carregar métricas de qualidade separadamente
    if 'quality_metrics' in transformed_data:
        load_quality_metrics_to_sqlite(transformed_data['quality_metrics'], 'DWStorage/enem_analysis.db')

    print("ETL concluído com validações de qualidade!")

if __name__ == "__main__":
    main()
