# Documentação da API

Esta pasta contém toda a documentação relacionada à API do sistema SISCAV.

## Índice

1. [Documentação Técnica da API](./01-documentacao-tecnica.md)
   - Visão geral da arquitetura
   - Decisões técnicas
   - Recursos e endpoints
   - Acesso ao Swagger UI

2. [Resumo de Refatoração da API](./02-refatoracao-api.md)
   - Melhorias implementadas
   - Correções de bugs
   - Aplicação de princípios SOLID, DRY e Componentização
   - Decisões de design

## Descrição

A API SISCAV é construída com FastAPI e serve como o backend central do sistema. Ela gerencia:

- Autenticação de administradores (JWT)
- Gerenciamento de whitelist de placas
- Recebimento e processamento de logs de acesso dos dispositivos IoT
- Controle remoto do portão
- Servir imagens de acesso de forma segura

## Princípios Aplicados

- **SOLID**: Separação de responsabilidades em camadas (Routers, CRUD, Schemas, Models)
- **DRY**: Reutilização de utilitários e funções compartilhadas
- **Componentização**: Estrutura modular e extensível

