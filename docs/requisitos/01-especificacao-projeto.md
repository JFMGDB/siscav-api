**Informações gerais
Nome do projeto**
Sistema de Controle de Acesso de Veículos
**Integrantes
Nome Função**
Anderson Marinho Gerente de projeto; Dev. fullstack.
José Barros Tech Leader; Dev. fullstack.
Jamilli Maria Scrum Master; Dev. fullstack.
Ênio Bezerra Dev. fullstack.
**Patrocinador
Empresa** Solucoes Eletronicas Eletronica do Futuro
LTDA 27.117.678/0001-
**Responsável** Orisvaldo Pereira
**Contato** 81 9-9692-
**Expectativas**
Atender as necessidades de gestão privada do cliente demandante que é da
categoria corporativo e é pioneiro na gestão hospitalar de hospitais públicos.


## 1 VISÃO GERAL E JUSTIFICATIVA DO PROJETO

**1.1 Introdução ao Problema**
Atualmente, o controle de acesso veicular nas instalações do cliente é realizado
por meio de métodos manuais ou semi-automatizados que apresentam ineficiências
operacionais e vulnerabilidades de segurança significativas. Os processos existentes,
que podem depender de guardas de segurança para verificação visual, uso de
controles remotos físicos ou chamadas telefônicas para autorizar a entrada, são
propensos a erros humanos, causam atrasos no fluxo de tráfego e carecem de um
sistema de registro auditável. A perda, roubo ou clonagem de controles remotos
representa um risco de segurança substancial, enquanto a ausência de um log digital
de acessos impede a análise de incidentes e a otimização de operações. Este cenário
cria um ambiente onde a segurança é reativa em vez de proativa e a gestão de acesso
é um gargalo operacional.
**1.2 Proposta de Solução**
Para endereçar os desafios descritos, propõe-se o desenvolvimento e a
implementação do sistema de controle de acesso veicular automatizado como uma
solução integrada que combina tecnologias de Internet das Coisas (IoT) e Inteligência
Artificial (IA) para modernizar e automatizar completamente o processo de controle de
acesso. A arquitetura da solução consiste em um endpoint inteligente, baseado em um
microcomputador e uma câmera de alta resolução, instalado em cada ponto de acesso.
Este dispositivo será responsável por capturar imagens de veículos, executar um
algoritmo de reconhecimento automático de placas de veículos para extrair os
caracteres da placa e, em seguida, comunicar-se de forma segura com um servidor
central. O servidor central hospedará a lógica de negócios, incluindo a gestão de uma
lista de placas de veículos previamente autorizadas. Ao receber a identificação de uma
placa do endpoint, o servidor a validará contra a lista. Se a placa for reconhecida como
autorizada, o servidor enviará um comando de volta, que por sua vez acionará o


mecanismo de portão existente através de um módulo relé.^
**1.3 Objetivos de Negócio**
A implementação do sistema visa traduzir os benefícios tecnológicos em valor de
negócio tangível para o cliente, alinhado com quatro pilares estratégicos:
● **Aumento da Segurança:** O sistema eleva o nível de segurança ao substituir
métodos de autenticação vulneráveis (como controles remotos) por uma
verificação baseada na identidade única do veículo (sua placa). Cada tentativa de
acesso, bem-sucedida ou não, é registrada com data, hora, placa e a imagem
capturada, criando uma trilha de auditoria digital robusta e inviolável. Isso permite
uma análise forense precisa de incidentes e inibe o acesso não autorizado.
● **Eficiência Operacional:** A automação completa do processo de verificação e
abertura do portão elimina a necessidade de alocação de pessoal para essa tarefa,
reduzindo custos operacionais. Além disso, o sistema agiliza o fluxo de tráfego,
minimizando filas e tempos de espera para veículos autorizados, o que resulta em
uma operação mais fluida e eficiente.
● **Conveniência e Experiência do Usuário:** Para usuários autorizados, o sistema
oferece uma experiência de acesso fluida e sem interrupções. Não há mais a
necessidade de procurar controles remotos, fazer chamadas ou esperar por um
guarda, o que aumenta a satisfação e a conveniência para funcionários, residentes
ou visitantes frequentes.
● **Modernização e Geração de Dados Estratégicos:** A adoção do sistema
posiciona a infraestrutura do cliente como moderna e tecnologicamente avançada.
Mais do que um sistema de automação, o sistema é um ativo gerador de dados.
Os logs de acesso, quando agregados ao longo do tempo, transformam-se em um
valioso conjunto de dados sobre os padrões de fluxo de veículos. A análise desses
dados pode revelar informações estratégicas, como horários de pico, frequência de
visitas por veículo e duração de permanência, permitindo otimizações operacionais
futuras que vão além do simples controle de acesso. Este projeto, portanto, não


