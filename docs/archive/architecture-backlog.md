# Visão Geral

Esta seção justifica e detalha a decisão arquitetural de mais alto nível: organizar o projeto em
dois repositórios distintos, um para o backend e outro para o frontend.

## 1.1. Racional para uma Arquitetura com Repositórios Separados

O projeto envolve bases de código com tecnologias fundamentalmente diferentes: um
frontend em JavaScript/TypeScript e um backend em Python, que também abrigará o script
IoT.^1 Separar esses componentes em seus próprios repositórios é uma abordagem clássica e
robusta que oferece vários benefícios, especialmente para uma equipe em aprendizado:
● **Clareza e Foco:** Cada repositório tem um propósito único e uma pilha de tecnologia
singular. Desenvolvedores de frontend não precisam lidar com o ferramental de Python, e
vice-versa. Isso reduz a carga cognitiva e permite que os membros da equipe se
concentrem em sua área de especialização.
● **Ciclos de Vida Independentes:** O frontend e o backend podem ser desenvolvidos,
testados e implantados de forma independente. Uma alteração na interface do usuário
não requer a execução de todo o pipeline de CI/CD do backend, levando a implantações
mais rápidas e seguras.
● **Gerenciamento de Dependências Simplificado:** Cada repositório gerencia seu próprio
conjunto de dependências (package.json para o frontend, pyproject.toml para o
backend). Isso evita a complexidade de gerenciar dependências de linguagens diferentes
em um único local e previne conflitos.
● **Autonomia da Equipe:** Em um cenário profissional, essa separação permite que equipes
de frontend e backend operem com maior autonomia, com a API RESTful servindo como
um contrato bem definido entre elas.

## 1.2. Estrutura de Diretórios dos Projetos

A seguir, uma representação visual das estruturas de diretórios para os dois repositórios
principais.
**Repositório Backend (siscav-api):**
controle-acesso-veicular-api/
├──.git/
├──.github/
│ └── workflows/
│ └── ci.yml
├── apps/
│ ├── api/ # Serviço Backend FastAPI
│ └── iot-device/ # Script Python ALPR IoT
├──.dockerignore
├──.gitignore


├── docker-compose.yml
├── pyproject.toml
└── README.md
**Repositório Frontend (siscav-web):**
controle-acesso-veicular-web/
├──.git/
├──.github/
│ └── workflows/
│ └── ci.yml
├── src/
│ └── (Estrutura interna do Next.js)
├──.dockerignore
├──.eslintrc.js
├──.gitignore
├── package.json
├── next.config.mjs
└── README.md
● **Repositório de Backend:**
○ siscav-api: Este repositório contém toda a lógica do lado do servidor.
○ apps/: Uma pasta que organiza as diferentes aplicações Python. api contém o
serviço FastAPI, e iot-device contém o script para o hardware.
○ pyproject.toml: Define as dependências e configurações do projeto Python.
○ docker-compose.yml: Um arquivo Docker Compose para desenvolvimento local,
definindo serviços para a api e o banco de dados PostgreSQL. Ele pode ser
configurado para se conectar ao serviço de frontend em execução localmente.
● **Repositório de Frontend:**
○ siscav-veicular-web: Este repositório é dedicado exclusivamente à aplicação de
painel de administração Next.js.
○ package.json: O centro de comando do projeto frontend, gerenciando scripts,
dependências e configurações de ferramentas como ESLint e Prettier.
○ .github/workflows/ci.yml: Uma definição de pipeline de CI dedicada ao frontend, que
executa lint, testes e compilação da aplicação Next.js.


# Backend

Esta seção detalha a estrutura interna da aplicação FastAPI, priorizando a clareza e a
adesão às melhores práticas.

## 2.1. Estrutura de Diretórios Orientada a Domínio

