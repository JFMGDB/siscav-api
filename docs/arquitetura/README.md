# Documentação de Arquitetura

Esta pasta contém a documentação arquitetural do sistema SISCAV, incluindo decisões de design, estrutura de repositórios e backlog do projeto.

## Índice

1. [Critérios de Aceite e DevOps](./01-criterios-aceite-devops.md)
   - Critérios de aceite para todas as tarefas do projeto
   - Classificação por área (DevOps, Back-end, Front-end)
   - Detalhamento de épicos e tarefas

2. [Arquitetura e Backlog do Projeto](./02-arquitetura-backlog.md)
   - Justificativa para repositórios separados
   - Estrutura de diretórios (backend e frontend)
   - Backlog completo organizado em épicos
   - Matriz de distribuição de tarefas

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