apenas resolve um problema imediato, mas também cria uma plataforma para
futuras iniciativas de business intelligence.
**2 REQUISITOS FUNCIONAIS DO SISTEMA**
Esta seção detalha as funcionalidades específicas que o sistema deve executar.
Cada requisito é identificado por um código único para garantir a rastreabilidade ao
longo do ciclo de vida do projeto.
**2.1 Módulo de Reconhecimento de Placas (ALPR)**
● **RF-001: Captura de Imagem:** O sistema, através da câmera conectada ao
endpoint no portão, deve ser capaz de capturar imagens estáticas de alta
resolução ou quadros de um fluxo de vídeo contínuo de veículos que se
aproximam e param na área de detecção designada.
● **RF-002: Detecção e Localização da Placa:** O software embarcado no endpoint
deve processar a imagem capturada para aplicar algoritmos de visão
computacional que detectem e isolem a região retangular correspondente à placa
do veículo. A precisão nesta etapa é fundamental, pois um erro na localização da
placa compromete todo o fluxo subsequente.^
● **RF-003: Extração de Caracteres (OCR):** Após a localização da placa, o sistema
deve aplicar uma técnica de Reconhecimento Óptico de Caracteres (OCR)
otimizada para a tarefa. Esta função converterá os caracteres alfanuméricos
presentes na imagem da placa em uma string de texto digital. O sistema deve ser
projetado para ter resiliência a variações comuns, como diferentes condições de
iluminação, ângulos de câmera e pequenos danos ou sujeira na placa.^
**2.2 Módulo de Controle de Acesso**
● **RF-004: Verificação na lista de acesso:** A string de texto da placa, extraída pelo
RF-003, deve ser enviada ao servidor central para ser comparada com a base de
dados de placas autorizadas. A lógica de comparação deve ser robusta, ignorando
diferenças de maiúsculas/minúsculas e caracteres especiais (como hifens ou
espaços) para maximizar a taxa de correspondência correta.
● **RF-005: Acionamento do Portão:** Caso a verificação no RF-004 resulte em uma
correspondência positiva (a placa está na lista de acesso), o sistema no endpoint
deve enviar um sinal elétrico de baixa tensão para o módulo relé. O relé, por sua
vez, fechará momentaneamente o circuito conectado aos terminais de
acionamento manual do motor do portão, simulando o pressionar de um botão e
iniciando o ciclo de abertura.^
● **RF-006: Registro de Eventos (Log):** O sistema deve registrar de forma
persistente no banco de dados central cada tentativa de acesso. Cada registro de
evento deve conter, no mínimo, os seguintes dados: a string da placa detectada, a
imagem original capturada do veículo, o timestamp exato do evento, e o resultado
da verificação (ex: "Autorizado" ou "Negado").
**2.3 Painel de Administração (Dashboard Web)**
● **RF-007: Autenticação de Administrador:** O sistema deve prover uma interface
web com uma tela de login segura. O acesso ao painel de administração e a todas
as suas funcionalidades deve ser restrito a usuários com credenciais válidas (nome
de usuário e senha), garantindo que apenas pessoal autorizado possa gerenciar o
sistema.
● **RF-008: Gerenciamento da lista de acesso (CRUD):** O painel deve oferecer ao
administrador autenticado a capacidade completa de gerenciar a lista de placas
autorizadas, seguindo as operações padrão de Criar, Ler, Atualizar e Deletar
(CRUD). A interface deve ser clara e permitir:
○ **Criar:** Adicionar uma nova placa à lista de acesso, possivelmente com um
campo de descrição (ex: "Veículo do Diretor").
○ **Ler:** Visualizar a lista completa de placas autorizadas de forma paginada
e pesquisável.
○ **Atualizar:** Editar os detalhes de uma placa já existente.
○ **Deletar:** Remover permanentemente uma placa da whitelist, revogando
seu acesso.


