# 🎯 Comandos Rápidos - CI/CD

Referência rápida dos comandos mais usados no dia a dia.

---

## 🔍 Verificação Local (Antes de Abrir PR)

```bash
# Comando completo que simula o CI
ruff check . && ruff format --check . && pytest -v

# OU em PowerShell (com melhor visualização)
ruff check . ; if ($?) { ruff format --check . } ; if ($?) { pytest -v }
```

---

## 🧹 Linting

```bash
# Verificar problemas
ruff check .

# Corrigir automaticamente
ruff check --fix .

# Ver detalhes dos erros
ruff check . --show-source
```

---

## 🎨 Formatação

```bash
# Verificar formatação (não modifica arquivos)
ruff format --check .

# Formatar automaticamente
ruff format .
```

---

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Verbose (mostra mais detalhes)
pytest -v

# Com cobertura
pytest --cov=apps --cov-report=term-missing

# Apenas um arquivo específico
pytest tests/test_main.py

# Apenas um teste específico
pytest tests/test_main.py::test_read_root

# Parar no primeiro erro
pytest -x

# Mostrar print statements
pytest -s
```

---

## 📦 Dependências

```bash
# Instalar dependências de dev
pip install -e ".[dev]"

# Atualizar pip
python -m pip install --upgrade pip

# Listar dependências instaladas
pip list

# Verificar pacotes desatualizados
pip list --outdated
```

---

## 🌿 Git Workflow

```bash
# Atualizar develop
git checkout develop
git pull origin develop

# Criar nova feature
git checkout -b feature/nome-da-feature

# Ver status
git status

# Adicionar arquivos
git add .

# Commit
git commit -m "feat: descrição"

# Push
git push origin feature/nome-da-feature

# Voltar para develop
git checkout develop
```

---

## 🔄 Sincronizar com Develop

```bash
# Atualizar sua branch com develop
git checkout develop
git pull origin develop
git checkout feature/sua-feature
git merge develop

# OU usando rebase (histórico mais limpo)
git checkout feature/sua-feature
git rebase develop
```

---

## 🐛 Debugging

```bash
# Ver output completo dos testes
pytest -vv

# Ver traceback completo
pytest --tb=long

# Ver variáveis locais
pytest --showlocals

# Modo debug interativo
pytest --pdb
```

---

## 📊 Coverage

```bash
# Gerar relatório de cobertura
pytest --cov=apps

# Com arquivos faltando
pytest --cov=apps --cov-report=term-missing

# Gerar HTML
pytest --cov=apps --cov-report=html

# Abrir relatório HTML (Windows)
start htmlcov/index.html
```

---

## 🔧 Ambiente Virtual

```bash
# Criar venv
python -m venv venv

# Ativar (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Ativar (Windows CMD)
.\venv\Scripts\activate.bat

# Ativar (Linux/Mac)
source venv/bin/activate

# Desativar
deactivate

# Remover venv
Remove-Item -Recurse -Force venv  # PowerShell
rm -rf venv  # Linux/Mac
```

---

## 🚀 Produtividade

```bash
# Alias úteis (adicione ao seu perfil PowerShell)
# $PROFILE para ver o caminho do arquivo

function test { pytest -v }
function lint { ruff check . }
function format { ruff format . }
function ci { ruff check . ; if ($?) { ruff format --check . } ; if ($?) { pytest -v } }

# Depois use simplesmente:
# test
# lint
# format
# ci
```

---

## 📝 Commits Convencionais

```bash
# Estrutura
git commit -m "tipo: descrição curta"

# Tipos comuns:
git commit -m "feat: adicionar nova funcionalidade"
git commit -m "fix: corrigir bug"
git commit -m "docs: atualizar documentação"
git commit -m "test: adicionar testes"
git commit -m "refactor: refatorar código"
git commit -m "style: ajustar formatação"
git commit -m "chore: atualizar dependências"
git commit -m "ci: ajustar pipeline"
```

---

## 🆘 Desfazer Coisas

```bash
# Desfazer último commit (mantém alterações)
git reset --soft HEAD~1

# Desfazer último commit (descarta alterações)
git reset --hard HEAD~1

# Desfazer alterações em arquivo específico
git checkout -- arquivo.py

# Limpar arquivos não rastreados
git clean -fd

# Desfazer merge
git merge --abort

# Desfazer rebase
git rebase --abort
```

---

## 🔍 Informações

```bash
# Ver versão do Python
python --version

# Ver versão do pip
pip --version

# Ver configuração do git
git config --list

# Ver branches
git branch -a

# Ver último commit
git log -1

# Ver histórico resumido
git log --oneline -10
```

---

## 🎯 One-Liners Úteis

```bash
# Instalar + testar
pip install -e ".[dev]" && pytest -v

# Formatar + lint + testar
ruff format . && ruff check . && pytest -v

# Commit tudo de uma vez
git add . && git commit -m "feat: mensagem" && git push

# Atualizar develop e criar feature
git checkout develop && git pull && git checkout -b feature/nova

# Resetar ambiente de dev
Remove-Item -Recurse -Force venv ; python -m venv venv ; .\venv\Scripts\Activate.ps1 ; pip install -e ".[dev]"
```
