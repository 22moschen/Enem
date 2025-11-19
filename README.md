# ENEMAnalytics

[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red.svg)](https://streamlit.io/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey.svg)](https://www.sqlite.org/)

Repositório para o desenvolvimento do projeto de experiência aplicada em dados do 4° período da faculdade Serra Dourada de Altamira.

**ENEMAnalytics** é uma plataforma completa de análise de dados educacionais que transforma microdados do ENEM em insights acionáveis para gestores e educadores de Altamira-PA, através de um dashboard interativo e pipeline ETL automatizado.

## 🎯 Problemáticas Identificadas

O projeto ENEMAnalytics aborda os seguintes desafios educacionais em Altamira-PA:

- **Desigualdade Educacional**: Diferenças significativas de desempenho entre estudantes de áreas urbanas e rurais, com médias que variam em até 50 pontos.
- **Falta de Insights Açãoáveis**: Dados do ENEM disponíveis publicamente, mas sem ferramentas acessíveis para análise local e tomada de decisões.
- **Ausências Sistemáticas**: Taxas elevadas de ausência em provas específicas, indicando possíveis barreiras de acesso ou preparação inadequada.
- **Correlações entre Áreas**: Alunos fortes em uma disciplina tendem a performar bem em outras, sugerindo benefícios de abordagens integradas no ensino.
- **Viés de Seleção**: Análises limitadas apenas a estudantes presentes, potencialmente subestimando desigualdades reais.

## 🛠️ Metodologias Abordadas

- **Análise Exploratória de Dados (EDA)**: Estatísticas descritivas, distribuições e correlações para entender padrões.
- **Segmentação por Grupos**: Análise comparativa entre urbano/rural e tipos de escola (federal, estadual, municipal, privada).
- **Visualização Interativa**: Dashboards dinâmicos com filtros para exploração personalizada dos dados.
- **ETL (Extract, Transform, Load)**: Pipeline robusto para processamento de microdados do ENEM.
- **Business Intelligence**: KPIs e métricas para monitoramento de desempenho educacional.
- **Qualidade de Dados**: Validações rigorosas, tratamento de outliers e imputação estatística.

## ✅ Como o Projeto Soluciona as Problemáticas

- **Ferramentas de Análise Acessíveis**: Dashboard web interativo permite que educadores e gestores explorem dados sem conhecimento técnico avançado.
- **Insights Geográficos**: Comparações urbano/rural ajudam a identificar regiões que precisam de mais investimentos.
- **Análises de Correlação**: Mostra como intervenções em uma área podem impactar outras disciplinas.
- **Relatórios Automatizados**: Geração de documentos PDF para compartilhamento de descobertas.
- **Transparência de Dados**: Código aberto e documentado facilita replicação em outros municípios.
- **Dados Confiáveis**: Pipeline ETL com validações rigorosas e métricas de qualidade.

## 🚀 Funcionalidades Principais

### 📊 Dashboard Interativo
- **Seleção de Ano**: Análise histórica com suporte a múltiplos anos de dados
- **Filtros Dinâmicos**: Exploração personalizada por grupos e regiões
- **Visualizações Avançadas**: Gráficos interativos com Plotly Express
- **Métricas em Tempo Real**: KPIs atualizados automaticamente
- **Exportação de Dados**: CSV e PDF para relatórios

### 🔄 Pipeline ETL Automatizado
- **Detecção Automática**: Identifica novos arquivos de dados automaticamente
- **Processamento Incremental**: Evita reprocessamento de dados já tratados
- **Controle de Qualidade**: Métricas detalhadas de processamento
- **Suporte Multi-Formato**: CSV, Excel e outros formatos
- **Validações Cruzadas**: Consistência entre presença e notas

### 📈 Análises Disponíveis
- **Desempenho por Grupo**: Urbano vs Rural, tipos de escola
- **Correlações**: Entre todas as áreas do conhecimento
- **Estatísticas Descritivas**: Distribuições, médias, medianas
- **Ausências e Eliminação**: Taxas por área e localização
- **Análise Exploratória**: Qualidade dos dados e validações

## 🏗️ Como Fizemos

### Desenvolvimento do Pipeline ETL
- Implementamos scripts modulares em Python para extração, transformação e carga dos dados.
- Utilizamos Pandas para manipulação eficiente de grandes volumes de dados.
- Criamos funções reutilizáveis para diferentes fontes de dados (CSV, Excel).
- Implementamos sistema de controle de duplicidade para evitar reprocessamento.

### Construção do Dashboard
- Desenvolvemos interface web com Streamlit, focada na usabilidade.
- Integramos gráficos interativos com Plotly Express para visualizações dinâmicas.
- Implementamos sistema de filtros para análises personalizadas.
- Adicionamos seleção de ano para análise histórica.

### Validação e Testes
- Criamos scripts de debug para verificar integridade dos dados durante o processamento.
- Testamos o pipeline ETL com diferentes cenários de dados.
- Validamos visualizações com usuários finais para feedback de usabilidade.
- Implementamos métricas de qualidade e validações rigorosas.

## 💻 Tecnologias Utilizadas

- **Linguagem Principal**: Python 3.11+ (Docker) / 3.13.7+ (Local)
- **Bibliotecas de Dados**:
  - `pandas`: Manipulação e análise de dados estruturados
  - `sqlite3`: Banco de dados relacional para armazenamento local
  - `numpy`: Computação numérica
  - `scikit-learn`: Algoritmos de machine learning
- **Visualização**:
  - `streamlit`: Framework para criação de dashboards web interativos
  - `plotly.express`: Biblioteca para gráficos dinâmicos e interativos
  - `altair`: Visualizações declarativas
- **Relatórios**:
  - `reportlab`: Geração de documentos PDF
  - `fpdf2`: Alternativa para geração de PDF
- **Controle de Versão**:
  - `git`: Controle de versão distribuído
  - `git-lfs`: Gerenciamento de arquivos grandes
- **Containerização**:
  - `docker`: Containerização da aplicação
  - `docker-compose`: Orquestração de serviços
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

## 📋 Pré-requisitos

### Para Execução com Docker (Recomendado)
- **Docker Desktop** (versão 20.10 ou superior)
- **Docker Compose** (versão 2.0 ou superior)
- **Git** (para clonagem do repositório)
- **Git LFS** (para arquivos grandes)
- **Navegador Web** moderno (Chrome, Firefox, Edge, Safari)
- **Espaço em Disco**: Pelo menos 1GB livre para dados e container

### Para Execução Local (Alternativa)
- **Sistema Operacional**: Windows 10/11, Linux ou macOS
- **Python**: Versão 3.8 ou superior (recomendado 3.13.7+)
- **Git**: Para controle de versão e clonagem
- **Git LFS**: Para acessar arquivos grandes (CSV)
- **Navegador Web**: Chrome, Firefox ou Edge
- **Espaço em Disco**: Pelo menos 500MB livres

## 🚀 Instalação e Configuração

### 1. Clonagem do Repositório

```bash
# Clone o repositório
git clone https://github.com/Felipe-Gabriel-Menezes-Lacerda/ENEMAnalytics.git

# Entre no diretório do projeto
cd ENEMAnalytics

# Instalar Git LFS (se não estiver instalado)
git lfs install

# Puxar arquivos grandes
git lfs pull
```

### 2. Configuração Inicial

#### Com Docker (Recomendado)
```bash
# Construir e executar o projeto completo
docker-compose up --build
```

#### Local (Alternativa)
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate.bat
# Linux/macOS:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

## 📖 Guia de Uso

### 🚀 Execução Rápida com Docker (Recomendado)

```bash
# Clone o repositório
git clone https://github.com/Felipe-Gabriel-Menezes-Lacerda/ENEMAnalytics.git
cd ENEMAnalytics

# Instalar Git LFS e baixar arquivos grandes
git lfs install && git lfs pull

# Executar projeto completo
docker-compose up --build
```

**Acesse o dashboard em: http://localhost:8501**

### 🔧 Comandos Avançados com Docker

| Comando | Descrição |
|---------|-----------|
| `docker-compose up --build` | Executa projeto completo (ETL + Dashboard) |
| `docker-compose up -d --build` | Executa em background |
| `docker-compose down` | Para containers |
| `docker-compose logs -f` | Visualiza logs em tempo real |
| `docker-compose restart` | Reinicia containers |

### 📊 Adicionando Novos Dados

Para incluir dados de novos anos do ENEM:

1. **Pare o container**:
   ```bash
   docker-compose down
   ```

2. **Baixe os microdados** do [site oficial do INEP](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem)

3. **Coloque o arquivo** na pasta `DataSources/` (mantenha o nome original)

4. **Reinicie o container**:
   ```bash
   docker-compose up --build
   ```

O sistema detectará automaticamente o novo arquivo e processará os dados.

**⚠️ Importante**: Use apenas arquivos CSV de microdados completos do ENEM, não os reduzidos.

## Execução Local (Alternativa)

### Criar Ambiente Virtual

#### Windows
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
venv\Scripts\activate.bat
```

#### Linux/macOS
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
source venv/bin/activate
```

### Instalar Todas as Dependências

```bash
# Instalar dependências do projeto
pip install -r requirements.txt

# Instalar Git LFS (se necessário para acessar arquivos grandes)
# pip install git-lfs  # Geralmente instalado via sistema operacional
```

**Nota**: O arquivo `requirements.txt` contém todas as bibliotecas necessárias, incluindo Streamlit, Pandas, Plotly, ReportLab, etc. O Git LFS é necessário para baixar os arquivos CSV grandes armazenados no repositório.

### Comandos para Rodar o Projeto Localmente

#### 1. Executar Pipeline ETL Automatizado (Processar Dados)
```bash
# Executar ETL automatizado que detecta novos dados
python automate_etl.py
```
**Quando usar**: Para processar dados automaticamente, incluindo detecção de novos arquivos em DataSources.

#### 2. Executar Pipeline ETL Padrão
```bash
# Executar ETL completo com arquivos tratados de Altamira
python run_etl.py
```
**Quando usar**: Para processamento específico dos dados tratados de Altamira.

#### 3. Executar Dashboard Principal
```bash
# Iniciar aplicação Streamlit principal
streamlit run streamlit_app.py
```
**Quando usar**: Para acessar o dashboard completo com todas as análises. Abre em `http://localhost:8501`.

#### 4. Executar Dashboard BI Específico
```bash
# Executar apenas o módulo de Business Intelligence
streamlit run Consumption/BI/bi_dashboard.py
```
**Quando usar**: Para análises focadas em BI, sem as outras abas do dashboard principal.

#### 5. Executar Preview dos Dados
```bash
# Visualizar dados brutos processados
streamlit run Consumption/Preview/preview.py
```
**Quando usar**: Para inspeção rápida dos dados no banco, útil durante desenvolvimento ou debug.

#### 6. Gerar Relatório PDF
```bash
# Gerar relatório automatizado
python Consumption/Reports/reports.py
```
**Quando usar**: Para criar relatórios em PDF com análises principais. O arquivo é salvo como `relatorio_enem.pdf`.

#### 7. Verificar Estrutura do Banco
```bash
# Executar script de verificação
python check_db.py
```
**Quando usar**: Para validar se o banco de dados foi criado corretamente e verificar integridade dos dados.

### Ordem Recomendada de Execução Local

1. **Primeira vez**: `python automate_etl.py` (processa dados automaticamente)
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