● **RF-009: Visualização de Logs de Acesso:** O administrador deve ter acesso a
uma seção no painel para visualizar o histórico de todos os eventos de acesso
registrados (conforme RF-006). A interface deve apresentar os logs em um formato
tabular e de fácil leitura, incluindo a imagem capturada. Funcionalidades essenciais
de busca por placa e filtragem por intervalo de datas e por status de acesso
(Autorizado/Negado) devem estar disponíveis.
● **RF-010: Acionamento Manual Remoto:** O painel de administração deve incluir
um controle de software, como um botão virtual, que permita ao administrador
acionar a abertura do portão remotamente a qualquer momento. Esta
funcionalidade serve como um mecanismo de anulação manual para situações
excepcionais (ex: permitir a entrada de um visitante não cadastrado) e como um
sistema de backup.
**3 REQUISITOS NÃO FUNCIONAIS (RNF)**
Esta seção define os atributos de qualidade, restrições e características
operacionais do sistema, descrevendo "como" o sistema deve operar, em vez de "o
que" ele deve fazer.
**3.1 Desempenho**
● **RNF-001: Latência de Processamento:** O tempo total decorrido desde a
captura da imagem de um veículo posicionado corretamente na área de
detecção até o envio do sinal de acionamento para o motor do portão (no caso
de uma placa autorizada) não deve exceder 5 segundos. Este tempo inclui a
captura da imagem, o processamento ALPR no endpoint, a comunicação com o
servidor, a validação no banco de dados e o comando de retorno.
● **RNF-002: Precisão do ALPR:** O subsistema de Reconhecimento Automático de
Placas de Veículos deve atingir uma taxa de precisão de reconhecimento de
caracteres de, no mínimo, 95% em condições de iluminação diurna e boa
visibilidade. Em condições de iluminação noturna, com o auxílio de iluminação
infravermelha adequada fornecida pela câmera, a precisão mínima aceitável é


de 85%.
**3.2 Confiabilidade e Disponibilidade**
● **RNF-003: Disponibilidade do Sistema:** A infraestrutura central do sistema
(servidor de aplicação backend e banco de dados) deve ser projetada para uma
disponibilidade de 99.5% (uptime). O software embarcado no endpoint
(Raspberry Pi) deve incorporar um mecanismo de watchdog ou serviço de
reinicialização automática para se recuperar de falhas de software inesperadas
sem a necessidade de intervenção física.
● **RNF-004: Operação Offline (Contingência):** O design da arquitetura deve
prever a possibilidade de uma futura implementação de um mecanismo de
contingência para operação offline. Isso envolveria o endpoint no portão
mantendo um cache local da whitelist, sincronizado periodicamente com o
servidor central. Em caso de perda de conectividade com a internet, o endpoint
poderia continuar a validar placas contra este cache local, garantindo a
continuidade da operação para veículos autorizados por um período limitado.^
**3.3 Segurança**
● **RNF-005: Comunicação Criptografada:** Toda a comunicação de dados entre o
endpoint Raspberry Pi e o servidor backend deve ser obrigatoriamente
criptografada utilizando o protocolo Transport Layer Security (TLS). Isso garante
a confidencialidade e a integridade dos dados transmitidos, como as imagens
das placas e as respostas da API, prevenindo ataques de interceptação
(man-in-the-middle).^
● **RNF-006: Segurança do Painel de Administração:** A aplicação web do painel
de administração deve ser desenvolvida seguindo as melhores práticas de
segurança para mitigar vulnerabilidades comuns, como as listadas no OWASP
Top 10, incluindo SQL Injection, Cross-Site Scripting (XSS) e Cross-Site Request
Forgery (CSRF). A escolha de um framework de backend robusto com
mecanismos de segurança integrados é um requisito fundamental para atender


a esta exigência.^
**3.4 Usabilidade**
● **RNF-007: Interface Intuitiva:** O design da interface do usuário (UI) e da
experiência do usuário (UX) do painel de administração deve ser limpo, intuitivo
e responsivo. Um administrador com conhecimentos básicos de informática deve
ser capaz de realizar todas as tarefas de gerenciamento (adicionar/remover
placas, consultar logs) com um mínimo de treinamento ou documentação.
**3.5 Manutenibilidade**
● **RNF-008: Código Modular e Documentado:** O código-fonte de todos os
componentes do sistema (software embarcado, backend e frontend) deve ser
estruturado de forma modular, com uma clara separação de responsabilidades.
O código deve ser bem comentado e acompanhado de uma documentação
técnica que facilite a compreensão, a manutenção futura e a integração de
novos desenvolvedores na equipe do projeto, um fator crítico para a
sustentabilidade do conhecimento dentro de uma empresa júnior.
**4 ARQUITETURA DO SISTEMA PROPOSTA
4.1 Visão Geral da Arquitetura**
A arquitetura do sistema será implementada seguindo um modelo de três
camadas distribuídas, que promove a modularidade, escalabilidade e manutenibilidade.
As três camadas são:

