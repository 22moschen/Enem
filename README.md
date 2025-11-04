# ENEMAnalytics

Repositório para o desenvolvimento do projeto de experiência aplicada em dados do 4° período da faculdade Serra Dourada de Altamira.

## Problemáticas Identificadas

O projeto ENEMAnalytics aborda os seguintes desafios educacionais em Altamira-PA:

- **Desigualdade Educacional**: Diferenças significativas de desempenho entre estudantes de áreas urbanas e rurais, com médias que variam em até 50 pontos.
- **Falta de Insights Açãoáveis**: Dados do ENEM disponíveis publicamente, mas sem ferramentas acessíveis para análise local e tomada de decisões.
- **Ausências Sistemáticas**: Taxas elevadas de ausência em provas específicas, indicando possíveis barreiras de acesso ou preparação inadequada.
- **Correlações entre Áreas**: Alunos fortes em uma disciplina tendem a performar bem em outras, sugerindo benefícios de abordagens integradas no ensino.
- **Viés de Seleção**: Análises limitadas apenas a estudantes presentes, potencialmente subestimando desigualdades reais.

## Metodologias Abordadas

- **Análise Exploratória de Dados (EDA)**: Estatísticas descritivas, distribuições e correlações para entender padrões.
- **Segmentação por Grupos**: Análise comparativa entre urbano/rural e tipos de escola (federal, estadual, municipal, privada).
- **Visualização Interativa**: Dashboards dinâmicos com filtros para exploração personalizada dos dados.
- **ETL (Extract, Transform, Load)**: Pipeline robusto para processamento de microdados do ENEM.
- **Business Intelligence**: KPIs e métricas para monitoramento de desempenho educacional.

## Como o Projeto Soluciona as Problemáticas

- **Ferramentas de Análise Acessíveis**: Dashboard web interativo permite que educadores e gestores explorem dados sem conhecimento técnico avançado.
- **Insights Geográficos**: Comparações urbano/rural ajudam a identificar regiões que precisam de mais investimentos.
- **Análises de Correlação**: Mostra como intervenções em uma área podem impactar outras disciplinas.
- **Relatórios Automatizados**: Geração de documentos PDF para compartilhamento de descobertas.
- **Transparência de Dados**: Código aberto e documentado facilita replicação em outros municípios.

## Como Fizemos

### Desenvolvimento do Pipeline ETL
- Implementamos scripts modulares em Python para extração, transformação e carga dos dados.
- Utilizamos Pandas para manipulação eficiente de grandes volumes de dados.
- Criamos funções reutilizáveis para diferentes fontes de dados (CSV, Excel).

### Construção do Dashboard
- Desenvolvemos interface web com Streamlit, focada na usabilidade.
- Integramos gráficos interativos com Plotly Express para visualizações dinâmicas.
- Implementamos sistema de filtros para análises personalizadas.

### Validação e Testes
- Criamos scripts de debug para verificar integridade dos dados durante o processamento.
- Testamos o pipeline ETL com diferentes cenários de dados.
- Validamos visualizações com usuários finais para feedback de usabilidade.

## Tecnologias Utilizadas

- **Linguagem Principal**: Python 3.13.7+
- **Bibliotecas de Dados**:
  - `pandas`: Manipulação e análise de dados estruturados
  - `sqlite3`: Banco de dados relacional para armazenamento local
- **Visualização**:
  - `streamlit`: Framework para criação de dashboards web interativos
  - `plotly.express`: Biblioteca para gráficos dinâmicos e interativos
- **Relatórios**:
  - `reportlab`: Geração de documentos PDF
- **Controle de Versão**: Git e GitHub
- **Ambiente Virtual**: venv (Python virtual environment)

## Problemas Encontrados Durante o Desenvolvimento e Soluções

### Problema 1: Estrutura de Dados Complexa dos Microdados ENEM
- **Descrição**: Arquivos CSV com 90+ colunas, encoding inconsistente, dados faltantes.
- **Solução**: Implementamos leitura seletiva de colunas relevantes, tratamento de encoding 'latin1', e filtros para Altamira-PA.

