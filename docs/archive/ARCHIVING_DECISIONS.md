# Decisões de Arquivamento

Este documento explica as decisões tomadas ao arquivar documentos obsoletos da documentação do projeto SISCAV.

## Data do Arquivamento

06 de dezembro de 2025

## Objetivo

Manter a documentação atualizada e alinhada com a implementação atual do sistema, removendo documentos que não refletem mais a estrutura e arquitetura implementada.

## Análise Realizada

### Estrutura Atual do Código

A implementação atual do projeto segue:
- **Padrão MVC** com separação clara de responsabilidades
- **Repositories** (`apps/api/src/api/v1/repositories/`) para acesso a dados
- **Controllers** (`apps/api/src/api/v1/controllers/`) para lógica de negócio
- **Endpoints** (`apps/api/src/api/v1/endpoints/`) para roteamento HTTP
- **Pasta `crud/`** existe mas está DEPRECATED e não é mais utilizada

### Documentos Identificados como Obsoletos

#### 1. `architecture/mvc-pattern-reorganization.md`

**Motivo**: Documento duplicado

**Análise**:
- Conteúdo idêntico a `development/coding-standards.md`
- Ambos descrevem a mesma reorganização arquitetural
- `coding-standards.md` está na pasta apropriada (`development/`) e é mais atualizado

**Decisão**: Arquivar `mvc-pattern-reorganization.md` e manter `coding-standards.md` como versão canônica.

**Justificativa**:
- Evita duplicação de conteúdo
- Mantém uma única fonte de verdade
- `development/` é a localização mais apropriada para padrões de código

#### 2. `architecture/architecture-backlog.md`

**Motivo**: Descreve estrutura obsoleta

**Análise**:
- Documento descreve a estrutura antiga do projeto com `crud/` como parte principal
- Mostra estrutura de diretórios que não reflete mais a implementação atual
- Embora tenha uma nota sobre a reorganização, ainda apresenta `crud/` como componente central
- A pasta `crud/` existe apenas para compatibilidade e está marcada como DEPRECATED

**Decisão**: Arquivar o documento, pois pode confundir novos desenvolvedores sobre a estrutura atual.

**Justificativa**:
- Estrutura descrita está obsoleta
- Pode causar confusão sobre qual estrutura seguir
- Informações históricas podem ser acessadas no archive quando necessário
- Documentação atual está disponível em outros documentos

## Documentos Mantidos e Atualizados

### `development/coding-standards.md`
- Mantido como versão canônica sobre padrões MVC
- Descreve a estrutura atual implementada
- Inclui guia de migração do código antigo

### `architecture/executive-summary.md`
- Atualizado com referências corretas
- Descreve a arquitetura atual
- Mantém visão geral das decisões arquiteturais

### `api/technical-documentation.md`
- Corrigido para mencionar "Repositories" ao invés de "CRUD"
- Reflete a estrutura atual de camadas

## Referências Atualizadas

As seguintes referências foram atualizadas:

1. **`docs/README.md`**: Removidas referências aos documentos arquivados, adicionadas referências aos documentos atuais
2. **`docs/architecture/README.md`**: Atualizado para remover referências aos documentos arquivados
3. **`docs/architecture/executive-summary.md`**: Referências atualizadas para apontar para documentos atuais
4. **`README.md` (raiz)**: Corrigida referência a `docs/DEMONSTRACAO_COMPLETA.md` (não existe mais)

## Estrutura Final

```
docs/
├── archive/                    # Documentos obsoletos (referência histórica)
│   ├── README.md               # Explicação do conteúdo arquivado
│   ├── ARCHIVING_DECISIONS.md  # Este documento
│   ├── mvc-pattern-reorganization.md
│   └── architecture-backlog.md
├── architecture/               # Documentação arquitetural atual
│   ├── executive-summary.md
│   └── acceptance-criteria-devops.md
├── development/                # Padrões e convenções atuais
│   └── coding-standards.md     # Versão canônica sobre MVC
└── ...
```

## Benefícios

1. **Clareza**: Documentação reflete apenas a implementação atual
2. **Redução de Confusão**: Novos desenvolvedores não encontram informações contraditórias
3. **Manutenibilidade**: Uma única fonte de verdade para cada tópico
4. **Histórico Preservado**: Documentos históricos ainda acessíveis no archive

## Manutenção Futura

Ao adicionar novos documentos:
1. Verificar se não duplica conteúdo existente
2. Garantir que reflete a implementação atual
3. Atualizar referências em documentos relacionados
4. Se um documento se tornar obsoleto, movê-lo para `archive/` e atualizar referências

## Conclusão

O arquivamento de documentos obsoletos melhora a qualidade e clareza da documentação, garantindo que desenvolvedores sempre encontrem informações atualizadas e precisas sobre a estrutura e arquitetura do sistema.

