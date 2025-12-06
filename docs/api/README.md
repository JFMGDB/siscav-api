# Documentação da API

Esta pasta contém toda a documentação relacionada à API do sistema SISCAV.

## Índice

- [Documentação Técnica da API](../../apps/api/docs/technical-documentation.md)
   - Visão geral da arquitetura
   - Decisões técnicas
   - Recursos e endpoints
   - Acesso ao Swagger UI

**Nota**: A documentação técnica da API foi movida para `apps/api/docs/technical-documentation.md` para ficar próximo ao código-fonte.

Para informações sobre padrões de código e arquitetura, consulte também [Development - Padrões de Código](../development/coding-standards.md)

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













