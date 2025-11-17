import sqlite3
import pandas as pd
import os
from datetime import datetime

def load_to_sqlite(data_dict, db_path='DWStorage/enem_analysis.db'):
    """
    Carrega os dados transformados para o banco SQLite.

    Args:
        data_dict (dict): Dicionário com DataFrames transformados.
        db_path (str): Caminho para o banco SQLite.
    """
    conn = sqlite3.connect(db_path)

    for table_name, df in data_dict.items():
        if df is not None and isinstance(df, pd.DataFrame):
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            print(f"Tabela '{table_name}' carregada com {len(df)} registros.")

    conn.close()
    print(f"Dados carregados para {db_path}")

def load_quality_metrics_to_sqlite(quality_metrics, db_path='DWStorage/enem_analysis.db'):
    """
    Carrega métricas de qualidade para o banco SQLite.

    Args:
        quality_metrics (dict): Dicionário com métricas de qualidade.
        db_path (str): Caminho para o banco SQLite.
    """
    conn = sqlite3.connect(db_path)

    # Converter para DataFrame
    df_quality = pd.DataFrame([quality_metrics])
    df_quality.to_sql('quality_metrics', conn, if_exists='replace', index=False)
    print(f"Métricas de qualidade carregadas: {len(df_quality)} registros.")

    conn.close()

def create_etl_control_table(db_path='DWStorage/enem_analysis.db'):
    """
    Cria a tabela de controle ETL se não existir.

    Args:
        db_path (str): Caminho para o banco SQLite.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tabela_controle_etl (
            NOME_ARQUIVO TEXT PRIMARY KEY,
            ANO_DADOS INTEGER,
            MD5_CHECKSUM TEXT,
            DATA_PROCESSAMENTO DATETIME,
            STATUS TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print("Tabela de controle ETL criada/verificada.")

def check_file_already_processed(file_path, checksum, db_path='DWStorage/enem_analysis.db'):
    """
    Verifica se o arquivo já foi processado baseado no nome e checksum.

    Args:
        file_path (str): Caminho para o arquivo.
        checksum (str): Checksum MD5 do arquivo.
        db_path (str): Caminho para o banco SQLite.

    Returns:
        tuple: (bool já_processado, str status).
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    filename = os.path.basename(file_path)

    cursor.execute('''
        SELECT MD5_CHECKSUM, STATUS FROM tabela_controle_etl
        WHERE NOME_ARQUIVO = ?
    ''', (filename,))

    result = cursor.fetchone()
    conn.close()

    if result:
        stored_checksum, status = result
        if stored_checksum == checksum:
            return True, "já_processado"
        else:
            return False, "modificado"
    else:
        return False, "novo"

def update_etl_control_table(file_path, year, checksum, status, db_path='DWStorage/enem_analysis.db'):
    """
    Atualiza a tabela de controle ETL com informações do processamento.

    Args:
        file_path (str): Caminho para o arquivo.
        year (int): Ano dos dados.
        checksum (str): Checksum MD5 do arquivo.
        status (str): Status do processamento ('PROCESSADO_OK', 'ERRO').
        db_path (str): Caminho para o banco SQLite.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    filename = os.path.basename(file_path)
    data_processamento = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('''
        INSERT OR REPLACE INTO tabela_controle_etl
        (NOME_ARQUIVO, ANO_DADOS, MD5_CHECKSUM, DATA_PROCESSAMENTO, STATUS)
        VALUES (?, ?, ?, ?, ?)
    ''', (filename, year, checksum, data_processamento, status))

    conn.commit()
    conn.close()
    print(f"Controle ETL atualizado para {filename}: {status}")

def load_to_sqlite_with_year(data_dict, db_path='DWStorage/enem_analysis.db'):
    """
    Carrega os dados transformados com coluna 'ano' para o banco SQLite, usando append para múltiplos anos.

    Args:
        data_dict (dict): Dicionário com DataFrames transformados (já com coluna 'ano').
        db_path (str): Caminho para o banco SQLite.
    """
    conn = sqlite3.connect(db_path)

    for table_name, df in data_dict.items():
        if df is not None and not df.empty and isinstance(df, pd.DataFrame):
            # Verificar se a tabela já existe e tem dados
            cursor = conn.cursor()
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            table_exists = cursor.fetchone()

            if table_exists:
                # Verificar se já existem dados para este ano
                if 'ano' in df.columns:
                    ano = df['ano'].iloc[0] if not df.empty else None
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE ano = ?", (ano,))
                    count = cursor.fetchone()[0]
                    if count > 0:
                        print(f"Tabela '{table_name}' já possui dados para o ano {ano}. Pulando...")
                        continue

            df.to_sql(table_name, conn, if_exists='append', index=False)
            print(f"Tabela '{table_name}' atualizada com {len(df)} registros (ano incluído).")

    conn.close()
    print(f"Dados carregados para {db_path} com separação por ano.")

def create_database_from_csv(csv_path, db_path='DWStorage/enem_analysis.db'):
    """
    Pipeline completo: Extrair, transformar e carregar dados.

    Args:
        csv_path (str): Caminho para o CSV dos microdados.
        db_path (str): Caminho para o banco SQLite.
    """
    from ..Extract.extract import extract_enem_data
    from ..Transform.transform import transform_enem_data

    print("Iniciando ETL...")
    df = extract_enem_data(csv_path)
    transformed_data = transform_enem_data(df)
    load_to_sqlite(transformed_data, db_path)
    print("ETL concluído!")

def create_database_from_altamira_files(participantes_path, resultados_path, db_path='DWStorage/enem_analysis.db'):
    """
    Pipeline completo usando arquivos tratados de Altamira.

    Args:
        participantes_path (str): Caminho para o arquivo Excel de participantes.
        resultados_path (str): Caminho para o arquivo CSV de resultados.
        db_path (str): Caminho para o banco SQLite.
    """
    from ..Extract.extract import extract_from_altamira_files
    from ..Transform.transform import transform_enem_data

    print("Iniciando ETL com arquivos tratados...")
    df = extract_from_altamira_files(participantes_path, resultados_path)
    transformed_data = transform_enem_data(df)
    load_to_sqlite(transformed_data, db_path)
    print("ETL concluído!")

if __name__ == "__main__":
    # Exemplo de uso com arquivos tratados
    participantes_path = "../../DataSources/tratados_altamira/PARTICIPANTES__ALTAMIRA_2024.csv.xlsx"
    resultados_path = "../../DataSources/tratados_altamira/RESULTADOS_ALTAMIRA_2024corrigido.csv"
    create_database_from_altamira_files(participantes_path, resultados_path)
