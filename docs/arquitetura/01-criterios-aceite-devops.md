# 1.0 Introdução e Propósito do Documento

## 1.1 Visão Geral

Este documento serve como a fonte de verdade ("source of truth") técnica para a equipe de
desenvolvimento do Sistema de Controle de Acesso Veicular. Ele detalha os Critérios de
Aceitação (ACs) para todas as tarefas contidas nos sete épicos do backlog do projeto. A
adesão a estes critérios é fundamental para estabelecer a "Definition of Done" para cada item
de trabalho, garantindo a entrega de um produto coeso, funcional e alinhado com a
arquitetura definida.

## 1.2 Objetivo

O propósito deste relatório é eliminar a ambiguidade no processo de desenvolvimento, alinhar
a equipe em relação aos entregáveis técnicos e garantir que a implementação final adira
estritamente à arquitetura e aos requisitos funcionais e não funcionais definidos nos
documentos do projeto.^1 Este guia visa capacitar a equipe a construir o sistema de forma
incremental e validada, minimizando o retrabalho e maximizando a qualidade.

## 1.3 Como Utilizar Este Documento

As equipes de DevOps, Back-end e Front-end devem utilizar este documento como referência
primária durante o planejamento de sprints, a execução das tarefas e os processos de Quality
Assurance (QA). Uma tarefa só deve ser considerada concluída quando todos os seus
Critérios de Aceitação forem atendidos, demonstrados e validados. Este documento deve ser
a base para a criação de casos de teste e para as revisões de código (code reviews).

## 1.4 Classificação de Áreas

Para clareza organizacional e para facilitar a atribuição de responsabilidades, as tarefas do
projeto são classificadas em três áreas de especialização principais. Esta classificação reflete
a arquitetura de repositórios separados e as distintas pilhas de tecnologia do projeto.^1

```
● DevOps: Abrange todas as tarefas relacionadas à infraestrutura como código,
automação de pipelines de integração e entrega contínua (CI/CD), containerização
(Docker), e a configuração do ambiente de desenvolvimento. Estas tarefas formam a
fundaçã sobre a qual as aplicações são construídas e operadas.
● Back-end: Inclui tarefas relacionadas à lógica de negócio no lado do servidor,
desenvolvimento de API RESTful, interação com o banco de dados, sistemas de
autenticação e segurança. Notavelmente, as tarefas do dispositivo IoT (script Python
para ALPR) também são classificadas nesta área, pois envolvem lógica de aplicação em
Python, processamento de dados e comunicação via HTTP, que são competências
centrais de um desenvolvedor back-end.
● Front-end: Engloba todas as tarefas relacionadas à interface do usuário (UI) e à
experiência do usuário (UX) do painel de administração. Isso inclui a construção de
componentes visuais, gerenciamento de estado do lado do cliente, consumo da API do
back-end e garantia de responsividade da aplicação web.
```
# 2.0 Detalhamento dos Épicos e Critérios de Aceitação

A estrutura dos épicos foi projetada para seguir um fluxo de desenvolvimento lógico e de
baixo risco. O projeto inicia com a construção da fundação de infraestrutura e automação,
uma decisão estratégica que estabelece padrões de qualidade e consistência desde o
primeiro dia. Esta abordagem é particularmente eficaz para uma equipe em aprendizado, pois
de-risca o processo de desenvolvimento, evitando problemas comuns de integração e
inconsistência de ambientes.^1 Somente após a solidificação desta base, o projeto avança para
a implementação da lógica de negócio central e, subsequentemente, para as interfaces de
usuário, garantindo que cada nova camada seja construída sobre uma fundação estável e
testada.

## 2.1 Épico 1: Fundação do Projeto & DevOps

**Objetivo do Épico:** Estabelecer a infraestrutura de código, o ambiente de desenvolvimento
local padronizado e os pipelines de integração contínua. Esta fase é crucial para criar uma
base técnica robusta que suportará todo o ciclo de vida do desenvolvimento subsequente.

```
ID da Tarefa Descrição da
Tarefa
```
```
Classificação da
Área
```
```
Critérios de
Aceitação
```
```
FND-01 Configurar
repositórios Git
separados para
backend (api) e
frontend (web).
```
```
DevOps Dado que a
arquitetura do
projeto define uma
separaçã clara
entre front-end e
back-end 1,
Quando a
organização do
projeto no GitHub
for inspecionada,
Então devem existir
dois repositórios
públicos e distintos:
siscav-api e
siscav-web.
Cada repositório
deve conter um
arquivo .gitignore
configurado
apropriadamente
para sua respectiva
stack tecnológica
(Python/FastAPI
para siscav-api e
Node.js/Next.js
para
siscav-web).Cada
repositório deve ter
uma estrutura de
branches
inicializada,
contendo, no
mínimo, as
branches main e
develop.O arquivo
README.md de
cada repositório
deve ser
inicializado com o
nome do projeto e
uma breve
descrição do seu
propósito (API de
backend ou painel
de administração).
```
**FND-02** Criar arquivo
Docker Compose
para
desenvolvimento
local (FastAPI,
Next.js,
PostgreSQL).

```
DevOps Dado que a
consistência do
ambiente de
desenvolvimento é
prioritária 1,
quando um
desenvolvedor
executar o
comando
docker-compose
up na raiz do
repositório
siscav-api, então
um container para
a API FastAPI e um
container para o
banco de dados
PostgreSQL devem
ser iniciados sem
erros.
A API FastAPI deve
estar acessível a
partir da máquina
host na porta de
desenvolvimento
especificada (e.g.,
localhost:8000).O
container da API
deve ser capaz de
estabelecer uma
conexão de rede
com o container do
banco de dados
PostgreSQL.Os
dados do
PostgreSQL devem
ser persistidos
utilizando um
volume Docker,
garantindo que os
dados não sejam
perdidos ao
reiniciar os
containers.As
variáveis de
ambiente para a
conexão com o
banco de dados
devem ser
gerenciadas de
forma segura (e.g.,
através de um
arquivo .env
referenciado no
docker-compose.y
ml).
```


