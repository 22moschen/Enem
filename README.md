# ENEMAnalytics

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-blue.svg)](https://github.com/features/actions)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red.svg)](https://streamlit.io/)

**ENEMAnalytics** é uma plataforma **profissional e escalável** de análise de dados educacionais que transforma microdados do ENEM em insights acionáveis para gestores, educadores e pesquisadores em Altamira-PA, através de um dashboard interativo, pipeline ETL robusto e API estruturada.

## 📋 Tabela de Conteúdo

- [Visão Geral](#visão-geral)
- [Quick Start](#quick-start)
- [Recursos Principais](#recursos-principais)
- [Documentação](#documentação)
- [Desenvolvimento](#desenvolvimento)
- [Deployment](#deployment)
- [Arquitetura](#arquitetura)
- [Contribuição](#contribuição)
- [Suporte](#suporte)

## 🎯 Visão Geral

### O Problema

Altamira-PA enfrenta desafios educacionais críticos:

- **Desigualdade de Desempenho**: Variação de até 50 pontos entre zonas urbanas e rurais
- **Dados Inacessíveis**: Microdados do ENEM publicamente disponíveis, mas sem ferramentas de análise
- **Falta de Insights**: Gestores educacionais sem visibilidade sobre tendências e correlações
- **Variabilidade**: Taxas altas de ausência em disciplinas específicas

### A Solução

ENEMAnalytics fornece:

✅ **Dashboard Interativo**: Análises em tempo real com filtros dinâmicos  
✅ **Pipeline ETL Automatizado**: Processamento robusto de microdados  
✅ **Relatórios Executivos**: Geração automática de PDF com insights principais  
✅ **Código Profissional**: Estrutura escalável, testável e mantível  
✅ **Monitoramento**: CI/CD, logging, health checks em produção  

## 🚀 Quick Start

### Opção 1: Docker (Recomendado)

```bash
# Clone repositório
git clone https://github.com/22moschen/Enem.git
cd Enem

# Instale Git LFS
git lfs install && git lfs pull

# Execute com Docker Compose
docker-compose up --build

# Acesse http://localhost:8501
```

### Opção 2: Local com Python

```bash
# Clone
git clone https://github.com/22moschen/Enem.git
cd Enem

# Ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instale
pip install -r requirements.txt

# Execute
streamlit run streamlit_app.py
```

## ✨ Recursos Principais

### 📊 Dashboard Analítico

- Seleção de ano para análise histórica
- Filtros dinâmicos por localização e tipo de escola
- Gráficos interativos com Plotly
- Exportação de dados em CSV/PDF
- KPIs em tempo real

### 🔄 Pipeline ETL

- Detecção automática de novos dados
- Processamento incremental (sem reprocessamento)
- Validações rigorosas de qualidade
- Tratamento de duplicatas
- Logging detalhado

### 📈 Análises Disponíveis

- Desempenho por região (urbano vs rural)
- Correlações entre disciplinas
- Estatísticas descritivas
- Análise de ausências
- Comparação por dependência administrativa

## 📚 Documentação

### Para Usuários

- [Guia de Uso](/docs/USER_GUIDE.md) - Como usar o dashboard
- [FAQ](/docs/FAQ.md) - Perguntas frequentes
- [Exemplos](/docs/EXAMPLES.md) - Cases de uso

### Para Desenvolvedores

- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Setup de desenvolvimento, workflow, debugging
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Implantação em produção, monitoramento, backups
- **[API.md](/docs/API.md)** - Documentação de endpoints (em desenvolvimento)

### Estrutura do Projeto

```
enem_analytics/
├── config/                  # Configurações centralizadas
│   └── settings.py         # Settings (DB, logging, paths)
├── src/enem_analytics/
│   ├── core/               # Funcionalidades principais
│   │   ├── logger.py       # Sistema de logging
│   │   └── models.py       # Modelos de dados (Pydantic)
│   ├── etl/                # Pipeline ETL
│   │   ├── extract.py      # Extração
│   │   ├── transform.py    # Transformação
│   │   └── load.py         # Carregamento
│   └── dashboards/         # Interfaces web
│       ├── main.py         # Dashboard principal
│       ├── reports.py      # Geração de relatórios
│       └── components.py   # Componentes reutilizáveis
├── tests/
│   ├── unit/               # Testes unitários
│   └── integration/        # Testes de integração
├── DataSources/            # Dados brutos
├── data/                   # Dados processados
├── logs/                   # Logs da aplicação
├── Makefile                # Tarefas comuns
├── pyproject.toml          # Metadados do projeto
├── requirements.txt        # Dependências Python
├── Dockerfile              # Container de produção
└── docker-compose.yml      # Orquestração de serviços
```

## 🛠️ Desenvolvimento

### Pré-requisitos

- Python 3.11+
- Git & Git LFS
- Docker (opcional)

### Setup

```bash
# Clonar e preparar
git clone https://github.com/22moschen/Enem.git
cd Enem
git lfs pull

# Instalar dependências de dev
make install-dev

# Configurar pre-commit hooks
pre-commit install
```

### Comandos Úteis

```bash
make help              # Lista todos os comandos
make test              # Rodar testes
make test-cov          # Testes com coverage
make lint              # Verificar código
make format            # Formatar código
make type-check        # Verificação de tipos
make run               # Executar aplicação
make etl               # Rodar ETL
make clean             # Limpar temporários
```

### Workflow de Desenvolvimento

1. **Create a feature branch**
   ```bash
   git checkout -b feature/sua-feature
   ```

2. **Desenvolva e teste**
   ```bash
   make test
   make lint
   ```

3. **Commit seguindo convenção**
   ```bash
   git commit -m "feat(modulo): descrição da feature"
   ```

4. **Push e abra PR**
   ```bash
   git push origin feature/sua-feature
   ```

Para detalhes completos, veja [DEVELOPMENT.md](DEVELOPMENT.md)

## 🚀 Deployment

### Produção

```bash
# Prepare o server
docker-compose build
docker-compose up -d

# Monitore
docker-compose logs -f app
```

### CI/CD com GitHub Actions

- Tests automáticos a cada push
- Build e push de imagem Docker
- Deployment automático para staging/produção

Para mais detalhes, veja [DEPLOYMENT.md](DEPLOYMENT.md)

## 🏗️ Arquitetura

### Camadas da Aplicação

```
┌─────────────────────────────────────┐
│      Streamlit Dashboard            │  ← Interface Web
├─────────────────────────────────────┤
│   Core Logic (Analytics, Reports)   │  ← Lógica de Negócio
├─────────────────────────────────────┤
│     ETL Pipeline (Extract/Transf)   │  ← Processamento de Dados
├─────────────────────────────────────┤
│    SQLite Database (DW Storage)     │  ← Armazenamento
├─────────────────────────────────────┤
│     Data Sources (CSV/Excel)        │  ← Dados Brutos
└─────────────────────────────────────┘
```

### Fluxo de Dados

```
CSV bruto → Extract → Transform → Load → SQLite
                                          ↓
                                    Streamlit Dashboard
                                          ↓
                                    PDF Reports
```

## 🔧 Tecnologias

| Camada | Tecnologias |
|--------|-------------|
| **Web** | Streamlit, Plotly, Altair |
| **Backend** | Python 3.11+, Pandas, NumPy, Scikit-learn |
| **Database** | SQLite, SQLAlchemy |
| **DevOps** | Docker, Docker Compose, GitHub Actions |
| **Code Quality** | Black, Ruff, MyPy, Pytest |

## 📊 Métricas e Qualidade

- **Code Coverage**: >70% de cobertura de testes
- **Type Hints**: 100% de código com type hints
- **Linting**: Zero warnings com Ruff
- **Format**: Padronizado com Black
- **CI/CD**: Testes automáticos a cada commit

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

Veja [CONTRIBUTING.md](CONTRIBUTING.md) para mais detalhes.

## 📝 Licença

Este projeto está sob a licença MIT. Veja [LICENSE](LICENSE) para detalhes.

## 📧 Suporte

### Reportar Issues

Encontrou um bug? [Abra uma issue](https://github.com/22moschen/Enem/issues/new?labels=bug)

### Solicitar Feature

Tem uma ideia? [Crie uma feature request](https://github.com/22moschen/Enem/issues/new?labels=enhancement)

### Contato

- **Email**: suporte@enemanalytics.com
- **Docs**: [Documentação Completa](docs/)
- **Issues**: [GitHub Issues](https://github.com/22moschen/Enem/issues)

## 🗺️ Roadmap

- [ ] **v2.1**: API REST completa
- [ ] **v2.2**: Autenticação e autorização
- [ ] **v2.3**: Análises preditivas (ML)
- [ ] **v2.4**: Integração com Google Sheets
- [ ] **v3.0**: Suporte para múltiplos municípios

## 🙏 Agradecimentos

- INEP pelo acesso aos microdados do ENEM
- Faculdade Serra Dourada de Altamira pelo suporte
- Community de Python e Streamlit

---

**Desenvolvido com ❤️ em Altamira-PA**

Última atualização: Dezembro 2025 | Versão: 2.0.0
