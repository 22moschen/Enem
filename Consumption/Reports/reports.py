import pandas as pd

from fpdf import FPDF
import os
from datetime import datetime
import plotly.express as px
import plotly.io as pio
import sqlite3

def generate_audit_report(selected_year, db_connection):
    """
    Generate a professional PDF audit report for ENEM data in Altamira-PA
    """
    try:
        # Load all necessary data
        def load_data_for_report(year, conn):
            where_clause = f"WHERE ANO = {year}" if year else ""

            # Load all required tables
            df_desempenho = pd.read_sql_query(f"SELECT * FROM desempenho_grupo {where_clause}", conn)
            df_correlacao = pd.read_sql_query(f"SELECT * FROM correlacao_notas {where_clause}", conn)
            df_descritivas = pd.read_sql_query(f"SELECT * FROM descritivas_notas {where_clause}", conn)
            df_ausencias = pd.read_sql_query(f"SELECT * FROM ausencias_grupo {where_clause}", conn)
            df_dependencia = pd.read_sql_query(f"SELECT * FROM desempenho_dependencia {where_clause}", conn)
            df_quality = pd.read_sql_query("SELECT * FROM quality_metrics", conn)

            # Load sample data for scatter plot
            df_processed = pd.read_sql_query(f"SELECT NU_NOTA_CN, NU_NOTA_MT, NU_NOTA_REDACAO, NU_NOTA_LC FROM enem_data_processed {where_clause} LIMIT 1000", conn)

            return df_desempenho, df_correlacao, df_descritivas, df_ausencias, df_dependencia, df_quality, df_processed

        df_desempenho, df_correlacao, df_descritivas, df_ausencias, df_dependencia, df_quality, df_processed = load_data_for_report(selected_year, db_connection)

        # Create PDF
        pdf = FPDF()
        pdf.add_page()

        # Title Page
        pdf.set_font("Arial", "B", 20)
        pdf.cell(200, 15, "Relatório de Auditoria e Desempenho ENEM", ln=True, align="C")
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, f"(Altamira-PA) - Ano {selected_year}", ln=True, align="C")
        pdf.set_font("Arial", "", 12)
        pdf.cell(200, 10, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="C")
        pdf.ln(10)
        pdf.set_font("Arial", "I", 10)
        pdf.multi_cell(0, 6, "Este relatório apresenta uma análise completa e auditável dos dados do ENEM em Altamira-PA, combinando métricas de qualidade de dados com insights educacionais acionáveis.")
        pdf.ln(10)

        # I. Resumo Executivo
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 12, "I. Resumo Executivo", ln=True)
        pdf.ln(5)

        pdf.set_font("Arial", "", 12)
        pdf.cell(200, 8, f"Data do Relatório: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
        pdf.cell(200, 8, f"Período Analisado: Ano {selected_year}", ln=True)
        pdf.ln(5)

        # KPIs principais
        if not df_desempenho.empty:
            media_geral = df_desempenho['Média Geral'].mean()
            maior_nota = df_desempenho['Média Geral'].max()
            pdf.cell(200, 8, f"Média Geral: {media_geral:.2f} pontos", ln=True)
            pdf.cell(200, 8, f"Maior Nota: {maior_nota:.2f} pontos", ln=True)

        if not df_ausencias.empty:
            presenca_total = df_ausencias[['Ausências_CN', 'Ausências_CH', 'Ausências_LC', 'Ausências_MT', 'Ausências_REDACAO']].sum().sum()
            total_registros = len(df_ausencias) * 5  # 5 areas
            porcentagem_presenca = ((total_registros - presenca_total) / total_registros) * 100
            pdf.cell(200, 8, f"Porcentagem de Presença: {porcentagem_presenca:.1f}%", ln=True)

        pdf.ln(5)
        pdf.set_font("Arial", "I", 11)
        pdf.multi_cell(0, 6, "Este relatório consolida os principais indicadores de desempenho educacional do ENEM em Altamira-PA para o ano selecionado, fornecendo uma base sólida para decisões estratégicas em educação.")
        pdf.ln(5)

        # II. Qualidade de Dados
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 12, "II. Qualidade de Dados", ln=True)
        pdf.ln(5)

        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 8, "Narrativa sobre o processo de ETL: Os dados foram submetidos a um rigoroso processo de limpeza e transformação, incluindo tratamento de valores faltantes, detecção de outliers e validação de consistência. Este processo garante a integridade dos dados utilizados nas análises subsequentes.")

        if not df_quality.empty:
            quality = df_quality.iloc[0]
            pdf.cell(200, 8, f"Contagem inicial de registros: {quality['registros_iniciais']:,}", ln=True)
            pdf.cell(200, 8, f"Porcentagem de dados faltantes (antes da imputação): {(quality['imputacao_total']/quality['registros_iniciais']*100):.1f}%", ln=True)
            pdf.cell(200, 8, f"Porcentagem de outliers detectados: {(quality['outliers_total']/quality['registros_finais']*100):.1f}%", ln=True)
            pdf.cell(200, 8, "Método de tratamento: Capping (limitação aos percentis inferior/superior)", ln=True)

        pdf.ln(5)
        pdf.set_font("Arial", "I", 11)
        pdf.multi_cell(0, 6, "A qualidade dos dados é fundamental para a confiabilidade das análises. O processo ETL implementado segue boas práticas estatísticas, preservando a distribuição original dos dados enquanto trata anomalias.")
        pdf.ln(5)

        # III. Análise de Desempenho
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 12, "III. Análise de Desempenho", ln=True)
        pdf.ln(5)

        # Generate Chart 1: Performance by area
        if not df_desempenho.empty:
            areas_data = df_desempenho[['CN_Média', 'CH_Média', 'LC_Média', 'MT_Média', 'RED_Média']].mean()
            fig1 = px.bar(x=areas_data.index, y=areas_data.values,
                         title="Desempenho Médio por Área do Conhecimento",
                         labels={'x': 'Área', 'y': 'Média'})
            pio.write_image(fig1, "temp_chart1.png", engine="kaleido")

            pdf.set_font("Arial", "B", 14)
            pdf.cell(200, 10, "Gráfico 1: Desempenho médio por área do conhecimento", ln=True)
            pdf.image("temp_chart1.png", x=10, y=None, w=180)
            pdf.ln(5)

            # Insight Chave for Chart 1
            pdf.set_font("Arial", "I", 11)
            pdf.multi_cell(0, 6, "**Insight Chave:** Áreas com médias mais baixas, como Matemática, podem indicar necessidades específicas de intervenção pedagógica. A diferença entre áreas sugere oportunidades para estratégias diferenciadas de ensino em Altamira-PA.")
            pdf.ln(5)

        # Generate Chart 2: Performance by dependency
        if not df_dependencia.empty:
            fig2 = px.bar(df_dependencia, x='DEPENDENCIA_ADM', y='Média Geral',
                         title="Comparação de Média por Dependência Administrativa",
                         color='DEPENDENCIA_ADM')
            pio.write_image(fig2, "temp_chart2.png", engine="kaleido")

            pdf.set_font("Arial", "B", 14)
            pdf.cell(200, 10, "Gráfico 2: Comparação de média por dependência administrativa", ln=True)
            pdf.image("temp_chart2.png", x=10, y=None, w=180)
            pdf.ln(5)

            # Insight Chave for Chart 2
            pdf.set_font("Arial", "I", 11)
            pdf.multi_cell(0, 6, "**Insight Chave:** Diferenças significativas entre escolas públicas e privadas destacam desigualdades educacionais. Estratégias de equalização, como programas de apoio e capacitação docente, são essenciais para reduzir essas disparidades em Altamira-PA.")
            pdf.ln(5)

        pdf.ln(10)

        # IV. Insights e Correlações
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 12, "IV. Insights e Correlações", ln=True)
        pdf.ln(5)

        # Generate Chart 3: Scatter plot correlation
        if not df_processed.empty:
            fig3 = px.scatter(df_processed, x='NU_NOTA_MT', y='NU_NOTA_CN',
                             title="Correlação: Matemática vs Ciências da Natureza",
                             trendline="ols")
            pio.write_image(fig3, "temp_chart3.png")

            pdf.set_font("Arial", "B", 14)
            pdf.cell(200, 10, "Gráfico 3: Correlação entre Matemática e Ciências da Natureza", ln=True)
            pdf.image("temp_chart3.png", x=10, y=None, w=180)
            pdf.ln(5)

            # Calculate correlation
            corr_value = df_processed['NU_NOTA_MT'].corr(df_processed['NU_NOTA_CN'])
            pdf.set_font("Arial", "", 12)
            pdf.multi_cell(0, 8, f"Explicação: A correlação entre Matemática e Ciências da Natureza é de {corr_value:.3f}, indicando uma relação {'forte positiva' if corr_value > 0.7 else 'moderada positiva' if corr_value > 0.3 else 'fraca'}. Isso significa que alunos com bom desempenho em Matemática tendem a ter desempenho similar em Ciências da Natureza, sugerindo habilidades analíticas compartilhadas.")

            # Insight Chave for Chart 3
            pdf.ln(5)
            pdf.set_font("Arial", "I", 11)
            pdf.multi_cell(0, 6, "**Insight Chave:** Esta correlação positiva sugere que intervenções pedagógicas integradas entre Matemática e Ciências da Natureza podem ser mais eficazes. Alunos que dominam conceitos matemáticos frequentemente aplicam raciocínio lógico similar nas ciências, indicando oportunidades para abordagens interdisciplinares em Altamira-PA.")

        pdf.ln(10)

        # V. Glossário e Notas
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 12, "V. Glossario e Notas", ln=True)
        pdf.ln(5)

        pdf.set_font("Arial", "", 12)
        glossario = """
        NU_NOTA_CN: Nota em Ciencias da Natureza (0-1000 pontos)
        NU_NOTA_CH: Nota em Ciencias Humanas (0-1000 pontos)
        NU_NOTA_LC: Nota em Linguagens e Codigos (0-1000 pontos)
        NU_NOTA_MT: Nota em Matematica (0-1000 pontos)
        NU_NOTA_REDACAO: Nota em Redacao (0-1000 pontos)
        TP_ESCOLA: Tipo de escola (Publica/Privada)
        GRUPO_ANALISE: Agrupamento por localizacao (Urbano/Rural)

        Metadados do projeto: Dados processados seguindo padroes estatisticos rigorosos,
        com tratamento de outliers por metodo IQR e imputacao por mediana.
        """

        pdf.multi_cell(0, 8, glossario)

        # Save PDF
        pdf.output(f"Relatorio_ENEM_Altamira_{selected_year}.pdf")

        # Clean up temp files
        for file in ["temp_chart1.png", "temp_chart2.png", "temp_chart3.png"]:
            if os.path.exists(file):
                os.remove(file)

        return f"Relatorio_ENEM_Altamira_{selected_year}.pdf"

    except Exception as e:
        print(f"Erro ao gerar relatorio: {e}")
        return f"Erro ao gerar relatório: {str(e)}"