**FND-03** Inicializar a
estrutura da
aplicação FastAPI e
dependências
(pyproject.toml).

```
Back-end Dado o repositório
siscav-api, Quando
a estrutura de
diretórios for
inspecionada,
Então ela deve
corresponder
exatamente à
arquitetura
orientada a
domínio definida na
documentação 1,
incluindo
src/api/v1/,
endpoints/, core/,
crud/, db/, models/
e schemas/.
O arquivo
pyproject.toml deve
ser criado e
populado com as
dependências
iniciais essenciais,
como fastapi,
uvicorn,
sqlalchemy,
pydantic e
alembic.A instância
principal da
aplicação FastAPI
deve ser criada no
arquivo
src/main.py.A
aplicação deve
iniciar sem erros ao
executar o
comando de
desenvolvimento
(e.g., uvicorn
src.main:app
--reload).
```

**FND-04** Inicializar a
estrutura da
aplicação Next.js e
dependências
(package.json).

```
Front-end Dado o repositório
siscav-web,
Quando a estrutura
de diretórios for
inspecionada,
Então ela deve
corresponder à
arquitetura
baseada no App
Router definida na
documentação 1,
incluindo src/app/,
(auth)/, (public)/,
components/, lib/ e
hooks/.
O arquivo
package.json deve
ser gerado (e.g., via
create-next-app) e
conter as
dependências
iniciais, incluindo
react, next,
typescript, e a
biblioteca de
componentes de UI
@mui/material com
suas dependências
associadas.As
ferramentas de
qualidade de
código, como
ESLint e Prettier,
devem estar
configuradas.A
aplicação Next.js
deve iniciar sem
erros ao executar o
comando npm run
dev.
```
**FND-05** Configurar Alembic **Back-end** Dado que o

para migrações de
banco de dados e
criar modelos de
esquema iniciais.

```
Alembic está
configurado no
repositório
siscav-api 1,
Quando os
modelos
SQLAlchemy
iniciais (User,
AuthorizedPlate,
AccessLog) forem
definidos na pasta
src/api/v1/models/,
Então o comando
alembic revision
--autogenerate -m
"Initial models"
deve gerar um
script de migração
sem erros.
O script de
migração gerado
deve conter as
instruções SQL
CREATE TABLE
para as três tabelas
iniciais.A execução
do comando
alembic upgrade
head deve aplicar a
migração com
sucesso ao banco
de dados
PostgreSQL em
execução via
Docker.Uma
inspeção direta no
banco de dados
deve confirmar que
as tabelas users,
authorized_plates e
access_logs foram
criadas com as
colunas corretas.
```
**FND-06** Implementar um
endpoint básico de
"verificação de
saúde" na API.

```
Back-end Dado que a API
FastAPI está em
execução, Quando
uma requisição
GET for enviada
para o endpoint
/api/v1/health,
Então a API deve
retornar uma
resposta com HTTP
status code 200
OK. O corpo da
resposta deve ser
um objeto JSON
contendo {"status":
"ok"}.Este endpoint
não deve exigir
nenhum tipo de
autenticação.O
endpoint deve ser
implementado
dentro da estrutura
de roteadores
definida (e.g., em
um arquivo
endpoints/health.p
y).
```
**FND-07** Implementar uma
página de
placeholder básica
na aplicação
Next.js.

```
Front-end Dado que a
aplicaçã Next.js
está em execução,
Quando um
navegador acessar
a rota raiz do
projeto (/), Então
uma página HTML
deve ser
renderizada sem
erros. A página
deve exibir um
título visível, como
<h1>Sistema de
Controle de Acesso
Veicular</h1>.Não
deve haver erros de
compilação ou de
execução no
console do
navegador.A página
deve ser criada
utilizando a
estrutura do App
Router (e.g.,
src/app/page.tsx).
```
**FND-08** Configurar
pipelines de CI
básicos no GitHub
Actions para os
repositórios de
backend e
frontend.

```
DevOps Dado que ambos
os repositórios
(siscav-api e
siscav-web)
possuem um
arquivo de
workflow em
.github/workflows/c
i.yml 1, Quando um
pull request for
aberto para a
branch develop em
qualquer um dos
repositórios, Então
o respectivo
pipeline do GitHub
Actions deve ser
acionado
automaticamente.
Para siscav-api: O
pipeline deve
executar com
sucesso as etapas
de linting (e.g., ruff
ou flake8) e testes
unitários (e.g.,
pytest).Para
siscav-web: O
pipeline deve
executar com
sucesso as etapas
de linting (eslint),
verificação de tipos
(tsc --noEmit) e
build do projeto
(npm run build).O
pipeline deve ser
configurado para
falhar (retornar um
status "vermelho")
se qualquer uma
das etapas acima
falhar, bloqueando
a mesclagem de
código de baixa
qualidade.
```
## 2.2 Épico 2: Implementação do Dispositivo IoT ALPR

**Objetivo do Épico:** Desenvolver o script Python que será executado no dispositivo de borda
(e.g., Raspberry Pi). Este componente é responsável pela captura da imagem do veículo,
processamento local para reconhecimento da placa (ALPR), comunicação com a API central e
acionamento do hardware do portão. A escolha da biblioteca easyocr é uma decisão técnica
estratégica, pois abstrai a alta complexidade dos modelos de Deep Learning, permitindo que
a equipe se concentre na lógica de orquestração do sistema, o que reduz significativamente o
risco técnico e o tempo de desenvolvimento.^1 Todas as tarefas deste épico, embora
executadas na borda, são classificadas como **Back-end** devido à sua natureza (lógica de
aplicação em Python).

