import pandas as pd
from fpdf import FPDF
import os
from datetime import datetime

def generate_report(selected_year=None, df_desempenho=None, df_correlacao=None, df_descritivas=None):
    """
    Generate a PDF report with ENEM analysis summary
    """
    try:
        # Create PDF
        pdf = FPDF()
        pdf.add_page()

        # Title
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, "ENEMAnalytics - Relatorio de Analise", ln=True, align="C")

        # Date and Year
        pdf.set_font("Arial", "", 12)
        pdf.cell(200, 10, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="C")
        if selected_year:
            pdf.cell(200, 10, f"Ano de Analise: {selected_year}", ln=True, align="C")
        pdf.ln(10)

        # Summary
        pdf.set_font("Arial", "B", 14)
        pdf.cell(200, 10, "Resumo Executivo", ln=True)
        pdf.ln(5)

        pdf.set_font("Arial", "", 12)
        summary_text = f"""
        Este relatorio apresenta uma analise completa dos dados do ENEM
        para Altamira-PA, incluindo metricas de desempenho, correlacoes
        entre areas do conhecimento e estatisticas descritivas.

        Os dados foram processados seguindo rigorosos padroes estatisticos
        e estao prontos para tomada de decisoes educacionais.
        """

        # Split text into lines for PDF
        lines = summary_text.strip().split('\n')
        for line in lines:
            pdf.cell(200, 8, line.strip(), ln=True)

        pdf.ln(10)

        # Detailed Analysis Section
        if df_desempenho is not None and not df_desempenho.empty:
            pdf.set_font("Arial", "B", 14)
            pdf.cell(200, 10, "Metricas de Desempenho", ln=True)
            pdf.ln(5)

            pdf.set_font("Arial", "", 12)
            melhor_grupo = df_desempenho.loc[df_desempenho['Média Geral'].idxmax(), 'GRUPO_ANALISE']
            melhor_media = df_desempenho['Média Geral'].max()
            pior_grupo = df_desempenho.loc[df_desempenho['Média Geral'].idxmin(), 'GRUPO_ANALISE']
            pior_media = df_desempenho['Média Geral'].min()
            diferenca = melhor_media - pior_media

            pdf.cell(200, 8, f"Melhor Desempenho: {melhor_grupo} - Media Geral: {melhor_media:.2f}", ln=True)
            pdf.cell(200, 8, f"Pior Desempenho: {pior_grupo} - Media Geral: {pior_media:.2f}", ln=True)
            pdf.cell(200, 8, f"Diferenca Maxima: {diferenca:.2f} pontos", ln=True)
            pdf.cell(200, 8, f"Total de Grupos Analisados: {len(df_desempenho)}", ln=True)
            pdf.ln(5)

        # Correlation Analysis
        if df_correlacao is not None and not df_correlacao.empty:
            pdf.set_font("Arial", "B", 14)
            pdf.cell(200, 10, "Analise de Correlacoes", ln=True)
            pdf.ln(5)

            pdf.set_font("Arial", "", 12)
            pdf.cell(200, 8, "Principais correlacoes encontradas entre as areas do conhecimento:", ln=True)
            pdf.ln(3)

            # Get correlation values
            corr_data = df_correlacao.drop('ANO', axis=1) if 'ANO' in df_correlacao.columns else df_correlacao
            corr_matrix = corr_data.values

            # Find strongest correlations
            areas = ['CN', 'CH', 'LC', 'MT', 'RED']
            strong_correlations = []
            for i in range(len(areas)):
                for j in range(i+1, len(areas)):
                    corr_value = corr_matrix[i, j]
                    if abs(corr_value) > 0.3:  # Only significant correlations
                        strength = "Forte" if abs(corr_value) > 0.6 else "Moderada"
                        direction = "Positiva" if corr_value > 0 else "Negativa"
                        strong_correlations.append(f"{areas[i]} x {areas[j]}: {corr_value:.3f} ({strength} {direction})")

            for corr in strong_correlations[:5]:  # Top 5 correlations
                pdf.cell(200, 6, f"- {corr}", ln=True)

            pdf.ln(5)

        # Descriptive Statistics
        if df_descritivas is not None and not df_descritivas.empty:
            pdf.set_font("Arial", "B", 14)
            pdf.cell(200, 10, "Estatisticas Descritivas", ln=True)
            pdf.ln(5)

            pdf.set_font("Arial", "", 12)
            pdf.cell(200, 8, "Distribuicao das notas por area do conhecimento:", ln=True)
            pdf.ln(3)

            for area in df_descritivas.index:
                mean_val = df_descritivas.loc[area, 'mean']
                std_val = df_descritivas.loc[area, 'std']
                min_val = df_descritivas.loc[area, 'min']
                max_val = df_descritivas.loc[area, 'max']
                pdf.cell(200, 6, f"{area}: Media={mean_val:.2f}, DP={std_val:.2f}, Min={min_val:.2f}, Max={max_val:.2f}", ln=True)

        # Save PDF
        pdf.output("relatorio_enem.pdf")

        return True

    except Exception as e:
        print(f"Erro ao gerar relatorio: {e}")
        # Create a simple text file as fallback
        with open("relatorio_enem.txt", "w", encoding="utf-8") as f:
            f.write("ENEMAnalytics - Relatorio de Analise\n")
            f.write(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
            if selected_year:
                f.write(f"Ano de Analise: {selected_year}\n")
            f.write("\nEste relatorio apresenta uma analise completa dos dados do ENEM para Altamira-PA.\n")
        return False