sisvac-api/
├── alembic/ # Scripts de migração de banco de dados
├── src/
│ ├── api/
│ │ ├── v1/
│ │ │ ├── endpoints/
│ │ │ │ ├── auth.py
│ │ │ │ ├── whitelist.py
│ │ │ │ ├── access_logs.py
│ │ │ │ └── gate_control.py
│ │ │ └── api.py # Agrega todos os roteadores v
│ ├── core/
│ │ ├── config.py # Gerenciamento de configurações com Pydantic
│ │ └── security.py # Lógica de hashing de senha, JWT
│ ├── crud/
│ │ ├── crud_whitelist.py
│ │ └── crud_user.py
│ ├── db/
│ │ ├── base.py # Base declarativa e modelos base
│ │ └── session.py # Dependência da sessão do banco de dados
│ ├── models/
│ │ ├── access_log.py
│ │ ├── user.py
│ │ └── authorized_plate.py
│ ├── schemas/
│ │ ├── access_log.py
│ │ ├── token.py
│ │ ├── user.py
│ │ └── authorized_plate.py
│ └── main.py # Instanciação da aplicação FastAPI
├── tests/
├──.env
├── alembic.ini
└── README.md


## 2.2. Componentes Centrais do Serviço

> **Nota**: Esta seção descreve a estrutura inicial do projeto. A arquitetura foi posteriormente reorganizada seguindo o padrão MVC com Repositories e Controllers. Para a estrutura atual, consulte `../development/coding-standards.md` ou `../architecture/executive-summary.md`.

```
● main.py: O ponto de entrada.
● api/v1/endpoints/: Cada arquivo aqui é um APIRouter para um domínio específico,
contendo as operações de rota (ex: @router.post("/login")).^
● schemas/: Contém modelos Pydantic para a validação do corpo da requisição,
serialização da resposta e são a fonte para o Swagger/OpenAPI.^
● models/: Contém as definições das tabelas do banco de dados SQLAlchemy.
● crud/: Contém funções que interagem diretamente com a sessão e os modelos do banco
de dados (ex: get_user_by_email, create_plate). [DEPRECATED - Use repositories/ e controllers/]
● core/: Para preocupações de toda a aplicação, como carregamento de configuração de
variáveis de ambiente (config.py) e funções de segurança (security.py) para hashing de
senhas e criação/validação de tokens JWT.
● db/: Gerencia a conexão e a sessão do banco de dados, fornecendo uma dependência
reutilizável (get_db) para os endpoints.^
● alembic/: Lida com as migrações de esquema do banco de dados.^
```

# Frontend

Esta seção descreve a estrutura para o painel de administração Next.js, utilizando o
App Router.

## 3.1. Organização do App Router (src/app)

src/
├── app/
│ ├── (auth)/ # Rotas que exigem autenticação
│ │ ├── dashboard/
│ │ │ ├── layout.tsx
│ │ │ └── page.tsx
│ │ ├── whitelist/
│ │ │ └── page.tsx
│ │ └── logs/
│ │ └── page.tsx
│ ├── (public)/ # Rotas de acesso público
│ │ └── login/
│ │ └── page.tsx
│ ├── layout.tsx # Layout raiz
│ └── page.tsx # Página raiz (redireciona para login/dashboard)
├── components/
│ ├── features/ # Componentes específicos de funcionalidades
│ │ ├── auth/Login-Form.tsx
│ │ ├── whitelist/Whitelist-Table.tsx
│ │ └── logs/Logs-Filter.tsx
│ └── ui/ # Componentes de UI genéricos e reutilizáveis (baseados em MUI)
├── hooks/
│ └── use-auth.ts
├── lib/
│ ├── api-client.ts # Cliente tipado para interagir com o backend FastAPI
│ └── utils.ts # Funções utilitárias gerais
└── styles/
└── globals.css

## 3.2. Estratégia de Design Baseada em Componentes

```
● components/ui/: Esta pasta conterá componentes de UI genéricos e reutilizáveis (ex:
botões estilizados, contêineres de layout, tabelas de dados) construídos sobre o MUI.
● components/features/: Estes são componentes "inteligentes" que estão cientes da
lógica de negócios da aplicação. Por exemplo, Whitelist-Table.tsx será responsável por
buscar dados da lista de permissões através do api-client e gerenciar seu próprio
```

```
estado, enquanto usa componentes genéricos como Table, Button e Modal de
components/ui.^
```
## 3.3. Lógica Central do Frontend