```
ID da Tarefa Descrição da
Tarefa
```
```
Classificação da
Área
```
```
Critérios de
Aceitação
```
```
IOT-01 Escrever um script
para capturar uma
imagem de alta
resolução da
```
```
Back-end Dado um
dispositivo com
uma câmera
compatível
```

```
câmera. conectada, Quando
o script Python for
executado, Então
ele deve capturar
uma imagem
estática e salvá-la
no sistema de
arquivos local.
A imagem salva
deve estar em um
formato padrão
(e.g., JPEG ou PNG)
e ter resolução
suficiente para que
os caracteres da
placa sejam
legíveis, atendendo
ao requisito
RF-001.1O script
deve lidar com
possíveis erros de
inicialização ou
captura da câmera
de forma graciosa.
```
**IOT-02** Integrar a
biblioteca easyocr
para extrair texto
de uma imagem de
amostra capturada.

```
Back-end Dado uma imagem
de um veículo com
uma placa visível,
Quando o script
passar esta
imagem para a
biblioteca easyocr,
Então a biblioteca
deve retornar uma
lista de textos
detectados na
imagem.
O script deve ser
capaz de inicializar
o leitor easyocr
com os idiomas
apropriados (e.g.,
pt para
português).A string
correspondente à
placa do veículo
deve estar presente
nos resultados
retornados pela
biblioteca,
cumprindo o
requisito RF-003.
```
**IOT-03** Desenvolver uma
função para
pré-processar a
imagem para
melhorar a
precisão do OCR.

```
Back-end Dado uma imagem
colorida capturada
pela câmera,
Quando a função
de
pré-processamento
for aplicada, Então
ela deve retornar
uma imagem
modificada, pronta
para o OCR.
A função deve, no
mínimo, converter a
imagem para
escala de
cinza.Testes com
imagens de baixa
iluminação ou
contraste devem
demonstrar que a
aplicação de
técnicas como
equalização de
histograma ou
ajuste de contraste
antes do OCR
melhora a taxa de
reconhecimento de
caracteres, visando
atender aos
requisitos de
precisão RNF-002.
```
**IOT-04** Desenvolver uma
função para
formatar a string da
placa extraída.

```
Back-end Dado uma string de
placa bruta
retornada pelo
easyocr (e.g.,
"ABC-1234" ou
"XYZ 9876"),
Quando a função
de formatação for
aplicada, Então ela
deve retornar uma
string normalizada.
A string retornada
deve conter apenas
caracteres
alfanuméricos e
estar em
maiúsculas (e.g.,
"ABC1234",
"XYZ9876").A
função deve
remover hifens,
espaços e
quaisquer outros
caracteres
especiais,
conforme a lógica
de comparação
robusta exigida
pelo RF-004.
```
**IOT-05** Implementar
requisição POST
HTTPS segura para
enviar dados da
placa e imagem
para a API do
backend.

```
Back-end Dado que o script
obteve a string da
placa formatada e
a imagem original,
Quando a função
de comunicação
for chamada, Então
uma requisição
POST deve ser
enviada para o
endpoint
/api/v1/access_logs
do servidor
backend.
A comunicação
deve
obrigatoriamente
usar o protocolo
HTTPS para
garantir a
criptografia dos
dados, atendendo
ao RNF-005.1A
requisição deve ser
do tipo
multipart/form-dat
a, contendo o
campo plate_string
com a placa
formatada e o
arquivo da imagem
capturada.O script
deve incluir
tratamento de
erros para falhas
de rede ou
indisponibilidade
da API.
```
**IOT-06** Implementar lógica
para analisar a
resposta da API
(Autorizado/Negad
o).

```
Back-end Dado que o script
enviou uma
requisição para a
API e recebeu uma
resposta, Quando
a resposta for
processada, Então
o script deve extrair
o status da decisão
de acesso. O script
deve ser capaz de
decodificar o corpo
da resposta JSON
e ler o valor da
chave status.A
lógica deve
diferenciar
corretamente entre
as respostas
{"status":
"Authorized"} e
{"status":
"Denied"}.
```
**IOT-07** Escrever um script
para controlar um
pino GPIO para
acionar o módulo
de relé com base
na resposta da API.

```
Back-end Dado que a
resposta da API foi
{"status":
"Authorized"},
Quando a lógica de
controle de
hardware for
executada, Então
um sinal elétrico
deve ser enviado
para um pino GPIO
específico do
dispositivo.
O sinal deve ser
mantido por um
curto período (e.g.,
1 segundo) e
depois desativado
para simular o
pressionar de um
botão.Se a
resposta da API for
{"status":
"Denied"}, nenhum
sinal deve ser
enviado ao pino
GPIO.Esta
funcionalidade
deve cumprir o
requisito de
acionamento do
portão RF-005.
```
## 2.3 Épico 3: Controle de Acesso Central & Logging (Backend)

**Objetivo do Épico:** Construir os endpoints da API e a lógica de negócios no servidor central.
Este é o "cérebro" do sistema, responsável por receber as solicitações do dispositivo IoT,
validar as placas de veículos contra a lista de autorizados e registrar de forma persistente
todas as tentativas de acesso para fins de auditoria.

