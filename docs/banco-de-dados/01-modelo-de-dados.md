# **Especificação do Modelo de Dados para o Sistema de Controle de Acesso Veicular (SCAVA)**

## **Sumário Executivo**

Este documento estabelece a especificação técnica completa para o modelo de dados do Sistema de Controle de Acesso Veicular (SCAVA). O seu propósito é servir como a fonte canônica de verdade ("source of truth") para a equipe de desenvolvimento no que tange à estrutura, aos relacionamentos e às restrições do banco de dados PostgreSQL. O modelo foi projetado para ser robusto, escalável e seguro, atendendo diretamente a todos os requisitos funcionais e não funcionais delineados na documentação do projeto.

A arquitetura de dados é centrada em três entidades fundamentais: administradores do sistema (users), veículos autorizados (authorized\_plates) e eventos de acesso (access\_logs). As decisões arquiteturais chave, como a utilização de Identificadores Únicos Universais (UUIDs) como chaves primárias, o manuseio rigoroso de fusos horários com o tipo de dado TIMESTAMPTZ, e a imposição da integridade de dados através de tipos enumerados (ENUM), foram tomadas para garantir a segurança, a consistência e a auditabilidade do sistema. Este modelo de dados não apenas suporta as funcionalidades atuais, como autenticação de administradores, gerenciamento da lista de permissões (whitelist) e visualização de logs, mas também estabelece uma fundação sólida para futuras expansões, como o gerenciamento de múltiplos dispositivos e sistemas de permissões baseados em papéis.

---

## **1.0 Modelo de Dados Conceitual e Racional de Design**

### **1.1 Introdução às Entidades de Domínio Centrais**

A estrutura do banco de dados do sistema SCAVA é construída sobre três entidades de domínio principais, que representam os pilares conceituais da aplicação, conforme identificado nas fases iniciais do projeto.1 A clara definição e separação dessas entidades garantem um design de banco de dados normalizado e de fácil manutenção.

* **Administradores (users):** Esta entidade representa os operadores humanos do sistema. É responsável por armazenar as credenciais e informações de identificação dos usuários que têm permissão para acessar o painel de administração web. A existência desta tabela é um pré-requisito direto para a implementação do requisito de autenticação segura (RF-007), que restringe o acesso às funcionalidades de gerenciamento apenas a pessoal autorizado.1  
* **Veículos Autorizados (authorized\_plates):** Esta entidade constitui a "lista de permissões" (whitelist) do sistema. Ela mantém um registro de todas as placas de veículos que têm permissão para acionar a abertura do portão. Esta tabela é o coração da lógica de controle de acesso e suporta diretamente o requisito de gerenciamento CRUD (Criar, Ler, Atualizar, Deletar) da lista de acesso pelo administrador (RF-008).1  
* **Eventos de Acesso (access\_logs):** Esta entidade funciona como uma trilha de auditoria imutável. Cada tentativa de acesso, seja ela bem-sucedida ou falha, é registrada como uma entrada nesta tabela. O registro persistente de cada evento, incluindo a placa detectada, o timestamp e a imagem capturada, é um requisito funcional crítico (RF-006) e fundamental para as funcionalidades de visualização e filtragem de histórico de acessos (RF-009).1

### **1.2 Diagrama de Entidade-Relacionamento (ERD) de Alto Nível**

O diagrama a seguir fornece uma representação visual do modelo de dados, ilustrando as tabelas e os relacionamentos entre elas. Este ERD oferece uma compreensão imediata e de alto nível da arquitetura do esquema.

Snippet de código

erDiagram  
    users {  
        UUID id PK  
        TEXT email UK  
        TEXT hashed\_password  
        TIMESTAMPTZ created\_at  
        TIMESTAMPTZ updated\_at  
    }

    authorized\_plates {  
        UUID id PK  
        TEXT plate  
        TEXT normalized\_plate UK  
        TEXT description  
        TIMESTAMPTZ created\_at  
        TIMESTAMPTZ updated\_at  
    }

    access\_logs {  
        UUID id PK  
        TIMESTAMPTZ timestamp  
        TEXT plate\_string\_detected  
        access\_status status  
        TEXT image\_storage\_key  
        UUID authorized\_plate\_id FK  
    }

    authorized\_plates |

