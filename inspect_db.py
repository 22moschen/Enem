import sqlite3
import pandas as pd

conn = sqlite3.connect('DWStorage/enem_analysis.db')

# Verificar colunas da tabela data_processed
cursor = conn.cursor()
cursor.execute('PRAGMA table_info(data_processed)')
columns = cursor.fetchall()
print('Colunas da tabela data_processed:')
for col in columns:
    print(f"  {col[1]}")

# Verificar valores únicos de presença por grupo
print('\nValores únicos de presença por grupo:')
df_presenca = pd.read_sql_query('SELECT GRUPO_ANALISE, TP_PRESENCA_CN, TP_PRESENCA_CH, TP_PRESENCA_LC, TP_PRESENCA_MT FROM data_processed', conn)
for grupo in df_presenca['GRUPO_ANALISE'].unique():
    grupo_data = df_presenca[df_presenca['GRUPO_ANALISE'] == grupo]
    print(f"Grupo {grupo}:")
    for col in ['TP_PRESENCA_CN', 'TP_PRESENCA_CH', 'TP_PRESENCA_LC', 'TP_PRESENCA_MT']:
        unique_vals = grupo_data[col].unique()
        print(f"  {col}: {unique_vals}")

# Contar total de alunos por grupo
print('\nTotal de alunos por grupo:')
df_total = pd.read_sql_query('SELECT GRUPO_ANALISE, COUNT(*) as total_alunos FROM data_processed GROUP BY GRUPO_ANALISE', conn)
print(df_total)

# Verificar ausências por grupo e área
print('\nAusências por grupo e área:')
df_ausencias = pd.read_sql_query('SELECT * FROM ausencias_grupo', conn)
print(df_ausencias)

conn.close()