```
ID da Tarefa Descrição da
Tarefa
```
```
Classificação da
Área
```
```
Critérios de
Aceitação
```
```
API-01 Criar o endpoint da
API access_logs
para receber dados
da placa e um
arquivo de imagem
do dispositivo IoT.
```
```
Back-end Dado que a API
está em execução,
Quando uma
requisição POST do
tipo
multipart/form-dat
a é feita para
/api/v1/access_logs,
Então a API deve
ser capaz de
receber e
processar a
requisição. O
endpoint deve
esperar um campo
de formulário
chamado
plate_string e um
arquivo chamado
image.O endpoint
deve retornar um
HTTP status code
200 OK em caso de
processamento
bem-sucedido.Dev
e haver validação
(usando Pydantic
Schemas) para
garantir que os
dados esperados
estão presentes na
requisição.
```
**API-02** Implementar a
lógica de negócios
para consultar a
tabela
authorized_plates
por uma
correspondência.

```
Back-end Dado que o
endpoint
access_logs
recebeu uma
plate_string,
Quando a lógica de
verificação for
executada, Então
uma consulta deve
ser feita ao banco
de dados na tabela
authorized_plates.
A consulta deve ser
"case-insensitive" e
ignorar caracteres
especiais,
conforme
RF-004.1Cenário 1:
Se uma placa
correspondente for
encontrada, a
lógica deve
retornar um
resultado positivo
(e.g., True).Cenário
2: Se nenhuma
placa
correspondente for
encontrada, a
lógica deve
retornar um
resultado negativo
(e.g., False).
```
**API-03** Implementar lógica
para armazenar a
```
Back-end Dado que a
requisição para
```

```
imagem capturada. access_logs
contém um arquivo
de imagem,
Quando a
requisição for
processada, Então
o arquivo de
imagem deve ser
salvo de forma
persistente.
A imagem deve ser
salva com um nome
de arquivo único
para evitar colisões
(e.g., usando um
UUID ou
timestamp).O
caminho ou URL
para a imagem
salva deve ser
armazenado para
ser associado ao
registro de log de
acesso, cumprindo
parte do RF-006.1A
implementação
pode usar o
sistema de arquivos
local (para
simplicidade) ou
um serviço de
object storage
(como MinIO ou S3,
para
escalabilidade).
```
**API-04** Criar o modelo
AccessLog e
funções CRUD para
salvar cada
tentativa de acesso
no banco de dados.

```
Back-end Dado qualquer
requisição
processada pelo
endpoint
access_logs,
Quando a
verificação da
placa for concluída,
Então um novo
registro deve ser
criado na tabela
access_log.
A função CRUD
create_access_log
deve ser
implementada.O
registro salvo deve
conter, no mínimo:
a string da placa
recebida, o
timestamp exato do
evento, o resultado
da verificação
("Authorized" ou
"Denied") e a
referência para a
imagem
armazenada,
conforme RF-006.
```
**API-05** Implementar a
lógica de resposta
da API.

```
Back-end Dado que a lógica
de verificação da
placa foi
executada,
Quando o endpoint
access_logs for
retornar uma
resposta ao
dispositivo IoT,
Então o corpo da
resposta JSON
deve refletir o
resultado. Se a
placa foi
encontrada na lista
de autorizados, a
resposta deve ser
{"status":
"Authorized"}.Se a
placa não foi
encontrada, a
resposta deve ser
{"status":
"Denied"}.
```
**API-06** Criar o endpoint da
API gate_control
para acionamento
manual remoto.

```
Back-end Dado que um
administrador
precisa abrir o
portão
remotamente,
Quando uma
requisição POST for
feita para
/api/v1/gate_control
/trigger, Então a API
deve processar a
solicitação.
O endpoint deve
retornar um HTTP
status code 200
OK para indicar que
o comando foi
recebido.Este
endpoint deve ser
protegido e só
pode ser acessado
por usuários
autenticados (ver
Épico 4).Esta
funcionalidade é
um pré-requisito
para o requisito
RF-010.
```
**API-07** Escrever testes
unitários para a
lógica de
verificação de
placas.

```
Back-end Dado a suíte de
testes do
back-end, Quando
o comando pytest
for executado,
Então devem
existir testes
específicos para a
função de
verificação de
placas. Deve haver
um teste para um
caso de sucesso
(placa
autorizada).Deve
haver um teste para
um caso de falha
(placa não
autorizada).Deve
haver testes que
verifiquem se a
lógica de
correspondência
ignora
corretamente
diferenças de
maiúsculas/minúsc
ulas e hifens (e.g.,
"abc-1234" deve
corresponder a
"ABC1234").Todos
os testes devem
passar com 100%
de sucesso no
pipeline de CI.
```
## 2.4 Épico 4: Autenticação de Administrador

**Objetivo do Épico:** Implementar um sistema de login seguro e full-stack para o painel de
administração, protegendo o acesso a todas as funcionalidades de gerenciamento. A
arquitetura de autenticação baseada em JSON Web Tokens (JWT) cria um back-end
_stateless_ , o que simplifica o servidor e melhora sua escalabilidade. Consequentemente, a
responsabilidade pelo gerenciamento do ciclo de vida do token é transferida para o
front-end, que deve armazená-lo de forma segura (e.g., em um cookie httpOnly para mitigar
ataques XSS), anexá-lo às requisições subsequentes e gerenciar o estado de autenticação na
UI. Esta é uma troca de complexidade deliberada que favorece um design de back-end mais
limpo e moderno.^1

