# Documentação de Arquitetura

Esta pasta contém a documentação arquitetural do sistema SISCAV, incluindo decisões de design, estrutura de repositórios e backlog do projeto.

## Índice

- [Resumo Executivo](./executive-summary.md)
  - Visão geral da arquitetura
  - Decisões arquiteturais principais
  - Componentes e tecnologias
  - Benefícios e justificativas

- [Critérios de Aceite e DevOps](./acceptance-criteria-devops.md)
  - Critérios de aceite para todas as tarefas do projeto
  - Classificação por área (DevOps, Back-end, Front-end)
  - Detalhamento de épicos e tarefas

**Nota**: Documentos históricos sobre a estrutura antiga e reorganização foram movidos para `archive/`. Para documentação atual sobre arquitetura e padrões, consulte:
- [Development - Padrões de Código](../development/coding-standards.md) - Padrão MVC implementado
- [Executive Summary](./executive-summary.md) - Visão geral da arquitetura atual

## Descrição

A arquitetura do SISCAV segue uma abordagem de três camadas:

1. **Camada de Borda (IoT)**: Dispositivos com câmera e processamento local
2. **Camada de Servidor (Backend)**: API FastAPI centralizada
3. **Camada de Cliente (Frontend)**: Painel de administração web

## Decisões Arquiteturais

- Separação de repositórios (backend e frontend)
- Uso de FastAPI para alta performance e documentação automática
- PostgreSQL para persistência de dados
- JWT para autenticação stateless
- Componentização e modularidade
- **Padrão MVC**: Separação clara entre Models, Views (Endpoints) e Controllers
- **Repository Pattern**: Isolamento de acesso a dados
- **Service Layer (Controllers)**: Centralização de lógica de negócio
- **SOLID e DRY**: Aplicação rigorosa de princípios de design