1. **Camada de Borda (Hardware/IoT Endpoint):** Composta por um dispositivo a ser
    definido, no momento, o cliente disponibilizou uma câmera Hikvision na qual
    estamos estudando suas especificidades e analisando sua viabilidade, instalada
    fisicamente no portão. Esta camada é responsável pelas tarefas em tempo real:
    captura de imagem da câmera, processamento local de ALPR e o acionamento
    físico do mecanismo do portão via relé.
2. **Camada de Servidor (Backend):** Uma aplicação web central que serve como o


```
cérebro do sistema. Ela expõe uma API RESTful segura, gerencia toda a lógica de
negócios (validação de placas, autenticação de administradores) e lida com a
persistência de dados no banco de dados (whitelist e logs de acesso).
```
3. **Camada de Cliente (Frontend):** Uma aplicação de página única (SPA -
    Single-Page Application) que funciona como o painel de administração. Esta
    aplicação é executada no navegador do administrador e consome a API do
    backend para fornecer uma interface de usuário rica, interativa e responsiva para o
    gerenciamento do sistema.
       Esta arquitetura deliberadamente separa o processamento na borda (edge) da
lógica de negócios central (core). Esta decisão estratégica, embora adicione uma
camada de comunicação de rede, é fundamental para a escalabilidade e a gestão do
sistema.
Centralizar a lista de acessos e os logs no servidor significa que adicionar um
novo portão ao sistema é tão simples quanto configurar um novo endpoint para se
comunicar com a mesma API, sem a necessidade de complexos mecanismos de
sincronização de banco de dados. Além disso, atualizações na lógica de negócios ou
no painel de administração podem ser implementadas centralmente no servidor, sem a
necessidade de intervenção física em cada dispositivo de portão.
**4.2 Componente de Hardware (IoT Endpoint)**
● **Algumas recomendações após pesquisas**
○ **Microcontrolador:** A unidade de processamento selecionada é o
**Raspberry Pi 4 Model B** (com 2GB de RAM ou superior). Esta escolha é
justificada por seu excelente balanço entre custo, poder de
processamento (suficiente para executar modelos de visão computacional
modernos), ampla conectividade de rede (Wi-Fi e Ethernet) e,
crucialmente, seus pinos de Entrada/Saída de Propósito Geral (GPIO),
que são essenciais para a interface com hardware externo como o


módulo relé.^
○ **Câmera:** Será utilizada uma câmera de alta resolução compatível com o
Raspberry Pi, como o **Pi Camera Module V2** ou uma câmera USB de
qualidade equivalente. Um requisito mandatório para a câmera é a
capacidade de visão noturna, utilizando um iluminador infravermelho (IR),
para garantir o cumprimento do requisito de precisão noturna (RNF-002).
Atualmente, estamos verificando a compatibilidade com a câmera
Hikvision.
○ **Módulo de Acionamento:** Um **módulo relé de 5V de um canal**. Este
componente simples e robusto atua como um interruptor eletrônico que
pode ser controlado pelos pinos GPIO do Raspberry Pi. Ele será
conectado em paralelo aos contatos do botão de acionamento manual
existentes no painel de controle do motor do portão. Esta abordagem é
significativamente mais simples e confiável do que tentar fazer a
engenharia reversa e replicar os sinais de radiofrequência (RF) de um
controle remoto, evitando complexidades desnecessárias e garantindo
compatibilidade com praticamente qualquer sistema de portão
motorizado.
_●_ **_Importante:_** _o design de arquitetura e montagem dos componentes de hardware
ficarão a cargo do cliente, conforme acordado previamente._
**4.3 Componente de Software Embarcado (no Raspberry Pi)
● Se for utilizado Raspberry:**
○ **Sistema Operacional: Raspbian Linux** (atualmente conhecido como
Raspberry Pi OS), por ser a distribuição oficial, bem suportada e familiar
para a maioria dos desenvolvedores. Alternativamente, o Ubuntu Core
pode ser considerado para implantações que exijam maior robustez e
segurança.^
● **Lógica de Aplicação:** O núcleo do software embarcado será um script Python
robusto, configurado para rodar como um serviço contínuo. Este script


