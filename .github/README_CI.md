# Configuração de Integração Contínua (CI) - SISCAV API

## Visão Geral

Este repositório utiliza **GitHub Actions** para Integração Contínua (CI), conforme especificado no requisito **FND-08** da documentação do projeto.

## Objetivo

O pipeline de CI garante que:
- Todo código novo atende aos padrões de qualidade
- Nenhum código quebrado seja mesclado na branch `develop`
- Os testes unitários sejam executados automaticamente
- O código esteja formatado corretamente

## Como Funciona

### Trigger (Acionamento)

O pipeline é **automaticamente acionado** quando:
- Um **Pull Request** é aberto para a branch `develop`
- Um **Pull Request** existente para `develop` recebe novos commits

### Etapas do Pipeline

O workflow `.github/workflows/ci.yml` executa as seguintes etapas:

1. **Checkout do Código** — clona o repositório

2. **Setup Python 3.13** — configura CPython com cache de dependências `pip`

3. **Instalação de Dependências** — `pip install -r requirements-dev.txt`

4. **Linting com Ruff** — `ruff check .` (falha se houver erros)

5. **Verificação de Formatação** — `ruff format --check .`

6. **Testes com Pytest** — `pytest -v --cov=apps ...` com `DATABASE_URL=sqlite:///:memory:`

7. **SonarQube / SonarCloud** (opcional) — se `SONAR_TOKEN` estiver configurado

O CI **não** usa `uv`; apenas **pip** + ficheiros `requirements*.txt` exportados a partir de `pyproject.toml` (ADR 004).

## Bloqueio de Merge

O pipeline **bloqueia** a mesclagem se:
- Houver erros de linting (Ruff)
- O código não estiver formatado corretamente
- Qualquer teste unitário falhar

## Testando Localmente

Antes de abrir um PR, simule o CI com **pip** (recomendado, igual ao Actions):

```bash
pip install -r requirements-dev.txt
ruff check .
ruff format --check .
pytest -v --tb=short --cov=apps --cov-report=term-missing --cov-report=xml:coverage.xml
```

**Com uv** (equivalente, se preferir):

```bash
uv sync --locked --extra dev
uv run ruff check .
uv run ruff format --check .
uv run pytest -v --tb=short --cov=apps --cov-report=term-missing --cov-report=xml:coverage.xml
```

Guia detalhado: [`docs/setup/commands.md`](../docs/setup/commands.md) e [`docs/setup/installation.md`](../docs/setup/installation.md).

## Configuração

- **Workflow**: `.github/workflows/ci.yml`
- **Ruff**: `ruff.toml`
- **Pytest**: `pyproject.toml` (`[tool.pytest.ini_options]`)
- **Dependências**: `pyproject.toml` (SSOT) → `requirements-dev.txt` (CI)
