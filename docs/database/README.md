# Database Documentation

Esta pasta contém toda a documentação relacionada ao modelo de dados e migrações do sistema SISCAV.

## Documentos Disponíveis

### [Modelo de Dados](../../apps/api/docs/database/data-model.md)
Especificação técnica completa do modelo de dados, incluindo:
- Entidades principais (users, authorized_plates, access_logs)
- Decisões arquiteturais (UUIDs, TIMESTAMPTZ, ENUMs)
- DDL completo para PostgreSQL
- Estratégias de indexação e integridade referencial
- Considerações de escalabilidade

### [Migração para Supabase](../../apps/api/docs/database/supabase-migration.md)
Guia para migração manual quando Docker/Alembic não estão disponíveis:
- Extensões necessárias
- Tipos ENUM
- Tabelas e índices
- Integração com Alembic

**Nota**: A documentação do banco de dados foi movida para `apps/api/docs/database/` para ficar próximo ao código da API.

## Descrição

O banco de dados PostgreSQL do SISCAV é projetado para:

- **Segurança**: Uso de UUIDs para chaves primárias
- **Consistência**: Tipos ENUM para integridade de dados
- **Auditoria**: Timestamps com timezone (TIMESTAMPTZ)
- **Performance**: Índices otimizados para consultas frequentes
- **Escalabilidade**: Suporte a particionamento e extensões futuras

## Entidades Principais

- **users**: Administradores do sistema
- **authorized_plates**: Whitelist de placas autorizadas
- **access_logs**: Trilha de auditoria de tentativas de acesso

## Scripts SQL

Scripts SQL para migração manual estão localizados em `db/sql/supabase/`:
- `01_enable_extensions.sql` (pgcrypto, pg_trgm)
- `02_types.sql` (ENUM `access_status`)
- `03_tables.sql` (`users`, `authorized_plates`, `access_logs`)
- `04_indexes.sql` (índices recomendados e opcionais com pg_trgm)

## Referências

- [Documentação da API](../api/README.md)
- [Documentação de Arquitetura](../architecture/README.md)