|--o{ access\_logs : "é referenciada em"

### **1.3 Decisões Arquiteturais Fundamentais**

As seguintes decisões de design de alto nível foram tomadas para garantir que o modelo de dados seja seguro, consistente e performático, abordando proativamente os desafios inerentes a um sistema de controle de acesso.

* **Escolha de Chaves Primárias (UUIDs):** Em vez de utilizar inteiros auto-incrementais tradicionais, todas as chaves primárias serão do tipo UUID (Identificador Único Universal). Esta abordagem oferece vantagens significativas. Primeiramente, UUIDs não são sequenciais, o que impede que agentes mal-intencionados enumerem recursos através da adivinhação de IDs em URLs de API, aumentando a segurança do sistema. Em segundo lugar, como os UUIDs são globalmente únicos, eles simplificam cenários futuros de replicação de banco de dados, fusão de dados de múltiplas instâncias ou migração para arquiteturas de microsserviços, onde a prevenção de colisão de chaves é crucial.  
* **Manuseio de Timestamps e Fusos Horários (TIMESTAMPTZ):** Todo e qualquer dado temporal será armazenado utilizando o tipo de dado TIMESTAMPTZ do PostgreSQL. Este tipo armazena o timestamp em UTC (Tempo Universal Coordenado) internamente e o converte para o fuso horário da sessão do cliente no momento da consulta. A utilização deste tipo é uma decisão não negociável para garantir a precisão e a ausência de ambiguidade nos registros de auditoria (RF-006).1 Isso elimina completamente problemas complexos relacionados a horários de verão ou a operação do sistema por administradores em diferentes fusos horários.  
* **Uso de Tipos Enumerados (ENUM):** Para o campo status na tabela access\_logs, será definido um tipo de dado personalizado access\_status no PostgreSQL. A alternativa seria usar um campo de texto (VARCHAR), mas essa abordagem é suscetível a erros de digitação (e.g., "Autorizado", "autorizado", "Aprovado") que corromperiam a integridade dos dados e complicariam as consultas. Ao definir um ENUM com os valores permitidos ('Authorized', 'Denied'), a integridade é imposta no nível mais baixo possível: o próprio banco de dados.1 Qualquer tentativa de inserir um valor inválido será rejeitada, garantindo que os dados armazenados sejam sempre consistentes. Esta abordagem é também mais eficiente em termos de armazenamento e torna o esquema do banco de dados auto-documentado. Esta é uma decisão estratégica para transferir a responsabilidade da validação de dados para o banco de dados, tornando a aplicação inerentemente mais robusta.

---

## **2.0 Definição Detalhada do Esquema Lógico**

Esta seção fornece uma descrição detalhada de cada tabela no esquema, incluindo a finalidade de cada coluna, seus tipos de dados lógicos, restrições e a justificativa vinculada aos requisitos do projeto.

### **2.1 Tabela: users (Identidade do Administrador)**

* **Propósito:** Armazenar as credenciais de autenticação para os administradores que acessam o painel web. Esta tabela é a base para o sistema de login seguro, conforme os requisitos de autenticação 1 e as tarefas de backend para criação de usuários e validação de credenciais.1

| Nome da Coluna | Tipo Lógico | Restrições / Descrição | Racional / Requisito Fonte |
| :---- | :---- | :---- | :---- |
| id | UUID | Chave Primária | Identificador único e não sequencial para cada usuário administrador. |
| email | Text | Not Null, Unique | Identificador de login do usuário. Deve ser único em todo o sistema. |
| hashed\_password | Text | Not Null | Senha do usuário armazenada como um hash criptográfico com salt. O texto plano nunca é armazenado, conforme as melhores práticas de segurança.1 |
| created\_at | Timestamp with Time Zone | Not Null, Default NOW() | Timestamp de auditoria para o momento da criação do registro do usuário. |
| updated\_at | Timestamp with Time Zone | Not Null, Default NOW() | Timestamp de auditoria para a última atualização do registro do usuário. |

### **2.2 Tabela: authorized\_plates (Whitelist de Veículos)**

* **Propósito:** Manter a lista definitiva de placas de veículos autorizadas. Esta tabela serve como fonte de dados para a interface de gerenciamento CRUD 1 e é consultada em tempo real pela lógica de controle de acesso para validar cada veículo.1

| Nome da Coluna | Tipo Lógico | Restrições / Descrição | Racional / Requisito Fonte |
| :---- | :---- | :---- | :---- |
| id | UUID | Chave Primária | Identificador único para cada placa na whitelist. |
| plate | Text | Not Null | A string da placa de licença como inserida pelo usuário, mantendo a formatação original (e.g., "ABC-1234"). Usada para exibição na UI. |
| normalized\_plate | Text | Not Null, Unique | Uma representação canônica e indexada da placa, sem caracteres especiais e em maiúsculas (e.g., "ABC1234"). Usada para comparações lógicas. |
| description | Text | Nullable | Um campo opcional para o administrador adicionar contexto sobre o veículo (e.g., "Veículo do Diretor"). |
| created\_at | Timestamp with Time Zone | Not Null, Default NOW() | Timestamp de auditoria para quando a placa foi adicionada. |
| updated\_at | Timestamp with Time Zone | Not Null, Default NOW() | Timestamp de auditoria para a última modificação da placa. |

A inclusão da coluna normalized\_plate é uma decisão de design crucial. Ela faz mais do que apenas otimizar o desempenho da consulta de verificação, que é uma operação de alta frequência. Esta coluna efetivamente desacopla a *apresentação* de uma placa de sua *identidade lógica*. O requisito imediato é realizar comparações que ignorem maiúsculas/minúsculas e hifens.1 Uma função de normalização simples resolve isso. No entanto, ao armazenar tanto a placa original (plate) quanto a versão normalizada (normalized\_plate), o sistema ganha resiliência a futuras mudanças. A interface do usuário pode sempre exibir a placa exatamente como foi inserida, preservando a fidelidade para o administrador. Enquanto isso, toda a lógica de negócio de controle de acesso interage exclusivamente com a coluna normalized\_plate, que é unicamente indexada. Se, no futuro, o sistema precisar suportar novos formatos de placas (e.g., de outros países, com espaços ou outros caracteres), apenas a função de normalização precisará ser atualizada, sem a necessidade de migrações de dados complexas ou alterações na camada de apresentação. O esquema torna-se, assim, resistente a mudanças nas regras de negócio.

### **2.3 Tabela: access\_logs (Auditoria de Eventos)**

* **Propósito:** Criar um registro persistente e de inserção única (append-only) de cada tentativa de acesso. Esta tabela fornece a trilha de auditoria completa exigida pelas especificações do sistema 1 e alimenta a interface de visualização e filtragem de logs no painel de administração.1

| Nome da Coluna | Tipo Lógico | Restrições / Descrição | Racional / Requisito Fonte |
| :---- | :---- | :---- | :---- |
| id | UUID | Chave Primária | Identificador único para cada evento de acesso registrado. |
| timestamp | Timestamp with Time Zone | Not Null, Default NOW() | O momento exato em que o evento foi processado pela API, garantindo uma linha do tempo precisa. |
| plate\_string\_detected | Text | Not Null | A string de texto exata que foi extraída da imagem do veículo pelo processo de OCR. |
| status | access\_status (ENUM) | Not Null | O resultado da verificação: 'Authorized' ou 'Denied'. |
| image\_storage\_key | Text | Not Null | O caminho ou chave para a imagem capturada no sistema de armazenamento (e.g., um caminho no sistema de arquivos ou uma chave de objeto no S3).1 |
| authorized\_plate\_id | UUID | Nullable, Foreign Key | Referencia authorized\_plates.id. Associa o evento a um veículo específico da whitelist se o acesso foi autorizado. É NULL para acessos negados. |

A decisão de tornar a chave estrangeira authorized\_plate\_id nula (NULL) é fundamental para modelar corretamente a realidade do domínio e para otimizar o desempenho. O sistema deve registrar *todas* as tentativas de acesso, incluindo as de veículos não autorizados.1 Uma tentativa negada, por definição, não tem uma entrada correspondente na tabela authorized\_plates, tornando impossível satisfazer uma restrição NOT NULL. Portanto, o valor NULL representa semanticamente a ausência de uma correspondência na whitelist. Esta modelagem também traz um benefício de desempenho significativo. A consulta mais comum na página de logs será a visualização do histórico cronológico 1, que pode ser executada com um SELECT simples na tabela access\_logs ordenado por timestamp. Como esta consulta não requer um JOIN com authorized\_plates, ela pode ser satisfeita de forma extremamente rápida, utilizando apenas os índices da própria tabela de logs. Um JOIN só será necessário em casos de uso menos frequentes, como quando um administrador solicita detalhes adicionais sobre um veículo específico que teve o acesso autorizado.

---

## **3.0 Modelo de Dados Físico para PostgreSQL (DDL)**

Esta seção contém o script DDL (Data Definition Language) completo e pronto para uso, que implementa o modelo lógico descrito para o banco de dados PostgreSQL, conforme especificado na configuração do ambiente de desenvolvimento.1 Este script deve ser a base para as migrações gerenciadas pelo Alembic.1

### **3.1 Definições de Tipos Personalizados**

SQL

\-- Define o vocabulário controlado para os resultados dos eventos de acesso,  
\-- garantindo a integridade dos dados na coluna 'status'.  
CREATE TYPE access\_status AS ENUM ('Authorized', 'Denied');

### **3.2 Declarações de Criação de Tabelas**

SQL

\-- Tabela para armazenar as credenciais dos administradores do sistema.  
CREATE TABLE users (  
    id UUID PRIMARY KEY DEFAULT gen\_random\_uuid(),  
    email TEXT NOT NULL UNIQUE,  
    hashed\_password TEXT NOT NULL,  
    created\_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),  
    updated\_at TIMESTAMPTZ NOT NULL DEFAULT NOW()  
);