### Problema 2: Merge de Dados de Múltiplas Fontes
- **Descrição**: Arquivos de participantes e resultados sem chaves de junção diretas.
- **Solução**: Utilizamos merge por município (CO_MUNICIPIO_PROVA) e criamos scripts de debug para validar integridade.

### Problema 3: Performance com Grandes Volumes de Dados
- **Descrição**: Processamento lento de milhares de registros durante transformação.
- **Solução**: Otimizamos operações com Pandas (uso de .copy(), filtros eficientes) e implementamos cache com @st.cache_data no Streamlit.

### Problema 4: Tratamento de Valores Ausentes
- **Descrição**: Notas zero vs. ausências reais, dados "NÃO INFORMADO".
- **Solução**: Criamos lógica específica para diferenciar ausências de notas zero, usando TP_PRESENCA_* para validação.

### Problema 5: Dependências de Caminhos de Arquivos
- **Descrição**: Scripts hardcoded com caminhos relativos que quebravam em diferentes ambientes.
- **Solução**: Implementamos configuração dinâmica de caminhos e validação de existência de arquivos.

## Arquitetura do Projeto

O projeto segue uma arquitetura em camadas bem definida, inspirada em data warehouses modernos:

### DataSources
**Função**: Armazenamento de dados brutos e fontes originais.
- Contém microdados do ENEM em formato CSV/Excel
- Arquivos tratados específicos de Altamira-PA
- **Responsabilidades**: Centralizar todas as fontes de dados, manter histórico de versões

### ETL (Extract, Transform, Load)
**Função**: Processamento e padronização dos dados.

#### Extract
- Lê dados de múltiplas fontes (CSV, Excel)
- Filtra registros relevantes (apenas Altamira-PA)
- Trata problemas de encoding e formato
- **Saída**: DataFrame Pandas com dados brutos filtrados

#### Transform
- Limpa e padroniza dados (tratamento de nulos, conversões)
- Cria agrupamentos por localização e dependência administrativa
- Calcula métricas agregadas (médias, correlações, estatísticas)
- **Saída**: Dicionário de DataFrames transformados

#### Load
- Carrega dados transformados para SQLite
- Cria tabelas otimizadas para consultas
- Garante integridade referencial
- **Saída**: Banco de dados estruturado

### DWStorage (Data Warehouse Storage)
**Função**: Armazenamento estruturado dos dados processados.
- Banco SQLite com tabelas otimizadas
- Esquemas seccionados por tipo de análise
- **Tabelas principais**:
  - `desempenho_grupo`: Médias por urbano/rural
  - `correlacao_notas`: Matriz de correlações
  - `ausencias_grupo`: Contagem de ausências
  - `descritivas_notas`: Estatísticas descritivas
  - `desempenho_dependencia`: Médias por tipo de escola

### Consumption
**Função**: Interfaces para consumo e visualização dos dados.

#### Preview
- Visualização rápida dos dados processados
- Tabelas interativas para inspeção
- **Arquivo**: `Consumption/Preview/preview.py`

#### Reports
- Geração automatizada de relatórios PDF
- Resumos executivos com métricas principais
- **Arquivo**: `Consumption/Reports/reports.py`

#### BI (Business Intelligence)
- Dashboard completo com KPIs e gráficos
- Análises avançadas e comparações
- **Arquivo**: `Consumption/BI/bi_dashboard.py`

### GaS (Governance and Security)
**Função**: Governança, documentação e controle de acesso.
- Documentação de metadados e processos
- Definição de níveis de acesso aos dados
- Pesquisa e catalogação de dados
- **Arquivo**: `GaS/research.txt`

## Pré-requisitos

- **Sistema Operacional**: Windows 10/11, Linux ou macOS
- **Python**: Versão 3.8 ou superior (recomendado 3.13.7+)
- **Git**: Para controle de versão e clonagem do repositório
- **Navegador Web**: Chrome, Firefox ou Edge (para acessar o dashboard)
- **Espaço em Disco**: Pelo menos 500MB livres para dados e dependências

## Como Clonar o Repositório

