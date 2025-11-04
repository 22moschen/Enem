import pandas as pd
import sqlite3
from fpdf import FPDF
import os

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Relatório ENEM Altamira 2024', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

def generate_report(db_path='enem_analysis.db', output_path='relatorio_enem.pdf'):
    """
    Gera um relatório PDF com análises principais.
    """
    conn = sqlite3.connect(db_path)

    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Arial', '', 10)

    # Desempenho por grupo
    df_desempenho = pd.read_sql_query("SELECT * FROM desempenho_grupo", conn)
    pdf.cell(0, 10, 'Desempenho por Grupo de Análise', 0, 1)
    for _, row in df_desempenho.iterrows():
        pdf.cell(0, 10, f"{row['GRUPO_ANALISE']}: Média Geral {row['Média Geral']:.2f}", 0, 1)

    # Correlações
    df_corr = pd.read_sql_query("SELECT * FROM correlacao_notas", conn)
    pdf.add_page()
    pdf.cell(0, 10, 'Matriz de Correlação', 0, 1)
    # Simples representação textual
    corr_text = df_corr.to_string()
    pdf.multi_cell(0, 5, corr_text)

    pdf.output(output_path)
    conn.close()
    print(f"Relatório gerado: {output_path}")

if __name__ == "__main__":
    generate_report()