orquestrará o fluxo de trabalho completo no endpoint: monitorar a área de
detecção, capturar uma imagem quando um veículo estiver presente, invocar a
biblioteca ALPR para processar a imagem, enviar a placa detectada para a API
do backend através de uma requisição HTTPS segura, aguardar a resposta de
autorização e, se positiva, acionar o pino GPIO conectado ao relé por um curto
período.
● **Análise e Seleção da Biblioteca ALPR:** A escolha da biblioteca de software
para o Reconhecimento Automático de Placas de Veículos é a decisão técnica
mais crítica que impactará diretamente a precisão e a confiabilidade do sistema.
Após uma análise de alternativas de código aberto, a seguinte avaliação foi
realizada:
○ **Opção 1 (OpenCV + Tesseract):** Esta é a abordagem "clássica",
utilizando a biblioteca OpenCV para as etapas de pré-processamento de
imagem (conversão para escala de cinza, detecção de bordas, correção
de perspectiva) e o motor Tesseract OCR para a extração de texto. No
entanto, o Tesseract foi originalmente projetado para o reconhecimento de
texto em documentos escaneados e seu desempenho em imagens do
"mundo real", como placas de veículos com variações de iluminação,
ângulos e ruído, é notoriamente baixo sem um pipeline de
pré-processamento extremamente complexo e frágil.^
○ **Opção 2 (OpenALPR):** Uma biblioteca dedicada e poderosa, escrita em
C++ e otimizada especificamente para ALPR, com bindings disponíveis
para Python.^ Oferece alta precisão, mas sua configuração pode ser
complexa, exigindo a compilação de múltiplas dependências (como
Tesseract e OpenCV), o que pode ser um desafio para uma equipe
menos experiente.
○ **Opção 3 (easyocr):** Uma biblioteca Python moderna que utiliza modelos
de Deep Learning (redes neurais convolucionais e recorrentes)
pré-treinados, construída sobre o framework PyTorch. A comunidade e


testes práticos demonstram que easyocr oferece uma precisão
significativamente superior à do Tesseract em cenários não ideais, sendo
muito mais robusta às variações de imagem. Sua instalação é trivial (pip
install easyocr), tornando-a a opção mais acessível e eficaz.^
○ **Recomendação I:** A tecnologia recomendada para a função de ALPR é o
**easyocr**. Esta biblioteca oferece o melhor equilíbrio entre altíssima
precisão (devido à sua base em Deep Learning), facilidade de
implementação e manutenção para a equipe da empresa júnior, e por ser
uma solução de código aberto bem mantida.
○ **Recomendação II:** Capturar a imagem como uma fotografia e utilizar
uma biblioteca de extração de textos de imagens, para cumprir prazos,
caso a análise de viabilidade das outras soluções ultrapasse o
cronograma para o semestre 2025.2.
**Tabela 4.3.1: Análise Comparativa de Bibliotecas ALPR
Critério OpenCV + Tesseract OpenALPR easyocr
Tecnologia Subjacente** Processamento de
Imagem Clássico, OCR
Tradicional
Visão
Computacional/ML, C++
Deep Learning
(CNN/RNN),
Python/PyTorch
**Precisão (Mundo Real)** Baixa a Média (requer
ajuste manual intensivo)
Alta Muito Alta (robusto a
variações)
**Complexidade de
Implementação**
Alta (requer pipeline de
pré-processamento
manual)
Média (compilação de
dependências C++)
Baixa (instalação via
pip)
**Comunidade e Suporte** Vasta (OpenCV), Média
(Tesseract para placas)
Média Crescente e Ativa
**Recomendação** Não Recomendado Alternativa Viável (para
equipes experientes)
**Recomendado
4.4 Arquitetura do Backend**
● **Análise e Seleção do Framework:** Para manter a consistência tecnológica e


