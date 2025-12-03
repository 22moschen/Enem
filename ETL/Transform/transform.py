import pandas as pd
import numpy as np
from .eda import detect_outliers_iqr

def impute_missing_grades(df, strategy='median_by_group'):
    """
    Imputação rigorosa de dados faltantes com flags de rastreamento.

    Args:
        df (pd.DataFrame): DataFrame com dados.
        strategy (str): Estratégia de imputação ('median_by_group', 'mean_by_group', 'knn').

    Returns:
        pd.DataFrame: DataFrame com imputação aplicada e flags.
    """
    df_imputed = df.copy()
    notas_cols = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']

    # Criar flags de rastreamento para valores originais faltantes
    for col in notas_cols:
        df_imputed[f'{col}_ORIGINAL_MISSING'] = df_imputed[col].isna()

    print(f"\n=== IMPUTAÇÃO DE DADOS FALTANTES ({strategy}) ===")

    if strategy == 'median_by_group':
        # Imputação por mediana do grupo (urbano/rural)
        group_col = 'TP_LOCALIZACAO_ESC'
        for col in notas_cols:
            missing_mask = df_imputed[col].isna()
            if missing_mask.sum() > 0:
                # Calcular mediana por grupo apenas para valores não-faltantes
                group_medians = df_imputed[~missing_mask].groupby(group_col)[col].median()

                # Aplicar imputação
                for group_val, median_val in group_medians.items():
                    group_mask = (df_imputed[group_col] == group_val) & missing_mask
                    df_imputed.loc[group_mask, col] = median_val
                    print(f"  {col} - Grupo {group_val}: {group_mask.sum()} imputados com mediana {median_val:.2f}")

                # Para grupos sem mediana (todos faltantes), usar mediana global
                still_missing = df_imputed[col].isna()
                if still_missing.sum() > 0:
                    global_median = df_imputed[~missing_mask][col].median()
                    df_imputed.loc[still_missing, col] = global_median
                    print(f"  {col} - Global: {still_missing.sum()} imputados com mediana global {global_median:.2f}")

    elif strategy == 'mean_by_group':
        # Imputação por média do grupo
        group_col = 'TP_LOCALIZACAO_ESC'
        for col in notas_cols:
            missing_mask = df_imputed[col].isna()
            if missing_mask.sum() > 0:
                group_means = df_imputed[~missing_mask].groupby(group_col)[col].mean()

                for group_val, mean_val in group_means.items():
                    group_mask = (df_imputed[group_col] == group_val) & missing_mask
                    df_imputed.loc[group_mask, col] = mean_val
                    print(f"  {col} - Grupo {group_val}: {group_mask.sum()} imputados com média {mean_val:.2f}")

                still_missing = df_imputed[col].isna()
                if still_missing.sum() > 0:
                    global_mean = df_imputed[~missing_mask][col].mean()
                    df_imputed.loc[still_missing, col] = global_mean
                    print(f"  {col} - Global: {still_missing.sum()} imputados com média global {global_mean:.2f}")

    return df_imputed

def treat_outliers(df, method='capping', notas_cols=None):
    """
    Tratamento de outliers com flags de rastreamento.

    Args:
        df (pd.DataFrame): DataFrame.
        method (str): Método de tratamento ('capping', 'removal', 'transformation').
        notas_cols (list): Colunas de notas.

    Returns:
        pd.DataFrame: DataFrame com outliers tratados.
    """
    if notas_cols is None:
        notas_cols = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']

    df_treated = df.copy()

    print(f"\n=== TRATAMENTO DE OUTLIERS ({method}) ===")

    for col in notas_cols:
        if df_treated[col].notna().sum() > 0:
            outliers, bounds, pct = detect_outliers_iqr(df_treated, col)

            if len(outliers) > 0:
                # Criar flag de outlier
                df_treated[f'{col}_OUTLIER'] = False
                outlier_mask = (df_treated[col] < bounds[0]) | (df_treated[col] > bounds[1])
                df_treated.loc[outlier_mask, f'{col}_OUTLIER'] = True

                if method == 'capping':
                    # Aplicar capping com cast para compatibilidade de dtype
                    df_treated.loc[df_treated[col] < bounds[0], col] = np.float32(bounds[0])
                    df_treated.loc[df_treated[col] > bounds[1], col] = np.float32(bounds[1])
                    print(f"  {col}: {len(outliers)} outliers tratados por capping (limites: {bounds[0]:.2f}, {bounds[1]:.2f})")

                elif method == 'removal':
                    # Remover outliers (criar máscara para remoção posterior)
                    df_treated[f'{col}_TO_REMOVE'] = outlier_mask
                    print(f"  {col}: {len(outliers)} outliers marcados para remoção")

                elif method == 'transformation':
                    # Transformação logarítmica (para valores positivos)
                    if (df_treated[col] > 0).all():
                        df_treated.loc[outlier_mask, col] = np.log(df_treated.loc[outlier_mask, col])
                        print(f"  {col}: {len(outliers)} outliers transformados (log)")

    return df_treated