```
● lib/api-client.ts: Este é um arquivo crítico. Ele conterá um wrapper tipado (talvez usando
fetch ou uma biblioteca como axios) para todas as interações com o backend FastAPI. O
uso de TypeScript aqui garante que, se a forma da resposta da API mudar, o código do
frontend mostrará erros em tempo de compilação.
● hooks/: Para hooks React personalizados que encapsulam lógica reutilizável, como o
gerenciamento do estado de autenticação (use-auth.ts).
● Gerenciamento de Estado: Para o escopo deste projeto, uma combinação do
gerenciamento de estado integrado do React (useState, useContext) e de uma biblioteca
de busca de dados do lado do cliente como SWR ou React Query para evitar a
sobrecarga de uma biblioteca de gerenciamento de estado completa como o Redux.
```

# Especificações

```
Esta seção traduz a especificação do projeto em um backlog, estruturado em épicos,
```
## Épico 1: Fundação do Projeto & DevOps

```
● Objetivo: Estabelecer o ambiente de desenvolvimento, controle de versão e pipeline de
CI/CD. Este é um trabalho fundamental que deve ser feito primeiro.
● Tarefas:
```
1. FND-01: Configurar repositórios Git separados para backend (api) e frontend (web).
2. FND-02: Criar arquivo Docker Compose para desenvolvimento local (FastAPI, Next.js,
    PostgreSQL).
3. FND-03: Inicializar a estrutura da aplicação FastAPI e dependências (pyproject.toml).
4. FND-04: Inicializar a estrutura da aplicação Next.js e dependências (package.json).
5. FND-05: Configurar Alembic para migrações de banco de dados e criar modelos de
    esquema iniciais.
6. FND-06: Implementar um endpoint básico de "verificação de saúde" na API.
7. FND-07: Implementar uma página de placeholder básica na aplicação Next.js.
8. FND-08: Configurar pipelines de CI básicos no GitHub Actions para os repositórios
    de backend e frontend.

## Épico 2: Implementação do Dispositivo IoT ALPR

```
● Objetivo: Desenvolver a lógica central para o endpoint do hardware.^
● Tarefas:
```
1. IOT-01: Escrever um script para capturar uma imagem de alta resolução da câmera.
2. IOT-02: Integrar a biblioteca easyocr para extrair texto de uma imagem de amostra
    capturada.
3. IOT-03: Desenvolver uma função para pré-processar a imagem para melhorar a
    precisão do OCR (escala de cinza, ajuste de contraste).
4. IOT-04: Desenvolver uma função para formatar a string da placa extraída (remover
    caracteres especiais, maiúsculas).
5. IOT-05: Implementar requisição POST HTTPS segura para enviar dados da placa e
    imagem para a API do backend.
6. IOT-06: Implementar lógica para analisar a resposta da API (Autorizado/Negado).
7. IOT-07: Escrever um script para controlar um pino GPIO para acionar o módulo de
    relé com base na resposta da API.

## Épico 3: Controle de Acesso Central & Logging (Backend)

```
● Objetivo: Construir o "cérebro" do backend que recebe dados do dispositivo IoT e
registra eventos.
● Tarefas:
```
1. API-01: Criar o endpoint da API access_logs para receber dados da placa e um
    arquivo de imagem do dispositivo IoT.


2. API-02: Implementar a lógica de negócios para consultar a tabela authorized_plates
    por uma correspondência.
3. API-03: Implementar lógica para armazenar a imagem capturada, potencialmente em
    um object store (como MinIO ou S3) ou no sistema de arquivos.
4. API-04: Criar o modelo AccessLog e funções CRUD para salvar cada tentativa de
    acesso no banco de dados.
5. API-05: Implementar a lógica de resposta da API. Por exemplo, ({"status":
    "Authorized"} ou {"status": "Denied"}).
6. API-06: Criar o endpoint da API gate_control para acionamento manual remoto.
7. API-07: Escrever testes unitários para a lógica de verificação de placas.

## Épico 4: Autenticação de Administrador

```
● Objetivo: Implementar um sistema de login seguro e full-stack para o painel.
● Tarefas:
```
1. AUTH-01 (BE): Criar modelo User e funções CRUD, incluindo hashing seguro de
    senha.
2. AUTH-02 (BE): Implementar um endpoint /login que valida credenciais e retorna um
    token JWT.