\-- Tabela para armazenar a lista de placas de veículos autorizadas (whitelist).  
CREATE TABLE authorized\_plates (  
    id UUID PRIMARY KEY DEFAULT gen\_random\_uuid(),  
    plate TEXT NOT NULL,  
    normalized\_plate TEXT NOT NULL UNIQUE,  
    description TEXT,  
    created\_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),  
    updated\_at TIMESTAMPTZ NOT NULL DEFAULT NOW()  
);

\-- Tabela para a trilha de auditoria de todas as tentativas de acesso.  
CREATE TABLE access\_logs (  
    id UUID PRIMARY KEY DEFAULT gen\_random\_uuid(),  
    "timestamp" TIMESTAMPTZ NOT NULL DEFAULT NOW(),  
    plate\_string\_detected TEXT NOT NULL,  
    status access\_status NOT NULL,  
    image\_storage\_key TEXT NOT NULL,  
    authorized\_plate\_id UUID REFERENCES authorized\_plates(id) ON DELETE SET NULL  
);

### **3.3 Gatilho para Geração de normalized\_plate**

Para garantir a consistência e automatizar a lógica de normalização, um gatilho (trigger) será implementado no banco de dados. Isso move a responsabilidade de normalização da aplicação para o banco de dados, garantindo que a coluna normalized\_plate seja sempre calculada da mesma forma, independentemente de como os dados são inseridos ou atualizados.

