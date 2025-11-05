import os
import pandas as pd
import glob
from ETL.Extract.extract import extract_enem_data, extract_from_altamira_files
from ETL.Transform.transform import transform_enem_data
from ETL.Load.load import load_to_sqlite

def detect_new_data():
    """
    Detecta novos arquivos de dados na pasta DataSources.
    Retorna lista de arquivos novos ou modificados.
    """
    data_sources = "DataSources"
    if not os.path.exists(data_sources):
        os.makedirs(data_sources)
        return []

    # Procurar por arquivos CSV, Excel, etc.
    patterns = [
        os.path.join(data_sources, "*.csv"),
        os.path.join(data_sources, "*.xlsx"),
        os.path.join(data_sources, "*.xls"),
        os.path.join(data_sources, "**", "*.csv"),
        os.path.join(data_sources, "**", "*.xlsx"),
        os.path.join(data_sources, "**", "*.xls")
    ]

    new_files = []
    for pattern in patterns:
        files = glob.glob(pattern, recursive=True)
        for file in files:
            # Verificar se é um arquivo tratado de Altamira
            if "tratados_altamira" in file.lower():
                continue  # Já processado pelo run_etl.py
            new_files.append(file)

    return new_files

def process_file(file_path):
    """
    Processa um arquivo individual baseado no tipo e conteúdo.
    """
    print(f"Processando arquivo: {file_path}")

    file_ext = os.path.splitext(file_path)[1].lower()

    try:
        if file_ext == '.csv':
            # Verificar se é microdados do ENEM
            df_sample = pd.read_csv(file_path, sep=';', nrows=5, encoding='latin1')
            if 'NU_INSCRICAO' in df_sample.columns:
                print("Arquivo identificado como microdados ENEM completo.")
                df = extract_enem_data(file_path)
                transformed = transform_enem_data(df)
                load_to_sqlite(transformed, 'DWStorage/enem_analysis.db')
                return True
            else:
                print("Arquivo CSV genérico detectado. Tentando processar como dados suplementares.")
                # Para outros CSVs, pode ser necessário tratamento específico
                return False

        elif file_ext in ['.xlsx', '.xls']:
            print("Arquivo Excel detectado. Verificando conteúdo...")
            df_sample = pd.read_excel(file_path, nrows=5)
            if 'NU_INSCRICAO' in df_sample.columns:
                print("Arquivo Excel identificado como dados ENEM.")
                # Para Excel, pode ser necessário merge com outros arquivos
                return False
            else:
                print("Arquivo Excel genérico. Pode requerer processamento manual.")
                return False

        else:
            print(f"Tipo de arquivo não suportado: {file_ext}")
            return False

    except Exception as e:
        print(f"Erro ao processar {file_path}: {e}")
        return False

def run_automated_etl():
    """
    Executa ETL automatizado detectando novos dados.
    """
    print("🔄 Iniciando ETL automatizado...")

    # Primeiro, executar o ETL padrão com dados tratados de Altamira
    try:
        from run_etl import main as run_standard_etl
        run_standard_etl()
        print("✅ ETL padrão executado com sucesso.")
    except Exception as e:
        print(f"⚠️ Erro no ETL padrão: {e}")

    # Detectar novos arquivos
    new_files = detect_new_data()
    if not new_files:
        print("ℹ️ Nenhum novo arquivo detectado em DataSources.")
        return

    print(f"📁 Novos arquivos detectados: {len(new_files)}")

    processed_count = 0
    for file_path in new_files:
        if process_file(file_path):
            processed_count += 1

    print(f"✅ Processamento concluído. {processed_count} arquivos processados com sucesso.")

if __name__ == "__main__":
    run_automated_etl()
