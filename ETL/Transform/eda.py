import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

def analyze_data_structure(df):
    """
    Análise da estrutura dos dados: tipos, missing values, duplicatas.

    Args:
        df (pd.DataFrame): DataFrame a ser analisado.

    Returns:
        dict: Dicionário com informações da estrutura.
    """
    structure_info = {
        'shape': df.shape,
        'columns': df.columns.tolist(),
        'dtypes': df.dtypes.to_dict(),
        'missing_values': df.isnull().sum().to_dict(),
        'missing_percentage': (df.isnull().sum() / len(df) * 100).round(2).to_dict(),
        'duplicates': df.duplicated().sum(),
        'unique_values': df.nunique().to_dict()
    }

    print("=== ANÁLISE DE ESTRUTURA DOS DADOS ===")
    print(f"Shape: {structure_info['shape']}")
    print(f"Duplicatas: {structure_info['duplicates']}")
    print("\nMissing Values por coluna:")
    for col, count in structure_info['missing_values'].items():
        if count > 0:
            pct = structure_info['missing_percentage'][col]
            print(f"  {col}: {count} ({pct}%)")

    return structure_info

def descriptive_statistics(df, notas_cols):
    """
    Gera estatísticas descritivas detalhadas para as notas.

    Args:
        df (pd.DataFrame): DataFrame com dados.
        notas_cols (list): Colunas de notas.

    Returns:
        pd.DataFrame: Estatísticas descritivas.
    """
    desc_stats = df[notas_cols].describe().round(2).T
    desc_stats['missing_count'] = df[notas_cols].isnull().sum()
    desc_stats['missing_pct'] = (desc_stats['missing_count'] / len(df) * 100).round(2)
    desc_stats['zero_count'] = (df[notas_cols] == 0).sum()
    desc_stats['zero_pct'] = (desc_stats['zero_count'] / len(df) * 100).round(2)

    print("\n=== ESTATÍSTICAS DESCRITIVAS DETALHADAS ===")
    print(desc_stats)

    return desc_stats

def detect_outliers_iqr(df, column, multiplier=1.5):
    """
    Detecta outliers usando método IQR.

    Args:
        df (pd.DataFrame): DataFrame.
        column (str): Coluna para análise.
        multiplier (float): Multiplicador para IQR.

    Returns:
        tuple: (outliers, limites inferior/superior, percentual de outliers)
    """
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - multiplier * IQR
    upper_bound = Q3 + multiplier * IQR

    outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)][column]
    outlier_pct = len(outliers) / len(df) * 100

    return outliers, (lower_bound, upper_bound), outlier_pct

def analyze_outliers(df, notas_cols):
    """
    Análise abrangente de outliers nas notas.

    Args:
        df (pd.DataFrame): DataFrame.
        notas_cols (list): Colunas de notas.

    Returns:
        dict: Informações sobre outliers.
    """
    outliers_info = {}

    print("\n=== ANÁLISE DE OUTLIERS (MÉTODO IQR) ===")

    for col in notas_cols:
        if df[col].notna().sum() > 0:
            outliers, bounds, pct = detect_outliers_iqr(df, col)
            outliers_info[col] = {
                'count': len(outliers),
                'percentage': round(pct, 2),
                'lower_bound': round(bounds[0], 2),
                'upper_bound': round(bounds[1], 2),
                'values': outliers.tolist()[:10]  # primeiros 10 para análise
            }

            print(f"\n{col}:")
            print(f"  Outliers detectados: {len(outliers)} ({pct:.2f}%)")
            print(f"  Limites: [{bounds[0]:.2f}, {bounds[1]:.2f}]")
            if len(outliers) > 0:
                print(f"  Valores extremos: {sorted(outliers.unique())[:5]}...{sorted(outliers.unique())[-5:]}")

    return outliers_info

