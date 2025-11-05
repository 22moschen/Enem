import pandas as pd
import plotly.express as px
import sqlite3
import os
from Consumption.Preview.preview import preview_data
from Consumption.Reports.reports import generate_report
from Consumption.BI.bi_dashboard import *
from ETL.Load.load import create_database_from_csv

# Configurações da página
st.set_page_config(
    page_title="ENEMAnalytics - Altamira 2024",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para verificar e criar banco se necessário
def ensure_database():
    db_path = 'DWStorage/enem_analysis.db'
    if not os.path.exists(db_path):
        st.warning("Banco de dados não encontrado. Tentando executar ETL...")
        csv_path = "DataSources/microdados_enem_2024.csv"
        if os.path.exists(csv_path):
            with st.spinner("Executando ETL automaticamente..."):
                create_database_from_csv(csv_path)
            st.success("ETL executado com sucesso!")
            return True
        else:
            st.error(f"Arquivo CSV não encontrado: {csv_path}. Faça upload ou verifique o caminho.")
            return False
    return True

# Função para carregar dados do banco
@st.cache_data
def load_data():
    db_path = 'DWStorage/enem_analysis.db'
    if not os.path.exists(db_path):
        if not ensure_database():
            return None, None, None, None, None

    conn = sqlite3.connect(db_path)
    try:
        df_desempenho = pd.read_sql_query("SELECT * FROM desempenho_grupo", conn)
        df_correlacao = pd.read_sql_query("SELECT * FROM correlacao_notas", conn)
        df_ausencias = pd.read_sql_query("SELECT * FROM ausencias_grupo", conn)
        df_descritivas = pd.read_sql_query("SELECT * FROM descritivas_notas", conn)
        try:
            df_dependencia = pd.read_sql_query("SELECT * FROM desempenho_dependencia", conn)
        except:
            df_dependencia = None
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None, None, None, None, None
    finally:
        conn.close()

    return df_desempenho, df_correlacao, df_ausencias, df_descritivas, df_dependencia

# Carregar dados
df_desempenho, df_correlacao, df_ausencias, df_descritivas, df_dependencia = load_data()

# Sidebar
st.sidebar.title("📊 ENEMAnalytics")
st.sidebar.markdown("Análise completa dos microdados do ENEM 2024 para Altamira-PA.")
st.sidebar.markdown("---")

# Botão para executar ETL se necessário
if st.sidebar.button("🔄 Executar ETL (se dados não carregados)"):
    csv_path = st.sidebar.text_input("Caminho para microdados_enem_2024.csv", "DataSources/microdados_enem_2024.csv")
    if os.path.exists(csv_path):
        with st.spinner("Executando ETL..."):
            create_database_from_csv(csv_path)
        st.success("ETL executado! Recarregue a página.")
        st.rerun()
    else:
        st.error(f"Arquivo CSV não encontrado: {csv_path}")

st.sidebar.markdown("---")

# Filtros globais
if df_desempenho is not None:
    selected_groups = st.sidebar.multiselect(
        "Selecionar Grupos para Análise",
        options=df_desempenho['GRUPO_ANALISE'].tolist(),
        default=df_desempenho['GRUPO_ANALISE'].tolist()
    )

    # Métricas dinâmicas
    if selected_groups:
        df_filtered = df_desempenho[df_desempenho['GRUPO_ANALISE'].isin(selected_groups)]
        melhor_media = df_filtered['Média Geral'].max()
        pior_media = df_filtered['Média Geral'].min()
        diff = melhor_media - pior_media
        st.sidebar.metric("Melhor Média (Filtrada)", f"{melhor_media:.2f}")
        st.sidebar.metric("Diferença Máxima", f"{diff:.2f}")

# Título principal
st.title("🎓 ENEMAnalytics - Análise de Desempenho Altamira 2024")
st.markdown("Dashboard interativo para exploração completa dos dados do ENEM 2024 em Altamira-PA.")

# Verificar se dados foram carregados
if df_desempenho is None:
    st.warning("Dados não carregados. Execute o ETL na sidebar ou verifique se o banco existe.")
    st.stop()

# Tabs principais
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Desempenho", "🔗 Correlações", "📊 Estatísticas", "📋 Relatórios", "🔍 Preview"])

with tab1:
    st.header("Desempenho por Grupo de Análise")

    if selected_groups:
        df_plot = df_desempenho[df_desempenho['GRUPO_ANALISE'].isin(selected_groups)]
    else:
        df_plot = df_desempenho

    # Gráfico de barras - Média Geral
    fig_bar = px.bar(
        df_plot,
        x='GRUPO_ANALISE',
        y='Média Geral',
        title='Média Geral por Grupo',
        color='GRUPO_ANALISE',
        text='Média Geral'
    )
    fig_bar.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    st.plotly_chart(fig_bar, width='stretch')

    # Gráfico de radar para todas as áreas
    fig_radar = px.line_polar(
        df_plot.melt(id_vars='GRUPO_ANALISE', value_vars=['CN_Média', 'CH_Média', 'LC_Média', 'MT_Média', 'RED_Média']),
        r='value',
        theta='variable',
        color='GRUPO_ANALISE',
        line_close=True,
        title='Perfil de Desempenho por Área'
    )
    st.plotly_chart(fig_radar, width='stretch')

    # Tabela detalhada
    st.subheader("Tabela Detalhada")
    st.dataframe(df_plot.style.highlight_max(axis=0), width='stretch')

    # Insights
    st.info("💡 **Insight**: Grupos urbanos tendem a ter médias mais altas, possivelmente devido a melhor infraestrutura educacional.")

with tab2:
    st.header("Correlações entre Áreas do Conhecimento")

    # Heatmap de correlação
    fig_heatmap = px.imshow(
        df_correlacao,
        text_auto='.2f',
        title='Matriz de Correlação entre Notas',
        color_continuous_scale='RdBu_r'
    )
    st.plotly_chart(fig_heatmap, width='stretch')

    # Scatter plots para correlações principais
    col1, col2 = st.columns(2)

    with col1:
        # Exemplo de scatter plot (dados fictícios para demonstração)
        import numpy as np
        x = np.random.randn(100)
        y = np.random.randn(100)
        fig_scatter1 = px.scatter(
            x=x, y=y,
            title='Exemplo: Correlação entre Áreas',
            labels={'x': 'Nota Área 1', 'y': 'Nota Área 2'}
        )
        st.plotly_chart(fig_scatter1)

    with col2:
        # Outro exemplo
        x2 = np.random.randn(100)
        y2 = np.random.randn(100)
        fig_scatter2 = px.scatter(
            x=x2, y=y2,
            title='Exemplo: Distribuição de Notas',
            labels={'x': 'Nota CN', 'y': 'Nota Redação'}
        )
        st.plotly_chart(fig_scatter2)

    st.info("💡 **Insight**: Correlações positivas indicam que alunos fortes em uma área tendem a performar bem em outras, sugerindo benefícios de abordagens integradas no ensino.")

with tab3:
    st.header("Estatísticas Descritivas e Ausências")

    # Estatísticas descritivas
    st.subheader("Distribuição das Notas")
    fig_box = px.box(
        df_descritivas.reset_index(),
        x='index',
        y=['mean', '50%', 'min', 'max'],
        title='Distribuição das Notas por Área'
    )
    st.plotly_chart(fig_box, width='stretch')

    st.dataframe(df_descritivas.style.format("{:.2f}"), width='stretch')

    # Ausências
    st.subheader("Ausências por Grupo e Área")
    df_ausencias_plot = df_ausencias.melt(id_vars='GRUPO_ANALISE', var_name='Área', value_name='Ausências')
    fig_ausencias = px.bar(
        df_ausencias_plot,
        x='GRUPO_ANALISE',
        y='Ausências',
        color='Área',
        title='Ausências por Grupo e Área',
        barmode='group'
    )
    st.plotly_chart(fig_ausencias, width='stretch')

    st.info("💡 **Insight**: Áreas com mais ausências podem indicar dificuldades específicas ou falta de preparação em determinadas matérias.")

    # Dependência administrativa (se disponível)
    if df_dependencia is not None:
        st.subheader("Desempenho por Dependência Administrativa")
        fig_dep = px.bar(
            df_dependencia,
            x='DEPENDENCIA_ADM',
            y='Média Geral',
            title='Média Geral por Tipo de Escola',
            color='DEPENDENCIA_ADM'
        )
        st.plotly_chart(fig_dep, width='stretch')

with tab4:
    st.header("Relatórios e Exportação")

    # Gerar relatório PDF
    if st.button("📄 Gerar Relatório PDF"):
        with st.spinner("Gerando relatório..."):
            generate_report()
        st.success("Relatório 'relatorio_enem.pdf' gerado com sucesso!")

    # Exportar dados
    st.subheader("Exportar Dados")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📥 Exportar Desempenho (CSV)"):
            df_desempenho.to_csv("desempenho_grupo.csv", index=False)
            st.success("Arquivo 'desempenho_grupo.csv' salvo!")

    with col2:
        if st.button("📥 Exportar Correlações (CSV)"):
            df_correlacao.to_csv("correlacao_notas.csv", index=False)
            st.success("Arquivo 'correlacao_notas.csv' salvo!")

    with col3:
        if st.button("📥 Exportar Estatísticas (CSV)"):
            df_descritivas.to_csv("descritivas_notas.csv", index=False)
            st.success("Arquivo 'descritivas_notas.csv' salvo!")

    # Resumo executivo
    st.subheader("Resumo Executivo")
    st.markdown(f"""
    - **Total de Grupos Analisados**: {len(df_desempenho)}
    - **Melhor Desempenho**: {df_desempenho.loc[df_desempenho['Média Geral'].idxmax(), 'GRUPO_ANALISE']} ({df_desempenho['Média Geral'].max():.2f})
    - **Pior Desempenho**: {df_desempenho.loc[df_desempenho['Média Geral'].idxmin(), 'GRUPO_ANALISE']} ({df_desempenho['Média Geral'].min():.2f})
    - **Diferença Máxima**: {df_desempenho['Média Geral'].max() - df_desempenho['Média Geral'].min():.2f} pontos
    """)

with tab5:
    st.header("Preview dos Dados")
    preview_data()

# Footer
st.markdown("---")
st.markdown("**Fonte**: Microdados ENEM 2024 - Altamira, PA | **Análise**: ENEMAnalytics")
st.markdown("**Desenvolvido com**: Streamlit, Pandas, Plotly, SQLite")
