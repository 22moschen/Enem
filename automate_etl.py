import os
import pandas as pd
import glob
from ETL.Extract.extract import extract_enem_data, extract_from_altamira_files
from ETL.Transform.transform import transform_enem_data
from ETL.Load.load import load_to_sqlite, load_quality_metrics_to_sqlite, load_to_sqlite_with_year, create_etl_control_table, check_file_already_processed, update_etl_control_table

def detect_new_data():
    """
    Detecta novos arquivos de dados na pasta DataSources.
    Retorna lista de arquivos novos ou modificados.
    """
    data_sources = "DataSources"
    if not os.path.exists(data_sources):
        os.makedirs(data_sources)
        return []

    new_files = []
    # Usar os.walk para percorrer recursivamente e evitar duplicatas
    for root, dirs, files in os.walk(data_sources):
        for file in files:
            file_path = os.path.join(root, file)
            file_ext = os.path.splitext(file)[1].lower()
            if file_ext in ['.csv', '.xlsx', '.xls']:
                # Verificar se é um arquivo tratado de Altamira
                if "tratados_altamira" in file_path.lower():
                    continue  # Já processado pelo run_etl.py
                new_files.append(file_path)

    return new_files

def detect_csv_in_dwstorage():
    """
    Detecta arquivos CSV na pasta DWStorage e extrai o ano do nome do arquivo.
    Retorna lista de dicionários com caminho e ano.
    """
    dwstorage = "DWStorage"
    if not os.path.exists(dwstorage):
        os.makedirs(dwstorage)
        return []

    csv_files = glob.glob(os.path.join(dwstorage, "*.csv"))
    csv_with_years = []

    for file_path in csv_files:
        filename = os.path.basename(file_path)
        # Extrair ano do nome do arquivo (assumindo formato como '2020.csv' ou 'dados_2021.csv')
        import re
        match = re.search(r'(\d{4})', filename)
        if match:
            year = int(match.group(1))
            csv_with_years.append({'path': file_path, 'year': year})
        else:
            print(f"Ano não encontrado no nome do arquivo: {filename}")

    return csv_with_years

def process_csv_by_year(file_path, year):
    """
    Processa um CSV específico de DWStorage, adicionando coluna de ano.
    """
    print(f"Processando CSV de {year}: {file_path}")

    try:
        # Verificar se é microdados do ENEM
        df_sample = pd.read_csv(file_path, sep=';', nrows=5, encoding='latin1')
        if 'NU_INSCRICAO' in df_sample.columns:
            print(f"Arquivo identificado como microdados ENEM de {year}.")
            df = extract_enem_data(file_path)
            transformed = transform_enem_data(df)

            # Adicionar coluna de ano a todos os DataFrames transformados
            for table_name, df_table in transformed.items():
                if df_table is not None:
                    df_table['ano'] = year

            load_to_sqlite_with_year(transformed, 'DWStorage/enem_analysis.db')
            return True
        else:
            print("Arquivo CSV não identificado como microdados ENEM.")
            return False

    except Exception as e:
        print(f"Erro ao processar {file_path}: {e}")
        return False

def process_file(file_path):
    """
    Processa um arquivo individual baseado no tipo e conteúdo, com verificação de duplicidade.
    """
    print(f"Processando arquivo: {file_path}")

    file_ext = os.path.splitext(file_path)[1].lower()

    try:
        if file_ext == '.csv':
            # Verificar se é microdados do ENEM
            df_sample = pd.read_csv(file_path, sep=';', nrows=5, encoding='latin1')
            if 'NU_INSCRICAO' in df_sample.columns:
                print("Arquivo identificado como microdados ENEM completo.")

                # Extrair dados e checksum
                df, checksum = extract_enem_data(file_path)

                # Verificar se já foi processado
                already_processed, status = check_file_already_processed(file_path, checksum, 'DWStorage/enem_analysis.db')

                if already_processed and status == "já_processado":
                    print(f"Arquivo {os.path.basename(file_path)} já processado e inalterado. ETL ignorado.")
                    return True
                elif status == "modificado":
                    print(f"Arquivo {os.path.basename(file_path)} modificado. Reprocessamento iniciado.")

                # Extrair ano do nome do arquivo
                filename = os.path.basename(file_path)
                import re
                match = re.search(r'(\d{4})', filename)
                year = int(match.group(1)) if match else 2023  # Default para 2023 se não encontrar

                # Transformar dados
                transformed = transform_enem_data(df, ano=year)

                # Carregar dados com separação por ano
                load_to_sqlite_with_year(transformed, 'DWStorage/enem_analysis.db')

                # Carregar métricas de qualidade separadamente
                if 'quality_metrics' in transformed:
                    load_quality_metrics_to_sqlite(transformed['quality_metrics'], 'DWStorage/enem_analysis.db')

                # Atualizar controle ETL
                update_etl_control_table(file_path, year, checksum, 'PROCESSADO_OK', 'DWStorage/enem_analysis.db')

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
        # Tentar atualizar controle ETL com erro
        try:
            filename = os.path.basename(file_path)
            import re
            match = re.search(r'(\d{4})', filename)
            year = int(match.group(1)) if match else 2023
            update_etl_control_table(file_path, year, "", 'ERRO', 'DWStorage/enem_analysis.db')
        except:
            pass
        return False

def run_automated_etl():
    """
    Executa ETL automatizado detectando novos dados com sistema de controle de duplicidade.
    """
    print("🔄 Iniciando ETL automatizado...")

    # Criar tabela de controle ETL se não existir
    create_etl_control_table('DWStorage/enem_analysis.db')

    # Verificar se o DB já existe em DWStorage
    db_path = 'DWStorage/enem_analysis.db'
    if os.path.exists(db_path):
        print("ℹ️ Banco de dados já existe em DWStorage. Pulando ETL padrão.")
    else:
        # Primeiro, executar o ETL padrão com dados tratados de Altamira
        try:
            from run_etl import main as run_standard_etl
            run_standard_etl()
            print("✅ ETL padrão executado com sucesso.")
        except Exception as e:
            print(f"⚠️ Erro no ETL padrão: {e}")

    # Detectar CSVs em DWStorage para processamento por ano
    csv_files = detect_csv_in_dwstorage()
    if csv_files:
        print(f"📁 CSVs detectados em DWStorage: {len(csv_files)}")
        for csv_info in csv_files:
            process_csv_by_year(csv_info['path'], csv_info['year'])

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
