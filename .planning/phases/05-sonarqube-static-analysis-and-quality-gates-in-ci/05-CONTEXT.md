# Phase 5: SonarQube — contexto

**Recolhido:** 2026-05-03  
**Estado:** Pronto para `/gsd-plan-phase 5`

## Fronteira da fase

Introduzir **SonarQube** no pipeline de qualidade do repositório **siscav-api** (Python 3.13 no CI, FastAPI em `apps/api/src/`, testes `pytest` com cobertura).

**Em âmbito típico:**

- **SonarCloud** (recomendado para OSS/GitHub) *ou* instância **SonarQube** self-hosted com token de projeto.
- `sonar-project.properties` na raiz (ou pasta `apps/api` se a análise for só ao pacote da API).
- Integração em **GitHub Actions** (job adicional ou extensão do `ci.yml`), com segredos `SONAR_TOKEN` / `SONAR_HOST_URL` conforme o modo.
- **Quality gate:** regras iniciais conservadoras (evitar bloquear o repo no dia 1); afinar após baseline.
- Cobertura: reutilizar relatório **pytest-cov** (XML Cobertura) se o Sonar o consumir.

**Fora de âmbito:** alterar regras de produto da API, migrar stack, ou hospedar servidor SonarQube na infraestrutura do cliente (apenas documentar opção).

## Requisitos provisórios (para formalizar como SONAR-xx no plano)

| ID | Descrição |
|----|-----------|
| SONAR-01 | Análise Sonar corre em cada PR/push aos branches já cobertos pelo CI (ou política acordada). |
| SONAR-02 | Resultado visível no SonarCloud/SonarQube com ligação ao commit. |
| SONAR-03 | Quality gate documentado; falha de gate reflete falha de CI (ou aviso, conforme decisão no plano). |
| SONAR-04 | Documentação mínima em `docs/` ou `.github/` sobre tokens e modo SonarCloud vs servidor. |

## Notas

- O `gsd-tools phase add` gerou número **1000** por interação com a pasta **999.1**; esta fase foi renumerada para **5** no roadmap para manter sequência legível após as fases 1–4 fechadas.