3. AUTH-03 (BE): Implementar dependência FastAPI para proteger endpoints, exigindo
    um JWT válido.
4. AUTH-04 (FE): Construir a página de Login e a UI do formulário na aplicação Next.js
    ((public)/login).
5. AUTH-05 (FE): Implementar lógica no api-client para chamar o endpoint /login e
    armazenar o JWT de forma segura (ex: em um cookie httpOnly).
6. AUTH-06 (FE): Implementar um layout protegido ((auth)/layout.tsx) que verifica o
    estado de autenticação do usuário e redireciona para o login se necessário.
7. AUTH-07 (Full-Stack): Implementar um botão "Sair" que limpa a sessão do usuário
    tanto no cliente quanto no servidor.

## Épico 5: Painel de Gerenciamento da Whitelist

```
● Objetivo: Construir a interface CRUD completa para gerenciar placas autorizadas.
● Tarefas:
```
1. WHT-01 (BE): Criar o modelo AuthorizedPlate e o conjunto completo de endpoints
    CRUD para ele (Criar, Ler, Atualizar, Deletar).
2. WHT-02 (FE): Projetar e construir a UI para a página da Whitelist, incluindo uma
    tabela de dados para exibir as placas.
3. WHT-03 (FE): Implementar a funcionalidade "Ler": buscar e exibir todas as placas
    autorizadas na tabela de dados.
4. WHT-04 (FE): Implementar a funcionalidade "Criar": um modal/formulário para
    adicionar uma nova placa à lista.
5. WHT-05 (FE): Implementar a funcionalidade "Atualizar": um botão "Editar" em cada
    linha para modificar os detalhes de uma placa.
6. WHT-06 (FE): Implementar a funcionalidade "Deletar": um botão "Deletar" com um


```
diálogo de confirmação para remover uma placa.
```
7. WHT-07 (FE): Adicionar funcionalidade de busca e paginação à tabela da whitelist.

## Épico 6: Painel de Visualização de Logs de Acesso

```
● Objetivo: Construir a interface para os administradores revisarem o histórico de acesso.
● Tarefas:
```
1. LOG-01 (BE): Criar o endpoint da API para listar logs de acesso com suporte para
    paginação, filtragem por intervalo de datas, placa e status.
2. LOG-02 (FE): Projetar e construir a UI para a página de Logs de Acesso, incluindo
    uma tabela de dados e controles de filtro.
3. LOG-03 (FE): Implementar a funcionalidade "Ler": buscar e exibir logs na tabela.
4. LOG-04 (FE): Implementar os controles de filtro (seletores de data, entrada de texto
    para placa, dropdown para status).
5. LOG-05 (FE): Implementar a lógica para exibir a imagem do veículo capturada, talvez
    em um modal quando uma entrada de log for clicada.
6. LOG-06 (BE): Garantir que o endpoint da API que serve imagens seja seguro e
    acessível apenas para administradores autenticados.
7. LOG-07 (Full-Stack): Implementar o botão de acionamento remoto do portão no
    painel que chama o endpoint da API gate_control.

## Épico 7: Reforço e Polimento do Sistema

```
● Objetivo: Abordar requisitos não funcionais e preparar o sistema para implantação.
● Tarefas:
```
1. HRD-01 (BE): Gerar e refinar a documentação automática Swagger/OpenAPI para a
    API.
2. HRD-02 (BE): Implementar limitação de taxa no endpoint de login para prevenir
    ataques de força bruta.
3. HRD-03 (FE): Garantir que a UI do painel seja totalmente responsiva e intuitiva.
4. HRD-04 (IoT): Implementar um watchdog ou serviço systemd no Raspberry Pi para
    garantir que o script ALPR reinicie automaticamente em caso de falha (RNF-003).
5. HRD-05 (DevOps): Criar Dockerfiles prontos para produção para as aplicações api e
    web.
6. HRD-06 (Docs): Escrever os arquivos README.md para cada aplicação, explicando
    os procedimentos de configuração e desenvolvimento.
7. HRD-07 (QA): Realizar testes de ponta a ponta de todo o fluxo, desde a aproximação
    do veículo até a abertura do portão, e medir em relação ao requisito de latência de 5
    segundos.