```
ID da Tarefa Descrição da
Tarefa
```
```
Classificação da
Área
```
```
Critérios de
Aceitação
```
```
AUTH-01 (BE) Criar modelo User
e funções CRUD,
incluindo hashing
seguro de senha.
```
```
Back-end Dado o modelo
User definido em
SQLAlchemy,
Quando uma
função para criar
um novo usuário for
chamada com uma
senha em texto
plano, Então a
senha deve ser
armazenada no
banco de dados
como um hash
seguro.
O modelo User
deve conter, no
mínimo, campos
para email (ou
username) e
hashed_password.
Uma biblioteca
robusta de hashing
(e.g., passlib) deve
ser utilizada para
criar o hash da
senha.Em nenhuma
circunstância a
senha em texto
plano deve ser
armazenada no
banco de dados,
atendendo às
melhores práticas
de segurança
implícitas no
RNF-006.1
```

**AUTH-02 (BE)** Implementar um
endpoint /login que
valida credenciais e
retorna um token
JWT.

```
Back-end Dado que um
usuário existe no
banco de dados,
Quando uma
requisição POST é
feita para
/api/v1/auth/login
com as credenciais
corretas (email e
senha), Então a API
deve retornar um
token JWT. O
endpoint deve
verificar a senha
fornecida
comparando seu
hash com o hash
armazenado.Em
caso de sucesso,
deve gerar um
token JWT
contendo
informações do
usuário (e.g., sub
com o ID do
usuário) e um
tempo de
expiração.A
resposta deve ser
um JSON no
formato
{"access_token":
"...", "token_type":
"bearer"} e um
HTTP status code
200 OK.Se as
credenciais forem
inválidas, deve
retornar um HTTP
401 Unauthorized.
```
**AUTH-03 (BE)** Implementar
dependência
FastAPI para
proteger endpoints,
exigindo um JWT
válido.

```
Back-end Dado um endpoint
que requer
autenticação (e.g.,
GET
/api/v1/whitelist),
Quando uma
requisição é feita
sem um token JWT
válido no
cabeçalho
Authorization,
Então a API deve
retornar um HTTP
401 Unauthorized.
Uma dependência
reutilizável do
FastAPI deve ser
criada para extrair
o token do
cabeçalho,
decodificá-lo e
validar sua
assinatura e
expiração.Se o
token for válido, a
dependência deve
retornar os dados
do usuário atual,
que podem ser
usados no
endpoint.Todos os
endpoints de
gerenciamento
(CRUDs, logs, etc.)
devem ser
protegidos com
esta dependência.
```
**AUTH-04 (FE)** Construir a página
de Login e a UI do
formulário na
aplicação Next.js.

```
Front-end Dado que o usuário
não está
autenticado,
Quando ele acessa
a aplicação, Então
a página de login
em
(public)/login/page.
tsx deve ser
exibida.
A página deve
conter um
formulário com
campos de entrada
para "Email" e
"Senha" (tipo
password) e um
botão "Entrar".A UI
deve ser construída
com componentes
da biblioteca MUI e
ser responsiva,
conforme
RNF-007.1Deve
haver feedback
visual para o
usuário em caso de
erro de login (e.g.,
"Credenciais
inválidas").
```
**AUTH-05 (FE)** Implementar lógica
no api-client para
chamar o endpoint
/login e armazenar
o JWT de forma
segura.

```
Front-end Dado que o usuário
preencheu o
formulário de login
e clicou em
"Entrar", Quando o
formulário for
submetido, Então
uma chamada
POST deve ser feita
para o endpoint
/api/v1/auth/login.
Em caso de
sucesso na
resposta da API, o
access_token JWT
recebido deve ser
armazenado no
cliente. A estratégia
de armazenamento
deve priorizar a
segurança (e.g., em
memória com um
refresh token em
cookie httpOnly, ou
localStorage para
este escopo de
projeto).Após o
armazenamento do
token, o usuário
deve ser
redirecionado
programaticamente
para a página do
dashboard.
```
**AUTH-06 (FE)** Implementar um
layout protegido
((auth)/layout.tsx)
que verifica o
estado de
autenticação do
usuário.

```
Front-end Dado que um
usuário tenta
acessar uma rota
protegida (e.g.,
/dashboard),
Quando a página é
carregada, Então o
layout protegido
deve verificar a
existência de um
token de
autenticação
válido. Se um token
válido existir, a
página solicitada
deve ser
renderizada
normalmente.Se
não houver token
ou se ele for
inválido/expirado, o
usuário deve ser
redirecionado
automaticamente
para a página
/login.Esta lógica
pode ser
implementada em
um hook
personalizado (e.g.,
use-auth.ts) para
ser reutilizada.
```
#### AUTH-07

**(Full-Stack)**

```
Implementar um
botão "Sair" que
limpa a sessão do
usuário.
```
```
Back-end &
Front-end
```
```
Dado que um
usuário está logado
no painel de
administração,
Quando ele clica
no botão "Sair",
Então sua sessão
deve ser encerrada.
Front-end: O
botão "Sair" deve
estar visível em
todas as páginas
do layout
autenticado. Front-
end: Ao ser
clicado, o token
JWT armazenado
no cliente (e.g.,
localStorage) deve
ser
removido. Front-en
d: Após a remoção
do token, o usuário
deve ser
redirecionado para
a página
/login. Back-end
(Opcional): Para
maior segurança,
pode-se
implementar um
endpoint /logout
que adicione o
token a uma
"blocklist" até sua
expiração,
prevenindo o reuso
de um token
vazado.
```
## 2.5 Épico 5: Painel de Gerenciamento da Whitelist

**Objetivo do Épico:** Construir a interface CRUD (Criar, Ler, Atualizar, Deletar) completa,
permitindo que os administradores gerenciem de forma eficiente e intuitiva a lista de placas
de veículos autorizadas, cumprindo integralmente o requisito RF-008.^1