```bash
# Clone o repositório
git clone https://github.com/Felipe-Gabriel-Menezes-Lacerda/ENEMAnalytics.git

# Entre no diretório do projeto
cd ENEMAnalytics
```

## Criar Ambiente Virtual

### Windows
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
venv\Scripts\activate.bat
```

### Linux/macOS
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
source venv/bin/activate
```

## Instalar Todas as Dependências

```bash
# Instalar dependências do projeto
pip install -r requirements.txt
```

**Nota**: O arquivo `requirements.txt` contém todas as bibliotecas necessárias, incluindo Streamlit, Pandas, Plotly, ReportLab, etc.

## Comandos para Rodar o Projeto

### 1. Executar Pipeline ETL (Processar Dados)
```bash
# Executar ETL completo com arquivos tratados de Altamira
python run_etl.py
```
**Quando usar**: Sempre que precisar processar ou atualizar os dados no banco. Executa extração, transformação e carga automaticamente.

### 2. Executar Dashboard Principal
```bash
# Iniciar aplicação Streamlit principal
streamlit run streamlit_app.py
```
**Quando usar**: Para acessar o dashboard completo com todas as análises. Abre em `http://localhost:8501`.

### 3. Executar Dashboard BI Específico
```bash
# Executar apenas o módulo de Business Intelligence
streamlit run Consumption/BI/bi_dashboard.py
```
**Quando usar**: Para análises focadas em BI, sem as outras abas do dashboard principal.

### 4. Executar Preview dos Dados
```bash
# Visualizar dados brutos processados
streamlit run Consumption/Preview/preview.py
```
**Quando usar**: Para inspeção rápida dos dados no banco, útil durante desenvolvimento ou debug.

### 5. Gerar Relatório PDF
```bash
# Gerar relatório automatizado
python Consumption/Reports/reports.py
```
**Quando usar**: Para criar relatórios em PDF com análises principais. O arquivo é salvo como `relatorio_enem.pdf`.

### 6. Verificar Estrutura do Banco
```bash
# Executar script de verificação
python check_db.py
```
**Quando usar**: Para validar se o banco de dados foi criado corretamente e verificar integridade dos dados.

## Ordem Recomendada de Execução

1. **Primeira vez**: `python run_etl.py` (processa dados)
2. **Exploração**: `streamlit run streamlit_app.py` (dashboard principal)
3. **Análises específicas**: Use os outros comandos conforme necessário
4. **Compartilhamento**: `python Consumption/Reports/reports.py` (gerar PDF)

## Estrutura de Arquivos Final

```
ENEMAnalytics/
├── .git/                          # Controle de versão Git
├── .gitignore                     # Arquivos ignorados
├── README.md                      # Esta documentação completa
├── requirements.txt               # Dependências Python
├── streamlit_app.py               # Dashboard principal
├── run_etl.py                     # Script para executar ETL
├── check_db.py                    # Verificação do banco
├── enem_analysis.db               # Banco SQLite (gerado)
├── relatorio_enem.pdf             # Relatório PDF (gerado)
├── venv/                          # Ambiente virtual (criado localmente)
├── DataSources/                   # Camada de fontes de dados
│   └── tratados_altamira/         # Dados específicos de Altamira
├── ETL/                           # Camada de processamento
│   ├── Extract/                   # Extração de dados
│   ├── Transform/                 # Transformação/modelagem
│   └── Load/                      # Carga para banco
├── DWStorage/                     # Armazenamento estruturado
│   └── enem_analysis.db           # Banco de dados (cópia)
├── Consumption/                   # Interfaces de consumo
│   ├── Preview/                   # Visualização rápida
│   ├── Reports/                   # Geração de relatórios
│   └── BI/                        # Business Intelligence
└── GaS/                           # Governança e documentação
    └── research.txt               # Pesquisa e metadados
```

## Contribuição

Para contribuir:
1. Faça fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

Este projeto é parte de um trabalho acadêmico da Faculdade Serra Dourada de Altamira.

## Suporte

Para dúvidas ou problemas:
- Verifique os logs de erro no terminal
- Execute `python check_db.py` para validar dados
- Consulte a documentação de cada módulo nos comentários do código