## Matriz de Distribuição de Tarefas e Balanceamento de Carga de

## Trabalho

```
ID da
Tarefa
Épico Breve
Descrição
Ref.
Requisito
Stack
Principal
Desenvolv
edor
Atribuído
Complexid
ade
(Pontos)
FND-01 Fundação Configurar
repositórios
Git
separados
N/A DevOps Dev 1 5
FND-02 Fundação Criar
Docker
Compose
local
N/A DevOps Dev 2 3
FND-03 Fundação Inicializar
estrutura
FastAPI
N/A Backend Dev 3 2
FND-04 Fundação Inicializar
estrutura
Next.js
N/A Frontend Dev 4 2
FND-05 Fundação Configurar
Alembic e
modelos
N/A Backend Dev 5 3
FND-06 Fundação Endpoint
de "health
check"
N/A Backend Dev 6 1
FND-07 Fundação Página
placeholder
Next.js
N/A Frontend Dev 7 1
FND-08 Fundação Pipelines
de CI para
cada
repositório
N/A DevOps Dev 1 5
IOT-01 IoT ALPR Capturar
imagem da
RF-001 IoT Dev 2 3
```

câmera
IOT-02 IoT ALPR Integrar
easyocr
RF-003 IoT Dev 3 5
IOT-03 IoT ALPR Pré-proces
samento de
imagem
RF-002 IoT Dev 4 3
IOT-04 IoT ALPR Formatar
string da
placa
RF-004 IoT Dev 5 2
IOT-05 IoT ALPR Requisição
HTTPS para
API
RNF-005 IoT Dev 6 3
IOT-06 IoT ALPR Analisar
resposta da
API
N/A IoT Dev 7 1
IOT-07 IoT ALPR Controlar
GPIO para
relé
RF-005 IoT Dev 1 3
API-01 Controle
Acesso
Endpoint
access_log
s
RF-006 Backend Dev 2 3
API-02 Controle
Acesso
Lógica de
verificação
da placa
RF-004 Backend Dev 3 2
API-03 Controle
Acesso
Armazenam
ento de
imagem
RF-006 Backend Dev 4 5
API-04 Controle
Acesso
Modelo e
CRUD
AccessLog
RF-006 Backend Dev 5 2
API-05 Controle
Acesso
Lógica de
resposta da
API
N/A Backend Dev 6 1


API-06 Controle
Acesso
Endpoint
gate_contr
ol
RF-010 Backend Dev 7 2
API-07 Controle
Acesso
Testes
unitários da
verificação
N/A Backend Dev 1 3
AUTH-01 Autenticaçã
o
Modelo
User e
hashing
RNF-006 Backend Dev 2 3
AUTH-02 Autenticaçã
o
Endpoint
de login
JWT
RF-007 Backend Dev 3 5
AUTH-03 Autenticaçã
o
Proteção
de
endpoints
RF-007 Backend Dev 4 3
AUTH-04 Autenticaçã
o
UI da
página de
Login
RF-007 Frontend Dev 5 2
AUTH-05 Autenticaçã
o
Lógica de
chamada
ao login
N/A Frontend Dev 6 3
AUTH-06 Autenticaçã
o
Layout
protegido
N/A Frontend Dev 7 3
AUTH-07 Autenticaçã
o
Funcionalid
ade "Sair"
N/A Full-Stack Dev 1 2
WHT-01 Whitelist Endpoints
CRUD
Whitelist
RF-008 Backend Dev 2 3
WHT-02 Whitelist UI da
página
Whitelist
RF-008 Frontend Dev 3 3
WHT-03 Whitelist Funcionalid
ade "Ler"
RF-008 Frontend Dev 4 2


