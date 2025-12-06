# Documentação do Projeto SISCAV

Bem-vindo à documentação completa do Sistema de Controle de Acesso Veicular (SISCAV). Esta documentação fornece informações técnicas, operacionais e de desenvolvimento para todos os aspectos do sistema.

## Visão Geral

O SISCAV é uma solução completa que integra IoT, Inteligência Artificial e automação para controle de acesso veicular totalmente automatizado. O sistema utiliza reconhecimento automático de placas (ALPR) para identificar veículos e controlar o acesso através de portões automatizados.

## Estrutura da Documentação

A documentação está organizada em seções temáticas para facilitar a navegação:

### [Getting Started](./getting-started/)
Guias de início rápido para configurar e executar o sistema pela primeira vez.
- [Guia de Instalação](./getting-started/installation-guide.md)
- [Troubleshooting](./getting-started/troubleshooting.md)

### [Architecture](./architecture/)
Documentação arquitetural do sistema, decisões de design e estrutura do projeto.
- [Resumo Executivo](./architecture/executive-summary.md)
- [Critérios de Aceite e DevOps](./architecture/acceptance-criteria-devops.md)
**Nota**: Documentos históricos sobre estrutura antiga foram arquivados. Consulte [Development - Padrões de Código](./development/coding-standards.md) para a arquitetura atual.

### [Requirements](./requirements/)
Especificações funcionais e não funcionais do sistema.
- [Especificação de Projeto](./requirements/project-specification.md)

### [API](./api/)
Documentação técnica da API REST.
- [Documentação Técnica da API](../apps/api/docs/technical-documentation.md) (movido para `apps/api/docs/`)

### [Database](./database/)
Documentação do modelo de dados e migrações.
- [Modelo de Dados](../apps/api/docs/database/data-model.md) (movido para `apps/api/docs/database/`)
- [Migração para Supabase](../apps/api/docs/database/supabase-migration.md) (movido para `apps/api/docs/database/`)

### [IoT](./iot/)
Documentação do dispositivo IoT e reconhecimento de placas.
**Nota**: A documentação do dispositivo IoT foi reorganizada e movida para `apps/iot-device/docs/`.
- Consulte [Documentação do Dispositivo IoT](../apps/iot-device/docs/README.md)

### [Hardware](./hardware/)
Documentação relacionada ao firmware e hardware do Arduino.
**Nota**: A documentação de hardware foi movida para `apps/iot-device/docs/hardware/`.
- Consulte [Documentação de Hardware](../apps/iot-device/docs/hardware/)

### [Operations](./operations/)
Guias operacionais, demonstração e troubleshooting.
**Nota**: A documentação operacional do dispositivo IoT foi movida para `apps/iot-device/docs/`.
- Consulte [Documentação do Dispositivo IoT](../apps/iot-device/docs/README.md)

### [Development](./development/)
Guias para desenvolvedores, padrões de código e convenções.
- [Padrões de Código e Arquitetura](./development/coding-standards.md)

### [Project Management](./project-management/)
Documentação relacionada ao gerenciamento de projeto e rastreamento de tarefas.
- [Status das Tarefas](./project-management/backend-tasks-trello-status.md)
- [Formato de Cards do Trello](./project-management/trello-cards-format.md)

### [Presentation](./presentation/)
Materiais de apresentação do projeto.
- [README](./presentation/README.md)

### [Assets](./assets/)
Recursos visuais e evidências do projeto.
- Imagens de demonstração e resultados

## Guias Rápidos por Perfil

### Para Desenvolvedores

1. **Iniciando no projeto**: 
   - Leia [Getting Started - Instalação do Dispositivo IoT](./getting-started/README.md)
   - Consulte [Architecture - Resumo Executivo](./architecture/executive-summary.md)
   - Revise [Development - Padrões de Código](./development/coding-standards.md)