aproveitar o ecossistema Python, o backend será desenvolvido nesta linguagem.
○ **Flask:** Um microframework minimalista e flexível. Embora seja excelente
para projetos pequenos ou APIs simples, exigiria a integração manual de
bibliotecas de terceiros para ORM, sistema de administração e
autenticação, o que aumentaria o tempo de desenvolvimento e a
complexidade.
○ **FastAPI:** Um framework moderno e de altíssimo desempenho, ideal para
a construção de APIs assíncronas. Sua principal vantagem é a
performance, que, embora impressionante, pode ser considerada
excessiva para a carga de requisições esperada neste projeto, onde a
velocidade de desenvolvimento é um fator mais crítico.
○ **Django:** Um framework de alto nível, "batteries-included" (com tudo
incluído). Django vem com um Object-Relational Mapper (ORM)
poderoso, um sistema de autenticação seguro e, mais importante, um
painel de administração totalmente funcional e customizável que pode ser
gerado automaticamente a partir dos modelos de dados.
○ **Recomendação:** Pode ser uma boa escolha utilizar o **Django**. Para uma
equipe de empresa júnior, os benefícios de ter funcionalidades robustas e
seguras prontas para uso superam a flexibilidade de frameworks
minimalistas. O painel de administração nativo do Django pode
implementar a maioria dos requisitos RF-008 e RF-009 com um esforço
de desenvolvimento drasticamente reduzido, permitindo que a equipe se
concentre na lógica de negócios específica do projeto. Entretanto, para
fins de encaixe no cronograma, pode-se utilizar o **FastAPI**.
● **Design da API REST:** A API será projetada seguindo os princípios RESTful para
garantir uma comunicação padronizada e sem estado entre o backend, o
frontend e o endpoint IoT. Os principais endpoints incluirão:
○ **POST /api/access-events/:** Usado pelo Raspberry Pi para submeter os
dados de uma nova tentativa de acesso (placa, imagem).


○ **GET /api/whitelist/:** Usado pelo frontend para obter a lista de placas
autorizadas.
○ **POST, PUT, DELETE /api/whitelist/<id>/:** Endpoints para o frontend
realizar as operações CRUD na whitelist.
○ **GET /api/access-logs/:** Usado pelo frontend para buscar os registros de
eventos de acesso, com suporte a filtros.
○ **POST /api/gate/trigger/:** Usado pelo frontend para o acionamento
manual remoto do portão.
**● Seleção do SGBD:**
○ **MySQL vs. PostgreSQL:** Ambos são Sistemas de Gerenciamento de
Banco de Dados (SGBD) relacionais, de código aberto e extremamente
capazes. No entanto, o PostgreSQL é frequentemente preferido em novos
projetos por sua conformidade mais estrita com o padrão ACID
(Atomicidade, Consistência, Isolamento, Durabilidade) em todas as
configurações, e por oferecer um conjunto mais rico de tipos de dados e
opções de indexação avançadas, como GIN (Generalized Inverted Index),
que podem ser úteis para futuras funcionalidades de busca textual
complexa nos logs.^
○ **Recomendação:** O SGBD recomendado é o **PostgreSQL**.^ Sua robustez,
extensibilidade e conformidade com os padrões o tornam uma escolha
tecnicamente superior e mais preparada para a evolução do sistema, sem
nenhuma desvantagem prática em relação ao MySQL para o escopo
deste projeto.
**4.5 Arquitetura do Frontend (Painel de Administração)**
● **Análise e Seleção do Framework:** A interface do painel de administração será
desenvolvida como uma SPA (Single-Page Application) para proporcionar uma
experiência de usuário moderna, rápida e fluida.
○ **Angular:** Um framework completo e opinativo, mantido pelo Google. É
extremamente poderoso, especialmente para aplicações de grande


escala, mas possui uma curva de aprendizado mais íngreme devido à sua
complexidade e ao uso de TypeScript e RxJS.^
○ **Vue.js:** Conhecido por sua abordagem progressiva e curva de
aprendizado suave. É uma excelente opção, mas seu ecossistema,
embora robusto, é um pouco menor em comparação com o React.^
○ **React:** Tecnicamente uma biblioteca para a construção de interfaces de
usuário, mas amplamente utilizada como um framework. Possui o maior e
mais maduro ecossistema, a maior comunidade de desenvolvedores e
uma quantidade incomparável de bibliotecas de componentes de UI,
ferramentas e tutoriais disponíveis.^
○ **Recomendação:** A tecnologia recomendada para o frontend é o **React**.
Seu vasto ecossistema e popularidade representam uma vantagem
estratégica para uma empresa júnior, pois facilitam a resolução de
problemas, aceleram o desenvolvimento através do reuso de
componentes e capacitam a equipe com uma das tecnologias mais
demandadas no mercado.
● **Seleção da Biblioteca de Componentes de UI:** Para acelerar o
desenvolvimento do dashboard e garantir uma UI consistente e de alta
qualidade, será utilizada uma biblioteca de componentes pré-construídos.
○ **Opções:** Existem várias bibliotecas de alta qualidade, como Ant Design,
CoreUI e Tailwind UI.^
○ **Recomendação:** A biblioteca de componentes recomendada é a **MUI
(anteriormente Material-UI)**. A MUI implementa as diretrizes do Google
Material Design e oferece um conjunto extremamente completo e maduro
de componentes prontos para uso, como Data Grids avançados,
formulários com validação, seletores de data/hora e gráficos, que se
alinham perfeitamente com os requisitos de um painel de administração
de dados (RF-008, RF-009).
**5 ENTREGÁVEIS E FASES DO PROJETO**


