# SonarQube / SonarCloud — configuração (SISCAV API)

## Objetivo

Publicar **análise estática** e **cobertura de testes** (Python/FastAPI em `apps/`) no **SonarCloud** ou num servidor **SonarQube** self-hosted, a partir do job de CI em `.github/workflows/ci.yml`.

## Pré-requisitos

- Conta no [SonarCloud](https://sonarcloud.io) *ou* instância SonarQube acessível ao CI.
- Permissão para criar **Secrets** (e opcionalmente **Variables**) no repositório GitHub.

## SonarCloud

1. Crie um projeto em SonarCloud (importar o repositório GitHub ou criar manualmente).
2. Copie a **Organization key** e o **Project key** mostrados no assistente.
3. Edite `sonar-project.properties` na **raiz do repositório**:
   - `sonar.organization=<Organization key>`
   - `sonar.projectKey=<Project key>`
4. Gere um **token** de análise (User → My Account → Security, ou token de projeto) e guarde-o como secret do GitHub (abaixo).

## SonarQube Server (self-hosted)

1. Crie o projeto no servidor e alinhe `sonar.projectKey` em `sonar-project.properties` com o definido no servidor.
2. No GitHub: **Settings → Secrets and variables → Actions → Variables**, crie `SONAR_HOST_URL` com a URL base (ex.: `https://sonar.example.com`). **Não** use `https://sonarcloud.io`.
3. Comente ou remova `sonar.organization` em `sonar-project.properties` se o servidor não usar organizações SonarCloud-style.

## GitHub — Secret `SONAR_TOKEN`

1. **Settings → Secrets and variables → Actions → New repository secret**
2. Nome: `SONAR_TOKEN`
3. Valor: token de análise SonarCloud ou token de projeto/usuário no SonarQube Server.

Enquanto `SONAR_TOKEN` **não** existir, o passo **SonarQube Scan** no CI é **ignorado** e o restante do pipeline (ruff + pytest) continua a correr normalmente.

## Variável `SONAR_HOST_URL` (opcional)

- **SonarCloud:** pode omitir; o workflow usa `https://sonarcloud.io` por omissão.
- **SonarQube Server:** defina a variável de repositório `SONAR_HOST_URL` com a URL do servidor.

## Cobertura (`coverage.xml`)

O CI executa pytest com `--cov-report=xml:coverage.xml` na **raiz do checkout**. O ficheiro está em `.gitignore`; o scanner lê-o no runner **antes** do passo Sonar. Não é necessário commitar `coverage.xml`.

## Quality Gate

**Política inicial:** o CI **não** espera pelo quality gate (`sonar.qualitygate.wait=true` não está ativo). O objetivo é completar o onboarding sem bloquear merges por dívida histórica.

Para **falhar o job** quando o quality gate falhar:

- Adicione `sonar.qualitygate.wait=true` em `sonar-project.properties`, **ou**
- Passe o parâmetro equivalente nos argumentos do passo `SonarSource/sonarqube-scan-action` (ver [documentação Sonar](https://docs.sonarsource.com/)).

## Pull requests a partir de forks

Os **secrets** do repositório **não** são expostos a workflows de PR vindos de **forks**. O passo Sonar continua a ser ignorado se o token não estiver disponível — comportamento esperado; análise completa costuma correr em branches do repositório principal.

## Referências

- `sonar-project.properties` (raiz)
- `.github/workflows/ci.yml`
