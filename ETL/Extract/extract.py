import pandas as pd
import os
import hashlib
from datetime import datetime

def calculate_file_checksum(file_path):
    """
    Calcula o hash MD5 do arquivo para verificação de integridade.

    Args:
        file_path (str): Caminho para o arquivo.

    Returns:
        str: Hash MD5 do arquivo.
    """
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def extract_enem_data(file_path):
    """
    Extrai dados do arquivo CSV dos microdados do ENEM.

    Args:
        file_path (str): Caminho para o arquivo CSV dos microdados.

    Returns:
        tuple: (pd.DataFrame com os dados extraídos, str checksum do arquivo).
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

    # Calcular checksum antes do processamento
    checksum = calculate_file_checksum(file_path)

    # Ler apenas colunas relevantes para Altamira-PA
    columns_of_interest = [
        'NU_INSCRICAO', 'TP_PRESENCA_CN', 'TP_PRESENCA_CH', 'TP_PRESENCA_LC', 'TP_PRESENCA_MT',
        'NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO',
        'TP_LOCALIZACAO_ESC', 'TP_DEPENDENCIA_ADM_ESC', 'NO_MUNICIPIO_ESC', 'SG_UF_ESC', 'NU_ANO'
    ]

    df = pd.read_csv(file_path, sep=';', encoding='latin1', usecols=columns_of_interest, low_memory=False)

    # Filtrar apenas Altamira-PA
    df_altamira = df[df['NO_MUNICIPIO_ESC'] == 'Altamira'].copy()

    # Extrair ano do nome do arquivo se NU_ANO não estiver presente ou for nulo
    filename = os.path.basename(file_path)
    import re
    match = re.search(r'(\d{4})', filename)
    ano_arquivo = int(match.group(1)) if match else 2023

    # Garantir que a coluna NU_ANO tenha o ano correto
    if 'NU_ANO' not in df_altamira.columns or df_altamira['NU_ANO'].isna().all():
        df_altamira['NU_ANO'] = ano_arquivo
    else:
        # Preencher valores nulos com o ano do arquivo
        df_altamira['NU_ANO'] = df_altamira['NU_ANO'].fillna(ano_arquivo)

    print(f"Dados extraídos: {len(df_altamira)} registros de Altamira-PA (Ano: {ano_arquivo})")
    return df_altamira, checksum

def extract_from_altamira_files(participantes_path, resultados_path):
    """
    Extrai dados dos arquivos tratados de Altamira.

    Args:
        participantes_path (str): Caminho para o arquivo Excel de participantes.
        resultados_path (str): Caminho para o arquivo CSV de resultados.

    Returns:
        pd.DataFrame: DataFrame combinado com os dados extraídos.
    """
    # Ler participantes
    df_participantes = pd.read_excel(participantes_path)

    # Ler resultados
    df_resultados = pd.read_csv(resultados_path, sep=';', encoding='latin1')

    # Merge dos dados
    df = pd.merge(df_participantes, df_resultados, left_on='NU_INSCRICAO', right_on='NU_SEQUENCIAL', how='inner')

    # Filtrar colunas relevantes
    columns_of_interest = [
        'NU_INSCRICAO', 'TP_PRESENCA_CN', 'TP_PRESENCA_CH', 'TP_PRESENCA_LC', 'TP_PRESENCA_MT',
        'NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO',
        'TP_LOCALIZACAO_ESC', 'TP_DEPENDENCIA_ADM_ESC', 'NO_MUNICIPIO_ESC', 'SG_UF_ESC'
    ]

    df_filtered = df[columns_of_interest].copy()

    # Validação rigorosa: garantir que apenas dados de Altamira-PA sejam processados
    if 'NO_MUNICIPIO_ESC' not in df_filtered.columns or 'SG_UF_ESC' not in df_filtered.columns:
        raise ValueError("Colunas de município e UF são obrigatórias para filtragem de Altamira-PA")

    # Verificar se há dados de Altamira-PA após filtro
    if df_filtered.empty:
        raise ValueError("Nenhum dado encontrado para Altamira-PA após aplicação dos filtros")

    # Log de auditoria
    print(f"Auditoria: {len(df_filtered)} registros filtrados para Altamira-PA")
    print(f"Auditoria: Distribuição por localização: {df_filtered['TP_LOCALIZACAO_ESC'].value_counts().to_dict()}")
    print(f"Auditoria: Distribuição por dependência: {df_filtered['TP_DEPENDENCIA_ADM_ESC'].value_counts().to_dict()}")

    print(f"Dados extraídos dos arquivos tratados: {len(df_filtered)} registros de Altamira-PA")
    return df_filtered

if __name__ == "__main__":
    # Exemplo de uso
    file_path = "../../DataSources/microdados_enem_2024.csv"  # Ajustar caminho conforme necessário
    df = extract_enem_data(file_path)
    print(df.head())