```
ID da Tarefa Descrição da
Tarefa
```
```
Classificação da
Área
```
```
Critérios de
Aceitação
```
```
WHT-01 (BE) Criar o modelo
AuthorizedPlate e o
conjunto completo
de endpoints CRUD
para ele.
```
```
Back-end Dado que a API
está em execução,
Quando
requisições forem
feitas aos
endpoints da
whitelist, Então as
operações CRUD
correspondentes
devem ser
executadas no
banco de dados.
Devem existir os
seguintes
endpoints
protegidos por
autenticação: GET
/api/v1/whitelist,
POST
/api/v1/whitelist,
PUT
/api/v1/whitelist/{pla
te_id}, DELETE
/api/v1/whitelist/{pla
te_id}.Cada
endpoint deve
interagir com sua
respectiva função
CRUD (get_plates,
create_plate, etc.)
para manipular os
dados na tabela
authorized_plates.A
validação de dados
de entrada (usando
Pydantic Schemas)
deve ser
implementada para
os endpoints POST
e PUT.
```
**WHT-02 (FE)** Projetar e construir
a UI para a página
da Whitelist,
incluindo uma
tabela de dados.

```
Front-end Dado que o usuário
acessa a rota
/whitelist estando
autenticado, Então
a página de
gerenciamento da
whitelist deve ser
renderizada. A UI
deve conter um
componente de
tabela de dados
(e.g., MUI DataGrid)
para exibir a lista
de placas.As
colunas da tabela
devem incluir, no
mínimo, a placa e
campos de ações
(Editar, Deletar).Um
botão proeminente
"Adicionar Nova
Placa" deve estar
presente na página.
```
**WHT-03 (FE)** Implementar a
funcionalidade
"Ler": buscar e
exibir todas as
placas autorizadas
na tabela de dados.

```
Front-end Dado que a página
da whitelist é
carregada,
Quando o
componente é
montado, Então
uma chamada GET
deve ser feita para
o endpoint
/api/v1/whitelist. Os
dados retornados
pela API (uma lista
de placas) devem
ser populados nas
linhas da tabela de
dados.Um
indicador de
carregamento
(loading spinner)
deve ser exibido
enquanto os dados
estão sendo
buscados.Em caso
de erro na
chamada da API,
uma mensagem de
erro amigável deve
ser exibida.
```
**WHT-04 (FE)** Implementar a
funcionalidade
"Criar": um
modal/formulário
para adicionar uma
nova placa à lista.

```
Front-end Dado que o usuário
clica no botão
"Adicionar Nova
Placa", Quando a
ação é executada,
Então um modal ou
um formulário deve
ser exibido. O
formulário deve
conter um campo
de entrada para a
nova placa e um
botão "Salvar".Ao
submeter o
formulário, uma
chamada POST
deve ser feita para
/api/v1/whitelist
com os dados da
nova placa.Após o
sucesso da
requisição, o modal
deve ser fechado e
a tabela de dados
deve ser atualizada
para exibir a nova
placa adicionada.
```
**WHT-05 (FE)** Implementar a
funcionalidade
"Atualizar": um
botão "Editar" em
cada linha para
modificar os
detalhes de uma
placa.

```
Front-end Dado que a tabela
de placas está
populada, Quando
o usuário clica no
botão "Editar" de
uma linha
específica, Então
um modal ou
formulário de
ediçã deve ser
exibido. O
formulário deve vir
pré-preenchido
com os dados da
placa
selecionada.Ao
submeter o
formulário, uma
chamada PUT deve
ser feita para
/api/v1/whitelist/{pla
te_id} com os
dados
atualizados.Após o
sucesso da
requisição, o modal
deve ser fechado e
a linha
correspondente na
tabela deve ser
atualizada com os
novos dados.
```
**WHT-06 (FE)** Implementar a
funcionalidade
"Deletar": um botão
"Deletar" com um
diálogo de
confirmação para
remover uma placa.

```
Front-end Dado que a tabela
de placas está
populada, Quando
o usuário clica no
botão "Deletar" de
uma linha
específica, Então
um diálogo de
confirmação (e.g.,
"Você tem certeza
que deseja remover
esta placa?") deve
ser exibido. Se o
usuário confirmar a
exclusão, uma
chamada DELETE
deve ser feita para
/api/v1/whitelist/{pla
te_id}.Após o
sucesso da
requisição, a linha
correspondente
deve ser removida
da tabela na UI.Se
o usuário cancelar,
nenhuma ação
deve ser
executada.
```
#### WHT-07

**(Full-Stack)**

```
Adicionar
funcionalidade de
busca e paginação
à tabela da
whitelist.
```
```
Back-end &
Front-end
```
```
Dado que a lista de
placas autorizadas
é grande, Quando
o usuário interage
com a página da
whitelist, Então ele
deve poder buscar
e paginar os
resultados.
Back-end: O
endpoint GET
/api/v1/whitelist
deve ser
modificado para
aceitar parâmetros
de consulta (query
parameters) como
?search=ABC,
?page=2 e
?limit=10. A lógica
de banco de dados
deve filtrar e
paginar os
resultados de
acordo. Front-end:
A UI da tabela de
dados deve incluir
um campo de texto
para busca e
controles de
paginação (e.g.,
botões "Próximo",
"Anterior"). Front-e
nd: Digitar no
campo de busca ou
clicar nos controles
de paginação deve
acionar uma nova
chamada à API com
os parâmetros
corretos e atualizar
a tabela com os
novos dados
retornados.
```
## 2.6 Épico 6: Painel de Visualização de Logs de Acesso

