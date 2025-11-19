import sqlite3
import pandas as pd
from typing import Dict, Any
import sys
import os
sys.path.append('ETL/Extract')
sys.path.append('ETL/Transform')

from ETL.Extract.extract import extract_enem_data
from ETL.Transform.transform import transform_enem_data

def create_database_from_csv(csv_path, db_path='DWStorage/enem_analysis.db', force=False):
    """
    Executa o pipeline ETL completo a partir de um arquivo CSV.
    Cria ou atualiza o banco de dados com os dados processados.
    """
    print(f"Iniciando ETL para o arquivo: {csv_path}")

    # Criar diretório do banco se não existir
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Verificar se arquivo já foi processado (usando checksum simples)
    checksum = str(os.path.getsize(csv_path))  # Checksum baseado no tamanho do arquivo
    ano = 2024  # Assumir ano 2024, pode ser extraído do nome do arquivo se necessário

    create_etl_control_table(db_path)

    if not force and check_file_already_processed(csv_path, checksum, db_path):
        print("Arquivo já processado. Pulando ETL.")
        return

    # Extrair dados
    print("Extraindo dados...")
    raw_data = extract_enem_data(csv_path)

    # Transformar dados
    print("Transformando dados...")
    transformed_data = transform_enem_data(raw_data)

    # Carregar dados
    print("Carregando dados...")
    load_to_sqlite_with_year(transformed_data, db_path)
    load_quality_metrics_to_sqlite(pd.DataFrame([transformed_data.get('quality_metrics')]), db_path)

    # Atualizar controle ETL
    update_etl_control_table(csv_path, ano, checksum, 'completed', db_path)

    print("ETL concluído com sucesso!")

def create_etl_control_table(db_path):
    """
    Cria tabela de controle ETL se não existir.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS etl_control (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT NOT NULL,
            ano INTEGER,
            checksum TEXT,
            status TEXT,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

def check_file_already_processed(file_path, checksum, db_path):
    """
    Verifica se o arquivo já foi processado baseado no checksum.
    Retorna (já_processado, status).
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT status FROM etl_control
        WHERE file_path = ? AND checksum = ?
    ''', (file_path, checksum))

    result = cursor.fetchone()
    conn.close()

    if result:
        return True, result[0]
    else:
        return False, None

def update_etl_control_table(file_path, ano, checksum, status, db_path):
    """
    Atualiza ou insere registro na tabela de controle ETL.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT OR REPLACE INTO etl_control (file_path, ano, checksum, status)
        VALUES (?, ?, ?, ?)
    ''', (file_path, ano, checksum))

    conn.commit()
    conn.close()

def load_to_sqlite(data: Dict[str, pd.DataFrame], db_path: str):
    """
    Carrega dados transformados para SQLite.
    """
    conn = sqlite3.connect(db_path)

    for table_name, df in data.items():
        if df is not None and not df.empty:
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            print(f"Tabela '{table_name}' carregada com sucesso. {len(df)} registros.")
        else:
            print(f"Tabela '{table_name}' está vazia ou None. Pulando carregamento.")

    conn.close()

def load_quality_metrics_to_sqlite(quality_metrics: pd.DataFrame, db_path: str):
    """
    Carrega métricas de qualidade para SQLite.
    """
    conn = sqlite3.connect(db_path)

    if quality_metrics is not None and not quality_metrics.empty:
        quality_metrics.to_sql('quality_metrics', conn, if_exists='replace', index=False)
        print(f"Tabela 'quality_metrics' carregada com sucesso. {len(quality_metrics)} registros.")
    else:
        print("Métricas de qualidade estão vazias ou None. Pulando carregamento.")

    conn.close()

def load_to_sqlite_with_year(data: Dict[str, pd.DataFrame], db_path: str):
    """
    Carrega dados transformados para SQLite com otimizações de performance.
    Adiciona coluna 'ANO' se não existir e cria índices para consultas rápidas.
    """
    conn = sqlite3.connect(db_path)

    for table_name, df in data.items():
        if df is not None and not df.empty:
            # Padronizar nome da coluna para 'ANO' (uppercase)
            if 'ano' in df.columns:
                df = df.rename(columns={'ano': 'ANO'})
            elif 'ANO' not in df.columns:
                print(f"Aviso: Coluna 'ANO' não encontrada em '{table_name}'. Adicionando valor padrão.")
                df['ANO'] = 2023  # Valor padrão

            # Carregar com batch insertions para melhor performance
            df.to_sql(table_name, conn, if_exists='append', index=False, chunksize=1000)
            print(f"Tabela '{table_name}' carregada com sucesso. {len(df)} registros.")

            # Criar índice na coluna ANO para consultas rápidas
            try:
                conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_ano ON {table_name}(ANO)")
                print(f"Índice criado para coluna ANO na tabela '{table_name}'.")
            except Exception as e:
                print(f"Aviso: Não foi possível criar índice para '{table_name}': {e}")
        else:
            print(f"Tabela '{table_name}' está vazia ou None. Pulando carregamento.")

    conn.close()