SQL

\-- Função do gatilho para normalizar a placa (remover não alfanuméricos e converter para maiúsculas).  
CREATE OR REPLACE FUNCTION normalize\_plate\_trigger\_func()  
RETURNS TRIGGER AS $$  
BEGIN  
    NEW.normalized\_plate :\= UPPER(REGEXP\_REPLACE(NEW.plate, '\[^A-Za-z0-9\]', '', 'g'));  
    RETURN NEW;  
END;  
$$ LANGUAGE plpgsql;

\-- Criação do gatilho que executa a função antes de cada INSERT ou UPDATE na tabela authorized\_plates.  
CREATE TRIGGER before\_insert\_or\_update\_authorized\_plates  
BEFORE INSERT OR UPDATE ON authorized\_plates  
FOR EACH ROW  
EXECUTE FUNCTION normalize\_plate\_trigger\_func();

---

## **4.0 Estratégia de Desempenho e Integridade de Dados**

Esta seção detalha as estratégias de indexação e as restrições de integridade referencial que garantem que o sistema atenda aos seus requisitos não funcionais de desempenho, confiabilidade e consistência de dados.1

### **4.1 Estratégia de Indexação para Otimização de Consultas**

Cada índice foi projetado para otimizar um padrão de consulta específico, diretamente derivado das funcionalidades descritas no backlog do projeto.

* **Índices da Tabela authorized\_plates:**  
  * CREATE UNIQUE INDEX ON authorized\_plates (normalized\_plate);  
    * **Racional:** Este é o índice mais crítico do sistema. Ele suporta a consulta de altíssima frequência que verifica se uma placa detectada existe na whitelist, uma operação central da lógica de negócio.1 A restrição UNIQUE também previne a inserção de placas logicamente duplicadas, garantindo a integridade da lista.  
  * CREATE INDEX ON authorized\_plates (plate text\_pattern\_ops);  
    * **Racional:** Este índice otimiza a funcionalidade de busca no painel de administração.1 Ele permite buscas eficientes baseadas em prefixo (e.g., WHERE plate LIKE 'ABC%'), proporcionando uma experiência de usuário fluida ao pesquisar na whitelist.  
* **Índices da Tabela access\_logs:**  
  * CREATE INDEX ON access\_logs ("timestamp" DESC);  
    * **Racional:** A consulta mais comum na página de logs será a visualização dos eventos mais recentes.1 Este índice torna essa operação, que ordena os resultados por data em ordem decrescente, extremamente rápida.  
  * CREATE INDEX ON access\_logs (status, "timestamp" DESC);  
    * **Racional:** Este índice composto acelera as consultas de filtragem por status (e.g., "mostrar todos os acessos 'Denied'") combinadas com a ordenação por data, uma funcionalidade chave do painel de logs.1  
  * CREATE INDEX ON access\_logs (plate\_string\_detected text\_pattern\_ops);  
    * **Racional:** Suporta a funcionalidade de busca por uma string de placa específica dentro do histórico de logs.1  
  * CREATE INDEX ON access\_logs (authorized\_plate\_id);  
    * **Racional:** Embora a chave estrangeira seja nula em muitos casos, este índice é crucial para encontrar eficientemente todos os eventos de acesso associados a um veículo autorizado específico, por exemplo, ao gerar um relatório de acesso para um único veículo.

