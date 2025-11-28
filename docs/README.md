# Documentação do Projeto SISCAV

Este diretório contém toda a documentação técnica e operacional do Sistema de Controle de Acesso Veicular (SISCAV).

## Estrutura da Documentação

A documentação está organizada em categorias para facilitar a navegação e localização de informações:

### [arquitetura/](./arquitetura/)
Documentação relacionada à arquitetura do sistema, decisões de design e critérios de aceitação.

- **01-criterios-aceite-devops.md**: Critérios de aceitação detalhados para todos os épicos do projeto, incluindo DevOps, Backend e Frontend.
- **02-arquitetura-backlog.md**: Visão geral da arquitetura do sistema, estrutura de diretórios e backlog completo do projeto.

### [requisitos/](./requisitos/)
Especificações funcionais e não funcionais do sistema.

- **01-especificacao-projeto.md**: Documento completo de especificação do projeto, incluindo requisitos funcionais (RF) e não funcionais (RNF), arquitetura proposta e fases de desenvolvimento.

### [api/](./api/)
Documentação técnica da API REST.

- **01-documentacao-tecnica.md**: Documentação técnica completa da API, incluindo decisões técnicas, padrões aplicados (SOLID, DRY, Componentização) e recursos disponíveis.
- **02-refatoracao-api.md**: Resumo das melhorias e refatorações aplicadas à API, seguindo princípios SOLID, DRY e Componentização.

### [banco-de-dados/](./banco-de-dados/)
Documentação do modelo de dados e migrações.

- **01-modelo-de-dados.md**: Especificação completa do modelo de dados, incluindo entidades, relacionamentos, decisões arquiteturais e estratégias de indexação.
- **02-migracao-supabase.md**: Guia para migração manual do banco de dados no Supabase, incluindo scripts SQL e procedimentos.

### [iot/](./iot/)
Documentação do dispositivo IoT e reconhecimento de placas.

- **01-refatoracao-dispositivo-iot.md**: Documentação detalhada da refatoração do dispositivo IoT, melhorias implementadas e arquitetura.
- **02-resumo-dispositivo-iot.md**: Resumo executivo das melhorias no sistema de reconhecimento de placas.

### [operacao/](./operacao/)
Guias operacionais, demonstração e troubleshooting.

- **01-guia-demonstracao.md**: Guia completo para demonstração do sistema.
- **02-guia-demonstracao-avaliacao.md**: Guia detalhado para demonstração e avaliação de desempenho do sistema de reconhecimento de placas.
- **03-troubleshooting-instalacao.md**: Guia de troubleshooting para problemas comuns durante a instalação das dependências do dispositivo IoT.
- **04-regressao-python312.md**: Documentação da regressão para Python 3.12 e resolução de problemas de compatibilidade.
- **05-solucao-erro-numpy.md**: Solução rápida para erros de compilação do NumPy.
- **06-solucao-final-python314.md**: Solução final para problemas com Python 3.14 e dependências.

### [presentation/](./presentation/)
Materiais de apresentação do projeto.

- **README.md**: Instruções para visualizar e exportar a apresentação técnica.

## Decisões de Organização

### Categorização por Domínio

A documentação foi organizada seguindo o princípio de separação por domínio de conhecimento:

1. **Arquitetura**: Decisões de alto nível e estrutura do sistema
2. **Requisitos**: O que o sistema deve fazer
3. **API**: Como a API funciona tecnicamente
4. **Banco de Dados**: Estrutura e gerenciamento de dados
5. **IoT**: Componente de borda e reconhecimento de placas
6. **Operação**: Como usar e manter o sistema
7. **Apresentação**: Materiais para demonstração

### Padronização de Nomes

Todos os arquivos seguem o padrão:
- `NN-nome-descritivo.md` onde `NN` é um número sequencial de dois dígitos
- Nomes em minúsculas com hífens
- Descrições claras e específicas

### Princípios Aplicados

A organização segue os mesmos princípios aplicados ao código:

- **SOLID**: Cada categoria tem responsabilidade única
- **DRY**: Evita duplicação de informações
- **Componentização**: Documentação modular e reutilizável

## Como Usar Esta Documentação

### Para Desenvolvedores

1. **Iniciando no projeto**: Comece por `requisitos/01-especificacao-projeto.md` e `arquitetura/02-arquitetura-backlog.md`
2. **Desenvolvendo API**: Consulte `api/01-documentacao-tecnica.md` e `banco-de-dados/01-modelo-de-dados.md`
3. **Trabalhando com IoT**: Veja `iot/01-refatoracao-dispositivo-iot.md` e `operacao/03-troubleshooting-instalacao.md`

### Para Operadores

1. **Configuração inicial**: `operacao/01-guia-demonstracao.md`
2. **Resolução de problemas**: `operacao/03-troubleshooting-instalacao.md`
3. **Avaliação de desempenho**: `operacao/02-guia-demonstracao-avaliacao.md`

### Para Gestores

1. **Visão geral**: `requisitos/01-especificacao-projeto.md`
2. **Critérios de aceitação**: `arquitetura/01-criterios-aceite-devops.md`
3. **Apresentação**: `presentation/README.md`

## Manutenção da Documentação

### Adicionando Nova Documentação

1. Identifique a categoria apropriada
2. Use o padrão de nomenclatura `NN-nome-descritivo.md`
3. Atualize este README com a referência ao novo documento
4. Mantenha a numeração sequencial dentro de cada categoria

### Atualizando Documentação Existente

1. Mantenha a estrutura e formatação consistente
2. Atualize a data de modificação se relevante
3. Documente decisões importantes e suas justificativas
4. Remova informações obsoletas

## Referências Rápidas

- **Swagger/OpenAPI**: Disponível em `http://localhost:8000/docs` quando a API estiver rodando
- **Scripts SQL**: Localizados em `db/sql/supabase/`
- **Código-fonte**: Estrutura documentada em `arquitetura/02-arquitetura-backlog.md`

## Contato

Para dúvidas sobre a documentação ou sugestões de melhoria, consulte a equipe de desenvolvimento do projeto.

