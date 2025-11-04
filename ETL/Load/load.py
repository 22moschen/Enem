import sqlite3
import pandas as pd
import os

def load_to_sqlite(data_dict, db_path='enem_analysis.db'):
    """
    Carrega os dados transformados para o banco SQLite.

    Args:
        data_dict (dict): Dicionário com DataFrames transformados.
        db_path (str): Caminho para o banco SQLite.
    """
    conn = sqlite3.connect(db_path)

    for table_name, df in data_dict.items():
        if df is not None:
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            print(f"Tabela '{table_name}' carregada com {len(df)} registros.")

    conn.close()
    print(f"Dados carregados para {db_path}")

def create_database_from_csv(csv_path, db_path='enem_analysis.db'):
    """
    Pipeline completo: Extrair, transformar e carregar dados.

    Args:
        csv_path (str): Caminho para o CSV dos microdados.
        db_path (str): Caminho para o banco SQLite.
    """
    from extract import extract_enem_data
    from transform import transform_enem_data

    print("Iniciando ETL...")
    df = extract_enem_data(csv_path)
    transformed_data = transform_enem_data(df)
    load_to_sqlite(transformed_data, db_path)
    print("ETL concluído!")

if __name__ == "__main__":
    # Exemplo de uso
    csv_path = "../../DataSources/microdados_enem_2024.csv"
    create_database_from_csv(csv_path)
