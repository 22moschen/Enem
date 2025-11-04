import streamlit as st
import pandas as pd
import sqlite3

def preview_data(db_path='enem_analysis.db'):
    """
    Função para preview rápido dos dados no banco.
    """
    st.title("Preview dos Dados ENEM Altamira 2024")

    conn = sqlite3.connect(db_path)
    tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)

    for table in tables['name']:
        st.subheader(f"Tabela: {table}")
        df = pd.read_sql_query(f"SELECT * FROM {table} LIMIT 10", conn)
        st.dataframe(df)

    conn.close()

if __name__ == "__main__":
    preview_data()