def create_aggregated_features(df):
    """
    Cria features agregadas para maximizar valor de visualização.

    Args:
        df (pd.DataFrame): DataFrame.

    Returns:
        pd.DataFrame: DataFrame com features adicionais.
    """
    df_featured = df.copy()

    notas_cols = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']

    # Score normalizado (z-score) por área
    for col in notas_cols:
        if df_featured[col].notna().sum() > 0:
            df_featured[f'{col}_ZSCORE'] = (df_featured[col] - df_featured[col].mean()) / df_featured[col].std()

    # Média geral
    df_featured['MEDIA_GERAL'] = df_featured[notas_cols].mean(axis=1)

    # Ranking por grupo
    df_featured['RANKING_GRUPO'] = df_featured.groupby('TP_LOCALIZACAO_ESC')['MEDIA_GERAL'].rank(ascending=False)

    # Categoria de desempenho
    df_featured['CATEGORIA_DESEMPENHO'] = pd.cut(
        df_featured['MEDIA_GERAL'],
        bins=[0, 400, 600, 800, 1000],
        labels=['Baixo', 'Regular', 'Bom', 'Excelente']
    )

    # Indicadores de melhoria
    df_featured['ACIMA_MEDIA_CIENCIAS'] = df_featured['NU_NOTA_CN'] > df_featured['NU_NOTA_CN'].mean()
    df_featured['ACIMA_MEDIA_HUMANAS'] = df_featured['NU_NOTA_CH'] > df_featured['NU_NOTA_CH'].mean()

    return df_featured

