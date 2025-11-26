import sqlite3
import pandas as pd

def clean_duplicate_data():
    """
    Remove registros duplicados das tabelas principais, mantendo apenas uma cópia por grupo e ano.
    """
    db_path = 'DWStorage/enem_analysis.db'
    conn = sqlite3.connect(db_path)

    try:
        # Tabelas a limpar
        tables_to_clean = ['desempenho_grupo', 'correlacao_notas', 'descritivas_notas', 'ausencias_grupo', 'desempenho_dependencia']

        for table in tables_to_clean:
            try:
                # Verificar se tabela existe
                cursor = conn.cursor()
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                if not cursor.fetchone():
                    print(f"Tabela {table} não existe. Pulando...")
                    continue

                # Verificar se tem coluna ANO
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [col[1] for col in cursor.fetchall()]
                has_year = 'ANO' in columns

                if has_year:
                    # Contar duplicatas antes da limpeza
                    count_before = pd.read_sql_query(f"SELECT COUNT(*) as total FROM {table}", conn).iloc[0]['total']

                    # Criar tabela temporária com dados únicos
                    # Para desempenho_grupo, manter uma linha por GRUPO_ANALISE e ANO
                    if table == 'desempenho_grupo':
                        unique_query = f"""
                        SELECT * FROM (
                            SELECT *,
                                   ROW_NUMBER() OVER (PARTITION BY GRUPO_ANALISE, ANO ORDER BY rowid) as rn
                            FROM {table}
                        ) WHERE rn = 1
                        """
                    else:
                        # Para outras tabelas, manter uma linha por ANO
                        unique_query = f"""
                        SELECT * FROM (
                            SELECT *,
                                   ROW_NUMBER() OVER (PARTITION BY ANO ORDER BY rowid) as rn
                            FROM {table}
                        ) WHERE rn = 1
                        """

                    # Criar tabela temporária
                    conn.execute(f"CREATE TABLE {table}_temp AS {unique_query}")

                    # Substituir tabela original
                    conn.execute(f"DROP TABLE {table}")
                    conn.execute(f"ALTER TABLE {table}_temp RENAME TO {table}")

                    # Contar após limpeza
                    count_after = pd.read_sql_query(f"SELECT COUNT(*) as total FROM {table}", conn).iloc[0]['total']

                    print(f"Tabela {table}: {count_before} -> {count_after} registros (removidos {count_before - count_after} duplicatas)")
                else:
                    print(f"Tabela {table} não tem coluna ANO. Pulando...")

            except Exception as e:
                print(f"Erro ao limpar tabela {table}: {e}")

        # Limpar tabela enem_data_processed (dados originais)
        try:
            count_before = pd.read_sql_query("SELECT COUNT(*) as total FROM enem_data_processed", conn).iloc[0]['total']

            # Manter apenas registros únicos por NU_INSCRICAO e ANO
            conn.execute("""
                CREATE TABLE enem_data_processed_temp AS
                SELECT * FROM (
                    SELECT *,
                           ROW_NUMBER() OVER (PARTITION BY NU_INSCRICAO, ANO ORDER BY rowid) as rn
                    FROM enem_data_processed
                ) WHERE rn = 1
            """)

            conn.execute("DROP TABLE enem_data_processed")
            conn.execute("ALTER TABLE enem_data_processed_temp RENAME TO enem_data_processed")

            count_after = pd.read_sql_query("SELECT COUNT(*) as total FROM enem_data_processed", conn).iloc[0]['total']
            print(f"Tabela enem_data_processed: {count_before} -> {count_after} registros (removidos {count_before - count_after} duplicatas)")

        except Exception as e:
            print(f"Erro ao limpar enem_data_processed: {e}")

        # Limpar tabela quality_metrics
        try:
            count_before = pd.read_sql_query("SELECT COUNT(*) as total FROM quality_metrics", conn).iloc[0]['total']

            # Manter apenas uma linha por ANO
            conn.execute("""
                CREATE TABLE quality_metrics_temp AS
                SELECT * FROM (
                    SELECT *,
                           ROW_NUMBER() OVER (PARTITION BY ANO ORDER BY rowid) as rn
                    FROM quality_metrics
                ) WHERE rn = 1
            """)

            conn.execute("DROP TABLE quality_metrics")
            conn.execute("ALTER TABLE quality_metrics_temp RENAME TO quality_metrics")

            count_after = pd.read_sql_query("SELECT COUNT(*) as total FROM quality_metrics", conn).iloc[0]['total']
            print(f"Tabela quality_metrics: {count_before} -> {count_after} registros (removidos {count_before - count_after} duplicatas)")

        except Exception as e:
            print(f"Erro ao limpar quality_metrics: {e}")

        # Recriar índices após limpeza
        tables_with_year = ['desempenho_grupo', 'correlacao_notas', 'descritivas_notas', 'ausencias_grupo', 'desempenho_dependencia', 'enem_data_processed']
        for table in tables_with_year:
            try:
                conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_ano ON {table}(ANO)")
                print(f"Índice recriado para {table}")
            except Exception as e:
                print(f"Erro ao recriar índice para {table}: {e}")

        conn.commit()
        print("✅ Limpeza de duplicatas concluída!")

    except Exception as e:
        print(f"Erro geral na limpeza: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    clean_duplicate_data()