2. **Desenvolvendo API**: 
   - Consulte [API - Documentação Técnica](../apps/api/docs/technical-documentation.md)
   - Revise [Database - Modelo de Dados](../apps/api/docs/database/data-model.md)
   - Veja [Development - Padrões de Código](./development/coding-standards.md)

3. **Trabalhando com IoT**: 
   - Veja [Documentação do Dispositivo IoT](../apps/iot-device/docs/README.md)
   - Consulte [Troubleshooting](../apps/iot-device/docs/troubleshooting.md)

### Para Operadores

1. **Configuração inicial**: 
   - Siga [Guia de Instalação do Dispositivo IoT](../apps/iot-device/docs/installation.md)
   - Consulte [Guia de Demonstração](../apps/iot-device/docs/demo-guide.md)

2. **Resolução de problemas**: 
   - Veja [Getting Started - Troubleshooting](./getting-started/troubleshooting.md)
   - Consulte [Troubleshooting do Dispositivo IoT](../apps/iot-device/docs/troubleshooting.md)

3. **Avaliação de desempenho**: 
   - Siga [Guia de Demonstração e Avaliação](../apps/iot-device/docs/demo-evaluation-guide.md)

### Para Gestores

1. **Visão geral**: 
   - Leia [Requirements - Especificação de Projeto](./requirements/project-specification.md)
   - Consulte [Architecture - Resumo Executivo](./architecture/executive-summary.md)

2. **Critérios de aceitação**: 
   - Veja [Architecture - Critérios de Aceite](./architecture/acceptance-criteria-devops.md)

3. **Status do projeto**: 
   - Consulte [Project Management - Status das Tarefas](./project-management/backend-tasks-trello-status.md)

4. **Apresentação**: 
   - Veja [Presentation - README](./presentation/README.md)

## Arquitetura do Sistema

O SISCAV segue uma arquitetura de três camadas:

1. **Camada de Borda (IoT)**: Dispositivos com câmera e processamento local de reconhecimento de placas
2. **Camada de Servidor (Backend)**: API FastAPI centralizada com padrão MVC
3. **Camada de Cliente (Frontend)**: Painel de administração web (repositório separado)

## Stack Tecnológica

- **Backend**: Python, FastAPI
- **Banco de Dados**: PostgreSQL
- **ORM e Migrações**: SQLAlchemy, Alembic
- **Validação de Dados**: Pydantic
- **Autenticação**: JWT (com `passlib` para hashing)
- **Reconhecimento de Placas (IoT)**: EasyOCR, OpenCV
- **DevOps**: GitHub Actions

## Princípios Aplicados

A documentação e o código seguem os mesmos princípios:

- **SOLID**: Separação de responsabilidades em camadas
- **DRY**: Reutilização e eliminação de duplicação
- **Componentização**: Estrutura modular e extensível
- **MVC**: Separação clara entre Models, Views (Endpoints) e Controllers

## Referências Rápidas

- **Swagger/OpenAPI**: Disponível em `http://localhost:8000/docs` quando a API estiver rodando
- **Scripts SQL**: Localizados em `db/sql/supabase/`
- **Código-fonte**: Estrutura documentada em [Development - Padrões de Código](./development/coding-standards.md)

## Manutenção da Documentação

### Adicionando Nova Documentação

1. Identifique a seção apropriada
2. Use o padrão de nomenclatura consistente
3. Atualize este README com a referência ao novo documento
4. Mantenha a estrutura hierárquica

### Atualizando Documentação Existente

1. Mantenha a estrutura e formatação consistente
2. Atualize a data de modificação se relevante
3. Documente decisões importantes e suas justificativas
4. Remova informações obsoletas

## Contribuindo

Para contribuir com a documentação:

1. Siga a estrutura existente
2. Mantenha o tom profissional e técnico
3. Inclua exemplos práticos quando relevante
4. Atualize os índices e referências cruzadas

## Contato

Para dúvidas sobre a documentação ou sugestões de melhoria, consulte a equipe de desenvolvimento do projeto.
