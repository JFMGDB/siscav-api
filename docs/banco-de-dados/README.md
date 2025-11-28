# Documentação de Banco de Dados

Esta pasta contém toda a documentação relacionada ao modelo de dados e migrações do sistema SISCAV.

## Índice

1. [Modelo de Dados](./01-modelo-de-dados.md)
   - Especificação técnica completa do modelo de dados
   - Entidades principais (users, authorized_plates, access_logs)
   - Decisões arquiteturais (UUIDs, TIMESTAMPTZ, ENUMs)
   - DDL completo para PostgreSQL
   - Estratégias de indexação e integridade referencial
   - Considerações de escalabilidade

2. [Migração para Supabase](./02-migracao-supabase.md)
   - Guia para migração manual quando Docker/Alembic não estão disponíveis
   - Extensões necessárias
   - Tipos ENUM
   - Tabelas e índices
   - Integração com Alembic

## Descrição

O banco de dados PostgreSQL do SISCAV é projetado para:

- Segurança: Uso de UUIDs para chaves primárias
- Consistência: Tipos ENUM para integridade de dados
- Auditoria: Timestamps com timezone (TIMESTAMPTZ)
- Performance: Índices otimizados para consultas frequentes
- Escalabilidade: Suporte a particionamento e extensões futuras

## Entidades Principais

- **users**: Administradores do sistema
- **authorized_plates**: Whitelist de placas autorizadas
- **access_logs**: Trilha de auditoria de tentativas de acesso

