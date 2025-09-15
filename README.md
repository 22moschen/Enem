# ENEMAnalytics
Repositório para o desenvolvimento do projeto de experiência aplicada em dados do 4° período da faculdade Serra Dourada de Altamira

## Camadas do Projeto:

O projeto será dividido em 5 grandes camadas:
- Data Sources
- ETL
- DW Storage
- Consumption
- Governacy and security

## Explicando as camadas do projeto:

### Data Sources

É a camada responsável pela implementação de API e microsserviços que farão consumo das fontes de dados. Normalmente nessa camada são inseridos dados brutos e despadronizados como fonte de dados para serem trabalhados.

### ETL

Essa camada é dividida em três partes, Extract, Transform, Load.

Na sub-camada Extract será feita a leitura dos dados, compreendendo sua estrutura no arquivo estruturado.

Na sub-camada Transform será feita a modelagem dos dados coletados, de modo que possibilite a análise de dados.

Na sub-camada Load será feito o envio dos dados para a próxima camada do projeto, a camada de DW Storage.

### DW Storage

Nesta camada será utilizada para armazenar os dados já padronizados em esquemas seccionados para as determinadas áreas da camada de Consumo, para visualização dos dados, geração de relatórios, e business intelligence.

### Consumption

A camada de consumo é voltada para o desenvolvimento de três vertentes: Visualização de dados (Preview), geração de relatórios (Reports), e business intelligence (BI). 

Será preciso desenvolver gráficos, dashboards, tabelas, documentos, de acordo com o escopo do projeto e capacidade de visualização.

### Governacy and security

É a camada responsável por fazer o gerenciamento de níveis de acesso da análise de dados. Responsável também pela documentação e catalogação dos dados presentes no projeto.


