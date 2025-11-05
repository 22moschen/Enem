import pandas as pd
import sqlite3
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

def generate_report(db_path='enem_analysis.db', output_path='relatorio_enem.pdf'):
    """
    Gera um relatório PDF com análises principais usando ReportLab.
    """
    conn = sqlite3.connect(db_path)

    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter

    # Título
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 50, "Relatório ENEM Altamira 2024")

    y_position = height - 80

    # Desempenho por grupo
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_position, "Desempenho por Grupo de Análise")
    y_position -= 20

    df_desempenho = pd.read_sql_query("SELECT * FROM desempenho_grupo", conn)
    c.setFont("Helvetica", 10)
    for _, row in df_desempenho.iterrows():
        c.drawString(50, y_position, f"{row['GRUPO_ANALISE']}: Média Geral {row['Média Geral']:.2f}")
        y_position -= 15
        if y_position < 50:
            c.showPage()
            y_position = height - 50

    # Correlações
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_position, "Matriz de Correlação")
    y_position -= 20

    df_corr = pd.read_sql_query("SELECT * FROM correlacao_notas", conn)
    c.setFont("Helvetica", 8)
    corr_text = df_corr.to_string()
    lines = corr_text.split('\n')
    for line in lines:
        c.drawString(50, y_position, line)
        y_position -= 12
        if y_position < 50:
            c.showPage()
            y_position = height - 50

    c.save()
    conn.close()
    print(f"Relatório gerado: {output_path}")

if __name__ == "__main__":
    generate_report()
