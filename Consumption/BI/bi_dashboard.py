import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3

# Configurações da página
st.set_page_config(
    page_title="BI ENEM Altamira 2024",
    page_icon="📊",
    layout="wide"
)

# Conectar ao banco
conn = sqlite3.connect('enem_analysis.db')
df_desempenho = pd.read_sql_query("SELECT * FROM desempenho_grupo", conn)
df_correlacao = pd.read_sql_query("SELECT * FROM correlacao_notas", conn)
conn.close()

st.title("Business Intelligence - ENEM Altamira 2024")

# KPIs principais
col1, col2, col3 = st.columns(3)
with col1:
    melhor = df_desempenho['Média Geral'].max()
    st.metric("Melhor Média", f"{melhor:.2f}")
with col2:
    pior = df_desempenho['Média Geral'].min()
    st.metric("Pior Média", f"{pior:.2f}")
with col3:
    diff = melhor - pior
    st.metric("Diferença", f"{diff:.2f}")

# Gráfico principal
fig = px.bar(df_desempenho, x='GRUPO_ANALISE', y='Média Geral', title='Desempenho por Grupo')
st.plotly_chart(fig)

# Heatmap de correlação
st.subheader("Correlações entre Áreas")
fig_corr = px.imshow(df_correlacao.set_index(df_correlacao.columns[0]), text_auto='.2f')
st.plotly_chart(fig_corr)

if __name__ == "__main__":
    st.write("Dashboard BI carregado!")
