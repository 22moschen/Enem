import pandas as pd
import os

def extract_enem_data(file_path):
    """
    Extrai dados do arquivo CSV dos microdados do ENEM.

    Args:
        file_path (str): Caminho para o arquivo CSV dos microdados.

    Returns:
        pd.DataFrame: DataFrame com os dados extraídos.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

    # Ler apenas colunas relevantes para Altamira-PA
    columns_of_interest = [
        'NU_INSCRICAO', 'TP_PRESENCA_CN', 'TP_PRESENCA_CH', 'TP_PRESENCA_LC', 'TP_PRESENCA_MT',
        'NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO',
        'TP_LOCALIZACAO_ESC', 'TP_DEPENDENCIA_ADM_ESC', 'NO_MUNICIPIO_ESC', 'SG_UF_ESC'
    ]

    df = pd.read_csv(file_path, sep=';', encoding='latin1', usecols=columns_of_interest, low_memory=False)

    # Filtrar apenas Altamira-PA
    df_altamira = df[df['NO_MUNICIPIO_ESC'] == 'Altamira'].copy()

    print(f"Dados extraídos: {len(df_altamira)} registros de Altamira-PA")
    return df_altamira

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

    # Adicionar município se não existir
    if 'NO_MUNICIPIO_ESC' not in df_filtered.columns:
        df_filtered['NO_MUNICIPIO_ESC'] = 'Altamira'
    if 'SG_UF_ESC' not in df_filtered.columns:
        df_filtered['SG_UF_ESC'] = 'PA'

    print(f"Dados extraídos dos arquivos tratados: {len(df_filtered)} registros de Altamira-PA")
    return df_filtered

if __name__ == "__main__":
    # Exemplo de uso
    file_path = "../../DataSources/microdados_enem_2024.csv"  # Ajustar caminho conforme necessário
    df = extract_enem_data(file_path)
    print(df.head())
