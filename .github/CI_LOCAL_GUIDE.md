# Guia: Como Testar o Pipeline de CI Localmente

Este guia explica como testar o pipeline de CI localmente antes de abrir um Pull Request.

## 1. Instalar Dependências de Desenvolvimento

```bash
# Ativar ambiente virtual (se ainda não estiver ativo)
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# ou
source venv/bin/activate      # Linux/Mac

# Instalar dependências de dev
pip install -e ".[dev]"
```

## 2. Executar Linting (Ruff)

```bash
# Verificar problemas de código
ruff check .

# Verificar formatação
ruff format --check .

# Auto-fix de problemas simples
ruff check --fix .

# Auto-formatar código
ruff format .
```

## 3. Executar Testes

```bash
# Executar todos os testes
pytest

# Executar com verbose
pytest -v

# Executar com cobertura
pytest --cov=apps --cov-report=term-missing

# Executar testes específicos
pytest tests/test_main.py

# Executar apenas testes unitários
pytest -m unit
```

## 4. Verificação Completa (Simula o CI)

```bash
# Execute todos os comandos em sequência
ruff check . && ruff format --check . && pytest -v
```

Se todos os comandos passarem sem erro, seu código está pronto para o Pull Request! ✅

## 5. Criar Pull Request

1. Certifique-se de estar na branch correta:
   ```bash
   git checkout -b feature/minha-feature
   ```

2. Commit suas alterações:
   ```bash
   git add .
   git commit -m "feat: descrição da funcionalidade"
   ```

3. Push para o repositório:
   ```bash
   git push origin feature/minha-feature
   ```

4. Abra um Pull Request no GitHub para a branch `develop`

5. O pipeline de CI será executado automaticamente

## Estrutura do Pipeline

O pipeline executa as seguintes etapas:

1. ✅ **Checkout** - Clona o código
2. ✅ **Setup Python** - Configura Python 3.12
3. ✅ **Instalar Deps** - Instala dependências
4. ✅ **Ruff Check** - Verifica qualidade do código
5. ✅ **Ruff Format** - Verifica formatação
6. ✅ **Pytest** - Executa testes unitários
7. 📊 **Coverage** - Gera relatório de cobertura (opcional)

## Solução de Problemas

### Erro: "ruff: command not found"
```bash
pip install ruff
```

### Erro: "pytest: command not found"
```bash
pip install pytest pytest-cov
```

### Erro: "ModuleNotFoundError"
```bash
# Reinstalar o projeto em modo editable
pip install -e ".[dev]"
```

### Erros de Linting
```bash
# Ver detalhes dos erros
ruff check . --show-source

# Corrigir automaticamente
ruff check --fix .
```