### **4.2 Relacionamentos de Chave Estrangeira e Integridade Referencial**

A integridade referencial entre as tabelas de eventos e de veículos autorizados é mantida através de uma restrição de chave estrangeira com uma política de exclusão cuidadosamente escolhida.

* ALTER TABLE access\_logs ADD CONSTRAINT fk\_authorized\_plate FOREIGN KEY (authorized\_plate\_id) REFERENCES authorized\_plates(id) ON DELETE SET NULL;  
  * **Racional para ON DELETE SET NULL:** A escolha desta cláusula é deliberada e crítica para a preservação da trilha de auditoria. Se um administrador remover uma placa da whitelist, a ação padrão (ON DELETE RESTRICT) impediria a exclusão, ou a ação ON DELETE CASCADE apagaria todos os registros de log históricos associados àquela placa. Ambas são indesejáveis. Apagar o histórico corromperia a trilha de auditoria, violando o propósito do requisito RF-006.1 A política ON DELETE SET NULL resolve este problema de forma elegante: ela permite que a placa seja removida da whitelist, mas, em vez de apagar os logs, ela simplesmente quebra o vínculo, definindo o campo authorized\_plate\_id como NULL nos registros históricos. O log do evento permanece, mas agora ele não está mais associado a uma placa *atualmente* autorizada. Isso preserva o histórico completo enquanto mantém a integridade referencial do banco de dados.

---

## **5.0 Escalabilidade e Considerações Futuras**

Este modelo de dados foi projetado não apenas para as necessidades atuais, mas também com uma visão de futuro, permitindo que o sistema evolua sem a necessidade de reestruturações dispendiosas.

### **5.1 Estratégia de Arquivamento de Dados para access\_logs**

* **O Problema:** A tabela access\_logs crescerá indefinidamente com o tempo. Em um sistema de produção, ela pode acumular milhões de registros, o que eventualmente degradará o desempenho das consultas, dos backups e das operações de manutenção.  
* **A Solução:** Uma estratégia proativa para gerenciar este crescimento é utilizar o recurso de particionamento de tabelas nativo do PostgreSQL. A tabela access\_logs pode ser particionada por intervalo de data (e.g., criando uma nova partição para cada mês ou trimestre). Consultas que filtram por timestamp se beneficiarão enormemente, pois o planejador de consultas do PostgreSQL poderá ignorar partições que não contêm os dados relevantes. Além disso, partições antigas podem ser facilmente movidas para um armazenamento mais lento e barato, ou até mesmo desanexadas da tabela principal para fins de arquivamento, mantendo o conjunto de dados "quente" (recente e frequentemente acessado) pequeno e performático.

### **5.2 Potenciais Extensões do Esquema**

O esquema atual pode ser estendido de forma limpa para suportar novas funcionalidades:

* **Papéis e Permissões de Usuário:** O modelo de autenticação atual é simples (todos são administradores). Para suportar diferentes níveis de acesso, poderiam ser adicionadas uma tabela roles (e.g., 'Admin', 'Auditor') e uma tabela de junção user\_roles. Isso permitiria, por exemplo, que um usuário 'Auditor' visualizasse os logs, mas não pudesse modificar a whitelist.  
* **Gerenciamento de Dispositivos:** O sistema atual assume um único ponto de acesso. Para escalar para múltiplos portões, uma nova tabela devices poderia ser criada para registrar cada dispositivo IoT (Raspberry Pi). A tabela access\_logs incluiria então uma chave estrangeira device\_id, permitindo que o sistema filtre logs por portão e gerencie a configuração de cada dispositivo centralmente.  
* **Alertas e Notificações:** Para transformar o sistema de um registrador passivo para uma ferramenta de segurança proativa, uma nova tabela alerts poderia ser introduzida. Ela poderia registrar eventos específicos, como múltiplas tentativas de acesso negadas da mesma placa em um curto período, e servir como base para um sistema que envia notificações por e-mail ou push para os administradores.

#### **Referências citadas**

1. piiv-unicap-especificacao-projetos-solucoes-eletronicas-do-futuro\_v1.pdf