WHT-04 Whitelist Funcionalid
ade "Criar"
RF-008 Frontend Dev 5 3
WHT-05 Whitelist Funcionalid
ade
"Atualizar"
RF-008 Frontend Dev 6 3
WHT-06 Whitelist Funcionalid
ade
"Deletar"
RF-008 Frontend Dev 7 3
WHT-07 Whitelist Busca e
paginação
RF-008 Full-Stack Dev 1 5
LOG-01 Logs
Acesso
Endpoint
de listagem
de logs
RF-009 Backend Dev 2 5
LOG-02 Logs
Acesso
UI da
página de
Logs
RF-009 Frontend Dev 3 3
LOG-03 Logs
Acesso
Funcionalid
ade "Ler"
RF-009 Frontend Dev 4 2
LOG-04 Logs
Acesso
Controles
de filtro
RF-009 Frontend Dev 5 3
LOG-05 Logs
Acesso
Exibição da
imagem
RF-009 Frontend Dev 6 2
LOG-06 Logs
Acesso
Endpoint
seguro de
imagem
N/A Backend Dev 7 3
LOG-07 Logs
Acesso
Botão de
acionament
o remoto
RF-010 Full-Stack Dev 1 2
HRD-01 Polimento Documenta
ção
Swagger
N/A Backend Dev 2 2


```
HRD-02 Polimento Rate
limiting no
login
RNF-006 Backend Dev 3 3
HRD-03 Polimento UI
responsiva
e intuitiva
RNF-007 Frontend Dev 4 3
HRD-04 Polimento Watchdog
no script
IoT
RNF-003 IoT Dev 5 3
HRD-05 Polimento Dockerfiles
de
produção
N/A DevOps Dev 6 5
HRD-06 Polimento Documenta
ção
README.m
d
RNF-008 Docs Dev 7 2
HRD-07 Polimento Testes E2E
e de
latência
RNF-001 QA Dev 1 5
```
# Conclusão

## Sumário dos Entregáveis

Este relatório forneceu um plano arquitetural abrangente, detalhando a estrutura de
repositórios separados, as arquiteturas internas das aplicações de backend e frontend, e um
backlog de projeto granular e equilibrado. A arquitetura proposta é projetada para
escalabilidade, manutenibilidade e, crucialmente, para o desenvolvimento de habilidades da
equipe.

## Caminho para o Sucesso

Este roteiro fornece um caminho claro e robusto para o futuro. Ao aderir a essas estruturas e
processos, a equipe está bem equipada não apenas para entregar um "Sistema de Controle
de Acesso de Veículos" funcional, mas também para ganhar uma experiência inestimável em
práticas modernas de engenharia de software.


## Próximos Passos

Recomenda-se que a equipe comece com o "Épico 1: Fundação do Projeto & DevOps" para
estabelecer seu ambiente de desenvolvimento antes de prosseguir para o desenvolvimento
de funcionalidades. Esta fase inicial é crítica para garantir que todas as ferramentas e
processos estejam em vigor, permitindo um ciclo de desenvolvimento suave e eficiente para
os épicos subsequentes.

### Referências citadas

### 1. piiv-unicap-especificacao-projetos-solucoes-eletronicas-do-futuro_v1.pdf

### 2. How to Structure Your FastAPI Projects - Medium, acessado em outubro 20,

### 2025,

### https://medium.com/@amirm.lavasani/how-to-structure-your-fastapi-projects-

### 219a6600a8f

### 3. FastAPI Best Practices and Conventions we used at our startup - GitHub,

### acessado em outubro 20, 2025,

### https://github.com/zhanymkanov/fastapi-best-practices

### 4. Bigger Applications - Multiple Files - FastAPI, acessado em outubro 20, 2025,

### https://fastapi.tiangolo.com/tutorial/bigger-applications/

### 5. First Steps - FastAPI, acessado em outubro 20, 2025,

### https://fastapi.tiangolo.com/tutorial/first-steps/

### 6. FastAPI - Rest Architecture - GeeksforGeeks, acessado em outubro 20, 2025,

### https://www.geeksforgeeks.org/python/fastapi-rest-architecture/

### 7. Structuring a FastAPI Project: Best Practices - DEV Community, acessado em

### outubro 20, 2025,

### https://dev.to/mohammad222pr/structuring-a-fastapi-project-best-practices-53l

### 8. The Ultimate Guide to Organizing Your Next.js 15 Project Structure - Wisp CMS,

### acessado em outubro 20, 2025,

### https://www.wisp.blog/blog/the-ultimate-guide-to-organizing-your-nextjs-15-pro

### ject-structure