def transform_enem_data(df, ano=None):
    """
    Transforma os dados extraídos do ENEM para análise com qualidade e veracidade.

    Args:
        df (pd.DataFrame): DataFrame com dados extraídos.
        ano (int, optional): Ano dos dados. Se None, tenta extrair do DataFrame ou usa padrão.

    Returns:
        dict: Dicionário com DataFrames transformados e métricas de qualidade.
    """
    print("=== INÍCIO DA TRANSFORMAÇÃO COM QUALIDADE ===")

    # 2. Criar coluna de presença geral (presente se todas as notas estão disponíveis - participou de ambos os dias)
    df['PRESENTE'] = df[['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']].notna().all(axis=1)

    # 3. Filtrar apenas presentes
    df_presentes = df[df['PRESENTE']].copy()
    print(f"Registros após filtro de presença: {len(df_presentes)} (removidos: {len(df) - len(df_presentes)})")

    # 4. Imputação rigorosa de dados faltantes
    df_imputed = impute_missing_grades(df_presentes, strategy='median_by_group')

    # 5. Tratamento de outliers
    df_outlier_treated = treat_outliers(df_imputed, method='capping')

    # 6. Remover registros marcados para remoção (se houver)
    removal_cols = [col for col in df_outlier_treated.columns if col.endswith('_TO_REMOVE')]
    if removal_cols:
        removal_mask = df_outlier_treated[removal_cols].any(axis=1)
        df_final = df_outlier_treated[~removal_mask].copy()
        print(f"Registros após remoção de outliers: {len(df_final)} (removidos: {removal_mask.sum()})")
    else:
        df_final = df_outlier_treated.copy()

    # 7. Criar features agregadas para visualização
    df_featured = create_aggregated_features(df_final)

    # 8. Criar grupo de análise baseado em localização
    df_featured['GRUPO_ANALISE'] = df_featured['TP_LOCALIZACAO_ESC'].map({
        1: 'ALTAMIRA - Urbana',
        2: 'ALTAMIRA - Rural'
    }).fillna('DADO NAO INFORMADO')

    # 9. Calcular médias por grupo
    desempenho_grupo = df_featured.groupby('GRUPO_ANALISE').agg({
        'NU_NOTA_CN': 'mean',
        'NU_NOTA_CH': 'mean',
        'NU_NOTA_LC': 'mean',
        'NU_NOTA_MT': 'mean',
        'NU_NOTA_REDACAO': 'mean',
        'MEDIA_GERAL': 'mean'
    }).round(2)

    desempenho_grupo = desempenho_grupo.rename(columns={
        'NU_NOTA_CN': 'CN_Média',
        'NU_NOTA_CH': 'CH_Média',
        'NU_NOTA_LC': 'LC_Média',
        'NU_NOTA_MT': 'MT_Média',
        'NU_NOTA_REDACAO': 'RED_Média',
        'MEDIA_GERAL': 'Média Geral'
    }).reset_index()

    # Adicionar coluna de ano baseada no parâmetro ou extração automática
    if ano is not None:
        desempenho_grupo['ANO'] = ano
    else:
        # Tentar extrair ano do DataFrame se disponível (coluna NU_ANO)
        if 'NU_ANO' in df.columns:
            ano_unico = df['NU_ANO'].dropna().unique()
            if len(ano_unico) == 1:
                desempenho_grupo['ANO'] = int(ano_unico[0])
            else:
                # Se múltiplos anos, usar o ano mais frequente
                desempenho_grupo['ANO'] = int(df['NU_ANO'].mode().iloc[0]) if not df['NU_ANO'].mode().empty else 2023
        else:
            desempenho_grupo['ANO'] = 2023  # Fallback padrão

    # 10. Correlações
    notas_cols = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']
    correlacao_notas = df_featured[notas_cols].corr().round(2)

    # Adicionar coluna de ano à correlação (mesmo valor para todas as linhas)
    correlacao_notas['ANO'] = ano if ano is not None else (df['NU_ANO'].mode().iloc[0] if 'NU_ANO' in df.columns and not df['NU_ANO'].mode().empty else 2023)

    # 11. Estatísticas descritivas após tratamento
    descritivas_notas = df_featured[notas_cols].describe().round(2).T
    descritivas_notas['missing_after_treatment'] = df_featured[notas_cols].isnull().sum()
    descritivas_notas['imputed_count'] = df_featured[[f'{col}_ORIGINAL_MISSING' for col in notas_cols]].sum()
    descritivas_notas['outlier_count'] = df_featured[[f'{col}_OUTLIER' for col in notas_cols]].sum()

    # Adicionar coluna de ano às descritivas
    descritivas_notas['ANO'] = ano if ano is not None else (df['NU_ANO'].mode().iloc[0] if 'NU_ANO' in df.columns and not df['NU_ANO'].mode().empty else 2023)

    # 12. Métricas de qualidade
    quality_metrics = pd.DataFrame([{
        'registros_iniciais': len(df),
        'registros_finais': len(df_featured),
        'remocao_presenca': len(df) - len(df_presentes),
        'imputacao_total': df_featured[[f'{col}_ORIGINAL_MISSING' for col in notas_cols]].sum().sum(),
        'outliers_total': df_featured[[f'{col}_OUTLIER' for col in notas_cols]].sum().sum(),
        'remocao_outliers': len(df_outlier_treated) - len(df_featured) if 'removal' in str(df_outlier_treated) else 0,
        'ANO': ano if ano is not None else (df['NU_ANO'].mode().iloc[0] if 'NU_ANO' in df.columns and not df['NU_ANO'].mode().empty else 2023)
    }])

    # 13. Ausências por grupo e área (calcular do DataFrame original antes do filtro de presença)
    # Primeiro, criar grupo de análise no DataFrame original
    df_original = df.copy()
    df_original['GRUPO_ANALISE'] = df_original['TP_LOCALIZACAO_ESC'].map({
        1: 'ALTAMIRA - Urbana',
        2: 'ALTAMIRA - Rural'
    }).fillna('DADO NAO INFORMADO')

    presenca_cols = ['TP_PRESENCA_CN', 'TP_PRESENCA_CH', 'TP_PRESENCA_LC', 'TP_PRESENCA_MT']
    ausencias_por_grupo = []

    for grupo in df_original['GRUPO_ANALISE'].unique():
        grupo_data = df_original[df_original['GRUPO_ANALISE'] == grupo]
        ausencias_grupo = {'GRUPO_ANALISE': grupo}

        for col in presenca_cols:
            if col in grupo_data.columns:
                # Contar ausências: TP_PRESENCA = 0 (faltou), 2 (eliminado), ou 3 (não compareceu)
                # Também incluir valores nulos como ausências
                ausencias = ((grupo_data[col].isin([0, 2, 3])) | grupo_data[col].isna()).sum()
                area = col.replace('TP_PRESENCA_', '').replace('_', ' ')
                ausencias_grupo[f'Ausências_{area}'] = ausencias
            else:
                # Se coluna não existe, assumir 0 ausências
                area = col.replace('TP_PRESENCA_', '').replace('_', ' ')
                ausencias_grupo[f'Ausências_{area}'] = 0

        # Para redação, contar ausências baseado em notas faltantes (não há TP_PRESENCA_REDACAO)
        ausencias_red = grupo_data['NU_NOTA_REDACAO'].isna().sum()
        ausencias_grupo['Ausências_REDACAO'] = ausencias_red

        ausencias_por_grupo.append(ausencias_grupo)

    df_ausencias_grupo = pd.DataFrame(ausencias_por_grupo)

    # Adicionar coluna de ano às ausências
    df_ausencias_grupo['ANO'] = ano if ano is not None else (df['NU_ANO'].mode().iloc[0] if 'NU_ANO' in df.columns and not df['NU_ANO'].mode().empty else 2023)

    # 14. Dependência administrativa (se disponível)
    if 'TP_DEPENDENCIA_ADM_ESC' in df_featured.columns:
        df_featured['DEPENDENCIA_ADM'] = df_featured['TP_DEPENDENCIA_ADM_ESC'].map({
            1: 'Federal',
            2: 'Estadual',
            3: 'Municipal',
            4: 'Privada'
        }).fillna('Não informado')

        desempenho_dependencia = df_featured.groupby('DEPENDENCIA_ADM').agg({
            'NU_NOTA_CN': 'mean',
            'NU_NOTA_CH': 'mean',
            'NU_NOTA_LC': 'mean',
            'NU_NOTA_MT': 'mean',
            'NU_NOTA_REDACAO': 'mean',
            'MEDIA_GERAL': 'mean'
        }).round(2)

        desempenho_dependencia['Média Geral'] = desempenho_dependencia[['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']].mean(axis=1).round(2)
        desempenho_dependencia = desempenho_dependencia.reset_index()

        # Adicionar coluna de ano à dependência
        desempenho_dependencia['ANO'] = ano if ano is not None else (df['NU_ANO'].mode().iloc[0] if 'NU_ANO' in df.columns and not df['NU_ANO'].mode().empty else 2023)
    else:
        desempenho_dependencia = None

    # 14. Análise de viés após tratamento
    bias_after = {
        'distribuicao_localizacao': df_featured['GRUPO_ANALISE'].value_counts(normalize=True) * 100,
        'distribuicao_dependencia': df_featured['DEPENDENCIA_ADM'].value_counts(normalize=True) * 100 if 'DEPENDENCIA_ADM' in df_featured.columns else None,
        'distribuicao_categoria': df_featured['CATEGORIA_DESEMPENHO'].value_counts(normalize=True) * 100
    }

    return {
        'desempenho_grupo': desempenho_grupo,
        'correlacao_notas': correlacao_notas,
        'descritivas_notas': descritivas_notas,
        'ausencias_grupo': df_ausencias_grupo,
        'desempenho_dependencia': desempenho_dependencia,
        'quality_metrics': quality_metrics,
        'bias_analysis': bias_after,
        'eda_results': None,  # Análise EDA pode ser executada separadamente se necessário
        'data_processed': df_featured,
        'enem_data_processed': df_featured  # Para scatter plots
    }

if __name__ == "__main__":
    # Exemplo de uso
    from ..Extract.extract import extract_enem_data
    df = extract_enem_data("../../DataSources/microdados_enem_2024.csv")
    transformed = transform_enem_data(df)
    print(transformed['desempenho_grupo'])