**Objetivo do Épico:** Construir a interface que permite aos administradores revisar o histórico
completo de tentativas de acesso. A funcionalidade deve incluir a capacidade de visualizar,
filtrar e pesquisar os logs, fornecendo uma trilha de auditoria robusta e de fácil consulta,
conforme especificado no requisito RF-009.^1

```
ID da Tarefa Descrição da
Tarefa
```
```
Classificação da
Área
```
```
Critérios de
Aceitação
```
```
LOG-01 (BE) Criar o endpoint da
API para listar logs
de acesso com
suporte para
paginação e
filtragem.
```
```
Back-end Dado que a API
está em execução,
Quando uma
requisição GET é
feita para
/api/v1/access-logs,
Então uma lista
paginada de logs
de acesso deve ser
retornada. O
endpoint deve
suportar
parâmetros de
consulta para
filtragem por: plate
(busca parcial),
start_date,
end_date e status
("Authorized" ou
"Denied").O
endpoint deve
suportar
parâmetros de
consulta para
paginação: page e
limit.A lógica de
banco de dados
deve construir uma
query SQL
dinâmica para
aplicar os filtros e a
paginação de
forma eficiente.
```
**LOG-02 (FE)** Projetar e construir
a UI para a página
de Logs de Acesso,
incluindo uma
tabela de dados e
controles de filtro.

```
Front-end Dado que o usuário
acessa a rota /logs
estando
autenticado, Então
a página de
visualização de
logs deve ser
renderizada. A UI
deve conter uma
seção de filtros
com: seletores de
intervalo de datas
(date pickers), um
campo de texto
para busca de
placa e um
dropdown para
selecionar o
status.Abaixo dos
filtros, uma tabela
de dados deve
exibir os logs, com
colunas para Placa,
Data/Hora, Status e
Imagem.
```
**LOG-03 (FE)** Implementar a
funcionalidade
"Ler": buscar e
exibir logs na
tabela.

```
Front-end Dado que a página
de logs é
carregada,
Quando o
componente é
montado, Então
uma chamada GET
inicial deve ser feita
para
/api/v1/access-logs
para buscar a
primeira página de
logs. Os resultados
retornados pela API
devem ser
renderizados nas
linhas da tabela de
dados.Um
indicador de
carregamento deve
ser exibido durante
a busca dos
dados.Controles de
paginação devem
estar presentes e
funcionais.
```
**LOG-04 (FE)** Implementar os
controles de filtro.

```
Front-end Dado que o usuário
interage com os
controles de filtro,
Quando o valor de
um filtro é alterado
(e.g., uma data é
selecionada ou
uma placa é
digitada), Então
uma nova chamada
GET deve ser feita
para
/api/v1/access-logs
com os novos
parâmetros de
consulta. A tabela
de dados deve ser
atualizada para
exibir os resultados
filtrados retornados
pela API.A lógica de
"debouncing" pode
ser aplicada ao
campo de busca de
placa para evitar
chamadas
excessivas à API
enquanto o usuário
digita.
```
**LOG-05 (FE)** Implementar a
lógica para exibir a
imagem do veículo
capturada.

```
Front-end Dado que a tabela
de logs está sendo
exibida, Quando o
usuário clica em um
ícone ou link na
coluna "Imagem"
de uma linha de
log, Então um
modal deve ser
aberto exibindo a
imagem capturada
para aquele evento
específico. A
imagem deve ser
buscada do
endpoint seguro de
imagens
(LOG-06).O modal
deve permitir que o
usuário feche a
visualização da
imagem.
```
**LOG-06 (BE)** Garantir que o
endpoint da API
que serve imagens
seja seguro e
acessível apenas
para
administradores
autenticados.

```
Back-end Dado que o
front-end solicita
uma imagem de
log, Quando uma
requisição GET é
feita para um
endpoint de
imagem (e.g.,
/api/v1/access-logs/
images/{image_file
name}), Então a
API deve validar a
autenticação do
usuário antes de
servir o arquivo. O
endpoint deve usar
a mesma
dependência de
autenticação JWT
(AUTH-03) para
proteger o
acesso.Se o
usuário não estiver
autenticado, a API
deve retornar HTTP
401
Unauthorized.Se
autenticado, a API
deve retornar o
arquivo de imagem
com o
Content-Type
apropriado (e.g.,
image/jpeg).
```
#### LOG-07

**(Full-Stack)**

```
Implementar o
botão de
acionamento
remoto do portão
no painel.
```
```
Back-end &
Front-end
```
```
Dado que um
administrador
precisa abrir o
portão
manualmente,
Quando ele clica
no botão "Acionar
Portão
Remotamente" no
painel, Então o
comando deve ser
enviado.
Front-end: Um
botão para
acionamento
remoto deve estar
disponível em uma
localização
apropriada no
dashboard (e.g., na
página de logs ou
em um cabeçalho
global). Front-end:
Clicar no botão
deve acionar uma
chamada POST
para o endpoint
/api/v1/gate_control
/trigger. Front-end:
Um feedback visual
(e.g., uma
notificação "toast")
deve informar ao
administrador que
o comando foi
enviado com
sucesso. Back-end:
O endpoint
(API-06) deve estar
funcional e
protegido por
autenticação.
```
## 2.7 Épico 7: Reforço e Polimento do Sistema

**Objetivo do Épico:** Abordar requisitos não funcionais (RNFs) e preparar o sistema para uma
implantaçã robusta e segura. Esta fase demonstra a maturidade do processo de
planejamento, alocando tempo explicitamente para atividades cruciais que transformam um
protótipo funcional em um sistema de qualidade de produção. Tarefas como documentação
da API, segurança, usabilidade, confiabilidade e testes de desempenho são tratadas como
entregáveis de primeira classe, garantindo que o produto final seja seguro, confiável e
manutenível.^1