def analyze_bias_and_representativeness(df):
    """
    Análise de viés e representatividade dos dados.

    Args:
        df (pd.DataFrame): DataFrame.

    Returns:
        dict: Informações sobre viés e representatividade.
    """
    bias_info = {}

    print("\n=== ANÁLISE DE VIÉS E REPRESENTATIVIDADE ===")

    # Distribuição por localização
    if 'TP_LOCALIZACAO_ESC' in df.columns:
        loc_dist = df['TP_LOCALIZACAO_ESC'].value_counts(normalize=True) * 100
        bias_info['localizacao'] = loc_dist.round(2).to_dict()
        print(f"Distribuição por localização: {bias_info['localizacao']}")

    # Distribuição por dependência administrativa
    if 'TP_DEPENDENCIA_ADM_ESC' in df.columns:
        dep_dist = df['TP_DEPENDENCIA_ADM_ESC'].value_counts(normalize=True) * 100
        bias_info['dependencia'] = dep_dist.round(2).to_dict()
        print(f"Distribuição por dependência: {bias_info['dependencia']}")

    # Análise de presença vs. notas
    notas_cols = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']
    presenca_cols = ['TP_PRESENCA_CN', 'TP_PRESENCA_CH', 'TP_PRESENCA_LC', 'TP_PRESENCA_MT']

    presence_vs_grades = {}
    for i, (pres_col, grade_col) in enumerate(zip(presenca_cols, notas_cols)):
        present_with_grade = df[(df[pres_col] == 1) & df[grade_col].notna()].shape[0]
        present_without_grade = df[(df[pres_col] == 1) & df[grade_col].isna()].shape[0]
        absent_with_grade = df[(df[pres_col] == 0) & df[grade_col].notna()].shape[0]

        presence_vs_grades[grade_col] = {
            'present_with_grade': present_with_grade,
            'present_without_grade': present_without_grade,
            'absent_with_grade': absent_with_grade
        }

        if present_without_grade > 0 or absent_with_grade > 0:
            print(f"Inconsistência detectada em {grade_col}: {present_without_grade} presentes sem nota, {absent_with_grade} ausentes com nota")

    bias_info['presence_consistency'] = presence_vs_grades

    return bias_info

def validate_data_consistency(df):
    """
    Validações de consistência cruzada dos dados.

    Args:
        df (pd.DataFrame): DataFrame.

    Returns:
        dict: Resultados das validações.
    """
    validation_results = {
        'passed': [],
        'warnings': [],
        'errors': []
    }

    print("\n=== VALIDAÇÕES DE CONSISTÊNCIA ===")

    # Validação 1: Notas devem estar entre 0 e 1000
    notas_cols = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']
    for col in notas_cols:
        invalid_grades = df[(df[col] < 0) | (df[col] > 1000) & df[col].notna()]
        if len(invalid_grades) > 0:
            validation_results['errors'].append(f"{len(invalid_grades)} notas inválidas em {col}")
            print(f"ERRO: {len(invalid_grades)} notas fora do intervalo [0,1000] em {col}")

    # Validação 2: Presença deve ser consistente com notas
    presenca_cols = ['TP_PRESENCA_CN', 'TP_PRESENCA_CH', 'TP_PRESENCA_LC', 'TP_PRESENCA_MT']
    for pres_col, grade_col in zip(presenca_cols, notas_cols):
        # Presente mas sem nota (exceto redação que pode ter status especial)
        if grade_col != 'NU_NOTA_REDACAO':
            inconsistent = df[(df[pres_col] == 1) & df[grade_col].isna()]
            if len(inconsistent) > 0:
                validation_results['warnings'].append(f"{len(inconsistent)} registros com presença mas sem nota em {grade_col}")
                print(f"AVISO: {len(inconsistent)} registros com presença mas sem nota em {grade_col}")

    # Validação 3: Verificar se todos os registros são de Altamira-PA
    if 'NO_MUNICIPIO_ESC' in df.columns and 'SG_UF_ESC' in df.columns:
        non_altamira = df[(df['NO_MUNICIPIO_ESC'] != 'Altamira') | (df['SG_UF_ESC'] != 'PA')]
        if len(non_altamira) > 0:
            validation_results['errors'].append(f"{len(non_altamira)} registros não são de Altamira-PA")
            print(f"ERRO: {len(non_altamira)} registros não são de Altamira-PA")

    # Resumo das validações
    print(f"\nResumo das validações:")
    print(f"  ✓ Passaram: {len(validation_results['passed'])}")
    print(f"  ⚠ Avisos: {len(validation_results['warnings'])}")
    print(f"  ✗ Erros: {len(validation_results['errors'])}")

    return validation_results

def run_complete_eda(df):
    """
    Executa análise exploratória completa dos dados.

    Args:
        df (pd.DataFrame): DataFrame a ser analisado.

    Returns:
        dict: Resultado completo da EDA.
    """
    notas_cols = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']

    eda_results = {
        'structure': analyze_data_structure(df),
        'descriptive_stats': descriptive_statistics(df, notas_cols),
        'outliers': analyze_outliers(df, notas_cols),
        'bias_analysis': analyze_bias_and_representativeness(df),
        'validations': validate_data_consistency(df)
    }

    return eda_results

if __name__ == "__main__":
    # Exemplo de uso
    from ..Extract.extract import extract_enem_data
    df = extract_enem_data("../../DataSources/microdados_enem_2024.csv")
    results = run_complete_eda(df)
    print("\nEDA concluída!")
