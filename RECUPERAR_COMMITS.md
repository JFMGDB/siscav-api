# Guia de Recuperação de Commits Perdidos

## Situação

Foram encontrados commits órfãos (perdidos) no repositório. Estes commits contêm trabalho importante que foi perdido após uma exclusão/reset.

## Commits Encontrados

### 1. Commit `3733db2` - "feat: adiciona schemas, models, utils e componentes IoT"
**Conteúdo:** Muito extenso! Inclui:
- Schemas, models, utils
- Componentes IoT completos
- Documentação extensa
- Scripts de instalação
- Código Arduino
- **Total: 7169 linhas adicionadas!**

### 2. Commit `3cd39a9` - "feat: Ajustes de testes unitários e de integração com cobertura de 88%"
**Conteúdo:**
- Testes unitários e de integração
- Documentação de instalação
- Scripts de migração
- **Total: 2754 linhas adicionadas**

### 3. Commit `a70529b` - "refactor: implementa camada de repositories seguindo padrão MVC e SOLID"
**Conteúdo:**
- Repositories completos
- **Total: 545 linhas adicionadas**

## Opções de Recuperação

### Opção 1: Recuperar Todos os Commits em uma Branch (Recomendado)

```bash
# Criar branch de recuperação a partir do commit mais antigo
git checkout -b recuperacao-completa 3733db2

# Ver o que foi recuperado
git log --oneline -20

# Se estiver satisfeito, fazer merge na main
git checkout main
git merge recuperacao-completa
```

### Opção 2: Recuperar Commits Individuais

#### Recuperar apenas o commit de IoT (3733db2):
```bash
git checkout -b recuperacao-iot 3733db2
# Revisar e depois fazer merge
```

#### Recuperar apenas o commit de testes (3cd39a9):
```bash
git checkout -b recuperacao-testes 3cd39a9
# Revisar e depois fazer merge
```

### Opção 3: Cherry-pick (Aplicar commits específicos)

```bash
# Aplicar apenas o commit de IoT
git cherry-pick 3733db2

# Aplicar apenas o commit de testes
git cherry-pick 3cd39a9

# Aplicar o commit de repositories (se necessário)
git cherry-pick a70529b
```

## Verificar Conteúdo Antes de Recuperar

### Ver o que tem em cada commit:

```bash
# Ver arquivos modificados
git show 3733db2 --stat

# Ver diferenças
git show 3733db2

# Ver mensagem do commit
git show 3733db2 --oneline
```

## Passo a Passo Recomendado

1. **Verificar o conteúdo:**
   ```bash
   git show 3733db2 --stat
   git show 3cd39a9 --stat
   ```

2. **Criar branch de recuperação:**
   ```bash
   git checkout -b recuperacao-perdidos 3733db2
   ```

3. **Verificar se está tudo correto:**
   ```bash
   git log --oneline -10
   ls -la  # Verificar arquivos
   ```

4. **Se estiver tudo OK, fazer merge:**
   ```bash
   git checkout main
   git merge recuperacao-perdidos
   ```

5. **Resolver conflitos (se houver):**
   ```bash
   # Git mostrará os conflitos
   # Resolva manualmente e depois:
   git add .
   git commit
   ```

## Lista Completa de Commits Órfãos Encontrados

Execute para ver todos:
```bash
git fsck --lost-found
```

Commits encontrados:
- `3733db2` - feat: adiciona schemas, models, utils e componentes IoT
- `3cd39a9` - feat: Ajustes de testes unitários e de integração
- `a70529b` - refactor: implementa camada de repositories
- `d5632d7` - refactor: refatora endpoints
- `6215088` - refactor: refatora endpoints
- `51074eb` - fix: Corrige erros do Ruff
- E outros...

## Aviso Importante

⚠️ **Antes de fazer merge, certifique-se de:**
1. Fazer backup do estado atual: `git branch backup-antes-recuperacao`
2. Revisar os arquivos recuperados
3. Verificar se não há conflitos com o trabalho atual
4. Testar o código recuperado

## Comandos Úteis

```bash
# Ver todos os commits órfãos
git fsck --lost-found | grep commit

# Ver histórico completo (incluindo perdidos)
git reflog --all

# Ver diferença entre branch atual e commit perdido
git diff main 3733db2

# Ver apenas os arquivos diferentes
git diff --name-only main 3733db2
```

