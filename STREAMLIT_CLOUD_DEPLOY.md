# Deployment Guide - ENEMAnalytics

## Streamlit Cloud Deployment

### Pré-requisitos

1. **Repositório público no GitHub** - Streamlit Cloud precisa de acesso público
2. **`requirements-prod.txt`** - Dependências limpas (sem `-e git+...`)
3. **`.streamlit/config.toml`** - Configuração do Streamlit
4. **`.streamlit/secrets.toml`** (opcional) - Variáveis sensíveis

### Passo 1: Garantir que o Repo é Público

```bash
# No GitHub, vá para: Settings → Visibility → Public
```

### Passo 2: Usar `requirements-prod.txt` no Deploy

Quando conectar no Streamlit Cloud:
- Use este arquivo: **`requirements-prod.txt`**
- NÃO use `requirements.txt` (contém editable install que Cloud não suporta)

### Passo 3: Fazer Push das Alterações

```bash
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

### Passo 4: Deploy no Streamlit Cloud

1. Acesse https://share.streamlit.io
2. Clique em "New app"
3. Conecte seu repositório GitHub
4. **Importante:**
   - Repository: `22moschen/Enem`
   - Branch: `main`
   - Main file path: `streamlit_app.py`
   - **Advanced settings:**
     - Python version: 3.11
     - Custom install commands: deixar em branco
     - Requirements file: `requirements-prod.txt`

### Troubleshooting

**Erro: "Failed to download sources"**
- [ ] Repositório é público? (Settings → Visibility)
- [ ] Usuário GitHub conectado tem acesso?
- [ ] `requirements.txt` tem `-e git+...`? (remover de `requirements-prod.txt`)
- [ ] Arquivo `streamlit_app.py` existe na raiz?

**App lento ou erro de memória**
- Aumentar cache:
  ```python
  @st.cache_data(ttl=3600)
  def load_data():
      ...
  ```

**Erro de import faltando**
- Adicionar pacote em `requirements-prod.txt`:
  ```bash
  pip install novo-pacote
  pip freeze | grep novo-pacote >> requirements-prod.txt
  ```

---

**Status:** ✅ Pronto para deploy
**Última atualização:** Dezembro 6, 2025