```
ID da Tarefa Descrição da
Tarefa
```
```
Classificação da
Área
```
```
Critérios de
Aceitação
```
```
HRD-01 (BE) Gerar e refinar a
documentação
automática
Swagger/OpenAPI
para a API.
```
```
Back-end Dado que a API
FastAPI está em
execução, Quando
um desenvolvedor
acessa a rota /docs
no navegador,
Então uma
interface interativa
do Swagger UI
deve ser exibida.
Todos os endpoints
implementados
devem estar
listados na
documentação.Cad
a endpoint deve ter
um sumário, uma
descrição clara, e
schemas Pydantic
definidos para os
corpos de
requisição e
resposta.A
documentação
deve ser detalhada
o suficiente para
que um
desenvolvedor
front-end ou de IoT
possa entender
como interagir com
a API sem precisar
ler o código-fonte.
```
**HRD-02 (BE)** Implementar
limitação de taxa
(rate limiting) no
endpoint de login
para prevenir
ataques de força
bruta.

```
Back-end Dado que um
atacante tenta um
ataque de força
bruta no endpoint
de login, Quando
múltiplas tentativas
de login falhas são
feitas a partir do
mesmo endereço IP
em um curto
período, Então o
acesso deve ser
temporariamente
bloqueado.
O endpoint POST
/api/v1/auth/login
deve ser
configurado para
permitir um número
limitado de
tentativas por
minuto (e.g., 5
tentativas).Após
exceder o limite,
requisições
subsequentes do
mesmo IP devem
receber uma
resposta HTTP 429
Too Many Requests
por um período de
tempo
definido.Esta
medida atende
diretamente a uma
das melhores
práticas de
segurança do
RNF-006.1
```
**HRD-03 (FE)** Garantir que a UI
do painel seja
totalmente
responsiva e
intuitiva.

```
Front-end Dado que o painel
de administração é
acessado de
diferentes
dispositivos,
Quando a
aplicação é
visualizada em
telas de desktop,
tablet e mobile,
Então o layout e os
componentes
devem se adaptar
para fornecer uma
experiência de
usuário funcional e
agradável.
Todos os
elementos de UI,
incluindo tabelas,
formulários e
botões, devem ser
utilizáveis em telas
pequenas.Não deve
haver quebra de
layout ou conteúdo
sobreposto.A
navegação deve
permanecer
intuitiva em todos
os tamanhos de
tela, cumprindo o
RNF-007.1
```
**HRD-04 (IoT/BE)** Implementar um
watchdog ou
serviço systemd no
Raspberry Pi para
garantir que o
script ALPR reinicie
automaticamente
em caso de falha.

```
Back-end Dado que o script
Python ALPR no
dispositivo IoT falha
inesperadamente
(e.g., devido a um
erro não tratado),
Quando o processo
termina, Então ele
deve ser reiniciado
automaticamente
sem intervenção
manual.
Um arquivo de
serviço systemd
deve ser criado
para gerenciar o
script Python.A
configuração do
serviço deve incluir
a diretiva
Restart=on-failure
ou
Restart=always.Isso
garante a alta
disponibilidade do
endpoint, conforme
exigido pelo
RNF-003.1
```
**HRD-05 (DevOps)** Criar Dockerfiles
prontos para
produção para as
aplicaçõs api e
web.

```
DevOps Dado que o projeto
precisa ser
implantado em um
ambiente de
produção, Quando
as imagens Docker
forem construídas,
Então elas devem
ser otimizadas para
segurança e
tamanho. Para
siscav-api: O
Dockerfile deve
usar "multi-stage
builds" para
separar o ambiente
de build do
ambiente de
execução,
resultando em uma
imagem final menor
contendo apenas
as dependências
de produção. Para
siscav-web: O
Dockerfile deve
construir a
aplicação Next.js
(npm run build) e
usar um servidor
web leve (como
Nginx ou o servidor
Node.js integrado
do Next.js) para
servir os arquivos
estáticos de
produção.
```
**HRD-06 (Docs)** Escrever os
arquivos
README.md para
cada aplicação,
explicando os
procedimentos de
configuração e
desenvolvimento.

```
DevOps Dado que um novo
desenvolvedor se
junta ao projeto,
Quando ele clona
um dos
repositórios, Então
o arquivo
README.md deve
fornecer todas as
instruções
necessárias para
configurar e
executar o projeto
localmente.
O README.md do
siscav-api deve
detalhar como
configurar o .env,
construir a imagem
Docker e iniciar os
serviços com
docker-compose.O
README.md do
siscav-web deve
detalhar como
instalar as
dependências
(npm install) e
iniciar o servidor de
desenvolvimento
(npm run dev).Esta
documentação é
crucial para a
manutenibilidade
do projeto,
conforme
RNF-008.1
```
**HRD-07 (QA)** Realizar testes de
ponta a ponta de
todo o fluxo e
medir em relação
ao requisito de
latência de 5
segundos.

```
DevOps Dado um ambiente
de teste que simula
o sistema
completo, Quando
um veículo com
uma placa
autorizada é
apresentado à
câmera, Então o
tempo total desde
a captura da
imagem até o
acionamento do
relé deve ser
medido.
Um cenário de
teste de ponta a
ponta (E2E) deve
ser executado
múltiplas vezes
(e.g., 10 vezes)
para obter uma
medição
consistente.A
média dos tempos
medidos não deve
exceder 5
segundos,
validando o
cumprimento do
requisito de
desempenho
crítico RNF-001.1O
teste deve ser
documentado com
os resultados
obtidos.
```

### Referências citadas

### 1. Arquitetura e Backlog de Projeto Acadêmico.pdf

