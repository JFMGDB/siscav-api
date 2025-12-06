# Archive

Esta pasta contém documentação obsoleta que não reflete mais a implementação atual do sistema, mas é mantida para referência histórica.

## Documentos Arquivados

### [mvc-pattern-reorganization.md](./mvc-pattern-reorganization.md)
**Motivo**: Documento duplicado. O conteúdo idêntico está disponível em `docs/development/coding-standards.md`, que é a versão mantida e atualizada.

**Data de Arquivamento**: 06 de dezembro de 2025

**Versão Atual**: Consulte `docs/development/coding-standards.md`

### [architecture-backlog.md](./architecture-backlog.md)
**Motivo**: Documento descreve a estrutura antiga do projeto com `crud/` como parte principal da arquitetura. A implementação atual usa `repositories/` e `controllers/` seguindo o padrão MVC.

**Data de Arquivamento**: 06 de dezembro de 2025

**Status**: Estrutura descrita está obsoleta. A pasta `crud/` existe apenas para compatibilidade e está marcada como DEPRECATED.

**Estrutura Atual**: Consulte:
- `docs/architecture/executive-summary.md` - Visão geral da arquitetura atual
- `docs/development/coding-standards.md` - Padrões e estrutura implementada
- `docs/README.md` - Índice completo da documentação

## Por que arquivar?

Estes documentos foram arquivados porque:

1. **Duplicação**: Conteúdo idêntico disponível em outros documentos mais atualizados
2. **Estrutura Obsoleta**: Descrevem arquitetura que não reflete mais a implementação atual
3. **Confusão Potencial**: Podem confundir novos desenvolvedores sobre a estrutura atual do projeto

## Acesso

Os documentos arquivados permanecem acessíveis para:
- Referência histórica
- Entendimento da evolução do projeto
- Contexto sobre decisões arquiteturais anteriores

## Nota

Se você está procurando documentação sobre a arquitetura atual, consulte:
- `docs/architecture/executive-summary.md`
- `docs/development/coding-standards.md`
- `docs/README.md`