O projeto será executado utilizando uma abordagem de desenvolvimento
iterativo e incremental, dividido em quatro fases distintas. Esta metodologia permite a
validação contínua, o gerenciamento de riscos e a entrega de valor de forma
progressiva.
**5.1 Fase 1: Prova de Conceito (PoC)**
● **Duração:** 2 semanas
● **Objetivo:** Validar as tecnologias-chave e mitigar os maiores riscos técnicos do
projeto em um ambiente controlado, especificamente o reconhecimento de
placas e o controle de hardware.
**● Entregáveis:**
○ Um script funcional em um protoboard que utiliza a biblioteca easyocr
para capturar uma imagem de uma câmera e imprimir a string da placa
detectada no terminal.
○ Um segundo script de teste que demonstra o acionamento bem-sucedido
de um módulo.
● **Critério de Sucesso:**
○ Atingir uma taxa de reconhecimento de placas de teste superior a 90%
em condições de laboratório. O relé deve ser acionado de forma confiável
e repetível através do comando de software.
**5.2 Fase 2: Desenvolvimento do MVP (Produto Mínimo Viável)**
● **Duração:** 6 semanas
● **Objetivo:** Construir a funcionalidade central do sistema de ponta a ponta,
integrando todas as camadas da arquitetura para criar um produto funcional.
**● Entregáveis:**

1. Backend com a API implementada, incluindo endpoints para autenticação,
    gerenciamento da lista de acesso (CRUD) e registro de eventos de
    acesso, com o banco de dados PostgreSQL configurado.
2. Software embarcado finalizado, capaz de capturar imagens, processá-las


```
com easyocr, comunicar-se com a API do backend e acionar o portão
com base na resposta.
```
3. Painel de administração com as funcionalidades essenciais: login de
    administrador, gerenciamento completo da whitelist e uma visualização
    básica dos logs de acesso.
4. Um sistema totalmente integrado, capaz de operar em um ambiente de
    teste, abrindo um portão de demonstração com base em uma placa
    registrada na whitelist.
**5.3 Fase 3: Testes e Implantação Piloto**
● **Duração:** 2 semanas
● **Objetivo:** Testar rigorosamente o sistema MVP em um ambiente real (no local
do cliente) para avaliar o desempenho, a confiabilidade e a usabilidade,
coletando feedback para refinamentos.
**● Entregáveis:**
1. O sistema MVP instalado e configurado em um portão selecionado nas
instalações do cliente para um período de testes controlados.
2. Um relatório de testes abrangente, detalhando as métricas de
desempenho (precisão do ALPR em condições reais, latência de ponta a
ponta) e um registro de todos os bugs e anomalias identificados.
3. Uma sessão de feedback formal com os usuários administradores do
cliente para avaliar a usabilidade do painel e coletar sugestões de
melhoria.
**5.4 Fase 4: Entrega Final e Documentação**
● **Duração:** a definir futuramente a partir de novo cronograma
● **Objetivo:** Finalizar o produto com base no feedback da fase piloto, realizar a
implantações final e entregar toda a documentação de suporte necessária.
**● Entregáveis:**
○ A versão de produção do sistema SCAVA, estável e com os bugs


prioritários corrigidos, devidamente instalada e operacional.
○ Um **Manual do Administrador** detalhado, um guia de usuário para o
cliente explicando como operar o painel de administração, gerenciar a
whitelist e interpretar os logs de acesso.
○ A **Documentação Técnica do Projeto** , incluindo esta Especificação de
Requisitos de Software finalizada, diagramas de arquitetura e um guia
básico de instalação e manutenção para a equipe de desenvolvimento.
○ Implementação das funcionalidades adicionais e incrementais

