# Quick Commands — CI/CD

Quick reference for the most common day-to-day commands.

**CI** uses **pip** + `requirements-dev.txt` (Python 3.13). Locally you may use **pip** or **uv** — equivalent commands below.

---

## Local Verification (Before Opening a PR)

**pip** (with venv active and deps from `pip install -r requirements-dev.txt`):

```bash
ruff check . && ruff format --check . && pytest -v
```

**uv**:

```bash
uv run ruff check . && uv run ruff format --check . && uv run pytest -v
```

**PowerShell** (pip):

```powershell
ruff check . ; if ($?) { ruff format --check . } ; if ($?) { pytest -v }
```

---

## Install Dependencies

| Goal | pip | uv |
|------|-----|-----|
| Development | `pip install -r requirements-dev.txt` | `uv sync --locked --extra dev` |
| Production runtime | `pip install -r requirements.txt` | `uv sync --locked` |
| Optional ML/OCR | `pip install -r requirements-ml.txt` | `uv sync --locked --extra ml` |

---

## Linting

```bash
# Check for issues
ruff check .

# Auto-fix
ruff check --fix .

# Show error details
ruff check . --show-source
```

---

## Formatting

```bash
# Check formatting (does not modify files)
ruff format --check .

# Format automatically
ruff format .
```

---

## Tests

```bash
# Run all tests
pytest

# Verbose output
pytest -v

# With coverage
pytest --cov=apps --cov-report=term-missing

# Single file
pytest tests/test_main.py

# Single test
pytest tests/test_main.py::test_read_root

# Stop on first failure
pytest -x

# Show print statements
pytest -s
```

---

## Dependencies

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Upgrade pip
python -m pip install --upgrade pip

# List installed packages
pip list

# Check outdated packages
pip list --outdated
```

---

## Git Workflow

```bash
# Update develop
git checkout develop
git pull origin develop

# Create new feature branch
git checkout -b feature/feature-name

# Status
git status

# Stage files
git add .

# Commit
git commit -m "feat: description"

# Push
git push origin feature/feature-name

# Return to develop
git checkout develop
```

---

## Sync with Develop

```bash
# Update your branch with develop
git checkout develop
git pull origin develop
git checkout feature/your-feature
git merge develop

# OR using rebase (cleaner history)
git checkout feature/your-feature
git rebase develop
```

---

## Debugging

```bash
# Full test output
pytest -vv

# Full traceback
pytest --tb=long

# Show local variables
pytest --showlocals

# Interactive debug mode
pytest --pdb
```

---

## Coverage

```bash
# Generate coverage report
pytest --cov=apps

# Show missing lines
pytest --cov=apps --cov-report=term-missing

# Generate HTML report
pytest --cov=apps --cov-report=html

# Open HTML report (Windows)
start htmlcov/index.html
```

---

## Virtual Environment

```bash
# Create venv
python -m venv venv

# Activate (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate (Windows CMD)
.\venv\Scripts\activate.bat

# Activate (Linux/Mac)
source venv/bin/activate

# Deactivate
deactivate

# Remove venv
Remove-Item -Recurse -Force venv  # PowerShell
rm -rf venv                        # Linux/Mac
```

---

## Productivity

```powershell
# Useful aliases (add to your PowerShell profile)
# $PROFILE to see the profile file path

function test { pytest -v }
function lint { ruff check . }
function format { ruff format . }
function ci { ruff check . ; if ($?) { ruff format --check . } ; if ($?) { pytest -v } }

# Then use:
# test
# lint
# format
# ci
```

---

## Conventional Commits

```bash
# Structure
git commit -m "type: short description"

# Common types:
git commit -m "feat: add new feature"
git commit -m "fix: fix bug"
git commit -m "docs: update documentation"
git commit -m "test: add tests"
git commit -m "refactor: refactor code"
git commit -m "style: adjust formatting"
git commit -m "chore: update dependencies"
git commit -m "ci: adjust pipeline"
```

---

## Undo Operations

```bash
# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1

# Undo changes in a specific file
git checkout -- file.py

# Remove untracked files
git clean -fd

# Abort merge
git merge --abort

# Abort rebase
git rebase --abort
```

---

## Information

```bash
# Python version
python --version

# pip version
pip --version

# Git configuration
git config --list

# Branches
git branch -a

# Last commit
git log -1

# Short history
git log --oneline -10
```

---

## Useful One-Liners

```bash
# Install + test
pip install -r requirements-dev.txt && pytest -v --tb=short --cov=apps --cov-report=term-missing

# Format + lint + test
ruff format . && ruff check . && pytest -v

# Commit and push
git add . && git commit -m "feat: message" && git push

# Update develop and create feature
git checkout develop && git pull && git checkout -b feature/new

# Reset dev environment
Remove-Item -Recurse -Force venv ; python -m venv venv ; .\venv\Scripts\Activate.ps1 ; pip install -r requirements-dev.txt
```
