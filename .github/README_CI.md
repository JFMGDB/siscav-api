# Configuração de Integração Contínua (CI) - SISCAV API

## 📋 Visão Geral

Este repositório utiliza **GitHub Actions** para Integração Contínua (CI), conforme especificado no requisito **FND-08** da documentação do projeto.

## 🎯 Objetivo

O pipeline de CI garante que:
- ✅ Todo código novo atende aos padrões de qualidade
- ✅ Nenhum código quebrado seja mesclado na branch `develop`
- ✅ Os testes unitários sejam executados automaticamente
- ✅ O código esteja formatado corretamente

## 🚀 Como Funciona

### Trigger (Acionamento)

O pipeline é **automaticamente acionado** quando:
- Um **Pull Request** é aberto para a branch `develop`
- Um **Pull Request** existente para `develop` recebe novos commits

### Etapas do Pipeline

O workflow `.github/workflows/ci.yml` executa as seguintes etapas:

1. **Checkout do Código** 
   - Clona o repositório

2. **Setup Python 3.13**
   - Configura o ambiente Python com cache de dependências `pip`

3. **Instalação de Dependências**
   - Instala dependências de desenvolvimento
   - Comando: `pip install -r requirements-dev.txt`

4. **Linting com Ruff** 
   - Verifica qualidade e estilo do código
   - Comando: `ruff check .`
   - **Falha se houver erros de linting**

5. **Verificação de Formatação** 📝
   - Verifica se o código está formatado corretamente
   - Comando: `ruff format --check .`
   - **Falha se o código não estiver formatado**

6. **Testes Unitários com Pytest** 🧪
   - Executa todos os testes unitários com cobertura
   - Comando: `pytest -v --tb=short --cov=apps --cov-report=term-missing --cov-report=xml:coverage.xml`
   - **Falha se qualquer teste falhar**

7. **SonarQube / SonarCloud** (opcional)
   - Se o secret `SONAR_TOKEN` estiver configurado, corre análise estática com `SonarSource/sonarqube-scan-action@v5` e envia cobertura a partir de `coverage.xml`.
   - Guia de configuração: [SONAR_SETUP.md](SONAR_SETUP.md)

8. **Relatório de Cobertura** 📊 (Opcional)
   - Gera relatório de cobertura de código
   - Upload para Codecov (se configurado)

## Bloqueio de Merge

**IMPORTANTE:** O pipeline está configurado para **BLOQUEAR** a mesclagem se:
- ❌ Houver erros de linting (Ruff)
- ❌ O código não estiver formatado corretamente
- ❌ Qualquer teste unitário falhar

Isso é feito através do uso de `continue-on-error: false` em cada etapa crítica.

## 🛠️ Testando Localmente

**Antes de abrir um Pull Request**, execute localmente:

```bash
# 1. Instalar dependências de dev
pip install -r requirements-dev.txt

# 2. Executar linting
ruff check .

# 3. Verificar formatação
ruff format --check .

# 4. Executar testes
pytest -v --tb=short --cov=apps --cov-report=term-missing --cov-report=xml:coverage.xml

# 5. OU executar tudo de uma vez (simula o CI)
ruff check . && ruff format --check . && pytest -v --tb=short --cov=apps --cov-report=term-missing --cov-report=xml:coverage.xml
```

Se todos os comandos passarem, seu código está pronto para PR!

**Guia detalhado**: Veja [`docs/setup/commands.md`](../docs/setup/commands.md)

## 📊 Status do Pipeline

Você pode visualizar o status do pipeline:
- Na aba **Actions** do GitHub
- No próprio Pull Request (check verde ✅ ou vermelho ❌)
- Nos badges no README (quando configurado)

## 🔧 Configuração

### Arquivo Principal
- **Workflow**: `.github/workflows/ci.yml`
- **Configuração Ruff**: `ruff.toml`
- **Configuração Pytest**: `pyproject.toml` (seção `[tool.pytest.ini_options]`)

### Dependências de Dev

Definidas em `pyproject.toml`:
```toml
[project.optional-dependencies]
dev = [
    "pytest",       # Framework de testes
    "pytest-cov",   # Cobertura de código
    "ruff",         # Linter/Formatter
    "httpx"         # Cliente HTTP para testes
]
```

## 📈 Melhorias Futuras

Planejado para implementação futura:
- [ ] Integração com Codecov para visualização de cobertura
- [ ] Testes de integração com banco de dados
- [ ] Deploy automático após merge em `develop`
- [ ] Análise de segurança (Bandit, Safety)
- [ ] Verificação de dependências vulneráveis

## 🤝 Contribuindo

1. Crie uma branch a partir de `develop`:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/sua-feature
   ```

2. Faça suas alterações e commits:
   ```bash
   git add .
   git commit -m "feat: descrição da feature"
   ```

3. **Teste localmente** (ver seção acima)

4. Push e abra um Pull Request:
   ```bash
   git push origin feature/sua-feature
   ```

5. Aguarde o pipeline passar ✅

6. Solicite code review

7. Após aprovação, faça merge!

## 📚 Referências

- [Documentação GitHub Actions](https://docs.github.com/en/actions)
- [Documentação Ruff](https://docs.astral.sh/ruff/)
- [Documentação Pytest](https://docs.pytest.org/)
- Requisito **FND-08** - `docs/Arquitetura - Critérios de Aceite e Devops.md`

---

**Projeto:** SISCAV - Sistema de Controle de Acesso Veicular  
**Instituição:** UNICAP  
**Repositório:** [siscav-api](https://github.com/JFMGDB/siscav-api)
