import pandas as pd
import numpy as np

def transform_enem_data(df):
    """
    Transforma os dados extraídos do ENEM para análise.

    Args:
        df (pd.DataFrame): DataFrame com dados extraídos.

    Returns:
        dict: Dicionário com DataFrames transformados.
    """
    # Criar coluna de presença geral (presente se pelo menos uma nota)
    df['PRESENTE'] = df[['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']].notna().any(axis=1)

    # Filtrar apenas presentes
    df_presentes = df[df['PRESENTE']].copy()

    # Substituir NaN por 0 para ausências
    notas_cols = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']
    df_presentes[notas_cols] = df_presentes[notas_cols].fillna(0)

    # Criar grupo de análise baseado em localização
    df_presentes['GRUPO_ANALISE'] = df_presentes['TP_LOCALIZACAO_ESC'].map({
        1: 'ALTAMIRA - Urbana',
        2: 'ALTAMIRA - Rural'
    }).fillna('DADO NAO INFORMADO')

    # Calcular médias por grupo
    desempenho_grupo = df_presentes.groupby('GRUPO_ANALISE').agg({
        'NU_NOTA_CN': 'mean',
        'NU_NOTA_CH': 'mean',
        'NU_NOTA_LC': 'mean',
        'NU_NOTA_MT': 'mean',
        'NU_NOTA_REDACAO': 'mean'
    }).round(2)

    desempenho_grupo['Média Geral'] = desempenho_grupo[['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']].mean(axis=1).round(2)
    desempenho_grupo = desempenho_grupo.rename(columns={
        'NU_NOTA_CN': 'CN_Média',
        'NU_NOTA_CH': 'CH_Média',
        'NU_NOTA_LC': 'LC_Média',
        'NU_NOTA_MT': 'MT_Média',
        'NU_NOTA_REDACAO': 'RED_Média'
    }).reset_index()

    # Correlações
    correlacao_notas = df_presentes[notas_cols].corr().round(2)

    # Ausências por grupo
    ausencias_grupo = df_presentes.groupby('GRUPO_ANALISE').agg({
        'NU_NOTA_CN': lambda x: (x == 0).sum(),
        'NU_NOTA_CH': lambda x: (x == 0).sum(),
        'NU_NOTA_LC': lambda x: (x == 0).sum(),
        'NU_NOTA_MT': lambda x: (x == 0).sum(),
        'NU_NOTA_REDACAO': lambda x: (x == 0).sum()
    }).reset_index()

    # Estatísticas descritivas
    descritivas_notas = df_presentes[notas_cols].describe().round(2).T

    # Dependência administrativa (se disponível)
    if 'TP_DEPENDENCIA_ADM_ESC' in df_presentes.columns:
        df_presentes['DEPENDENCIA_ADM'] = df_presentes['TP_DEPENDENCIA_ADM_ESC'].map({
            1: 'Federal',
            2: 'Estadual',
            3: 'Municipal',
            4: 'Privada'
        }).fillna('Não informado')

        desempenho_dependencia = df_presentes.groupby('DEPENDENCIA_ADM').agg({
            'NU_NOTA_CN': 'mean',
            'NU_NOTA_CH': 'mean',
            'NU_NOTA_LC': 'mean',
            'NU_NOTA_MT': 'mean',
            'NU_NOTA_REDACAO': 'mean'
        }).round(2)

        desempenho_dependencia['Média Geral'] = desempenho_dependencia.mean(axis=1).round(2)
        desempenho_dependencia = desempenho_dependencia.reset_index()
    else:
        desempenho_dependencia = None

    return {
        'desempenho_grupo': desempenho_grupo,
        'correlacao_notas': correlacao_notas,
        'ausencias_grupo': ausencias_grupo,
        'descritivas_notas': descritivas_notas,
        'desempenho_dependencia': desempenho_dependencia
    }

if __name__ == "__main__":
    # Exemplo de uso
    from ..Extract.extract import extract_enem_data
    df = extract_enem_data("../../DataSources/microdados_enem_2024.csv")
    transformed = transform_enem_data(df)
    print(transformed['desempenho_grupo'])
