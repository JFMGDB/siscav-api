# Coleção Postman - SISCAV API

Esta coleção Postman contém todos os endpoints da API SISCAV para facilitar os testes e desenvolvimento.

## Arquivos

- `SISCAV_API.postman_collection.json` - Coleção principal com todos os endpoints
- `SISCAV_API.postman_environment.json` - Ambiente com variáveis configuráveis

## Como Importar

1. Abra o Postman
2. Clique em **Import** (canto superior esquerdo)
3. Selecione os arquivos:
   - `SISCAV_API.postman_collection.json`
   - `SISCAV_API.postman_environment.json`
4. Clique em **Import**

## Configuração Inicial

### 1. Configurar Ambiente

1. No Postman, selecione o ambiente **"SISCAV API - Local Development"** no canto superior direito
2. Verifique/ajuste a variável `base_url`:
   - **Local:** `http://localhost:8000`
   - **Produção:** `https://sua-api-producao.com`

### 2. Criar Usuário (se necessário)

Antes de fazer login, você precisa ter um usuário criado no banco de dados. Você pode criar manualmente ou usar um script Python:

```python
from apps.api.src.api.v1.core.security import get_password_hash
from apps.api.src.api.v1.models.user import User
from apps.api.src.api.v1.db.session import get_db

db = next(get_db())
user = User(
    email="test@example.com",
    hashed_password=get_password_hash("password123")
)
db.add(user)
db.commit()
```

### 3. Obter Token de Acesso

1. Execute a requisição **"Login - Obter Token"** na pasta **Autenticação**
2. O token será automaticamente salvo na variável `access_token`
3. Todos os endpoints protegidos usarão automaticamente este token

## Estrutura da Coleção

### Health & Status
- **Root - API Status**: Verifica se a API está online
- **Health Check**: Verificação de saúde da API

### Autenticação
- **Login - Obter Token**: Autentica e obtém token JWT
  - **Rate Limiting:** Máximo de 5 tentativas por minuto

### Whitelist - Placas Autorizadas
- **Listar Placas**: Lista todas as placas autorizadas (com paginação)
- **Criar Placa**: Adiciona nova placa à whitelist
- **Obter Placa por ID**: Busca placa específica
- **Atualizar Placa**: Atualiza dados de uma placa
- **Remover Placa**: Remove placa da whitelist

### Access Logs - Logs de Acesso
- **Registrar Acesso (IoT)**: Endpoint usado pelos dispositivos IoT
  - **Não requer autenticação**
  - Envia imagem e placa detectada
  - Retorna status (Authorized/Denied)
- **Listar Logs de Acesso**: Lista todos os logs (com filtros)
- **Listar Logs - Apenas Autorizados**: Filtra apenas acessos autorizados
- **Listar Logs - Filtrar por Placa**: Busca logs de uma placa específica
- **Obter Imagem do Log**: Retorna a imagem capturada

### Gate Control - Controle de Portão
- **Acionar Portão**: Aciona o portão remotamente

### Devices - Dispositivos IoT
- **Escanear Dispositivos Bluetooth**: Lista dispositivos disponíveis
- **Conectar Dispositivo Bluetooth**: Conecta a um dispositivo
- **Status da Conexão**: Verifica status da conexão
- **Desconectar Dispositivo**: Desconecta dispositivo atual

## Variáveis Automáticas

A coleção salva automaticamente os seguintes valores após requisições bem-sucedidas:

- `access_token`: Token JWT (após login)
- `plate_id`: ID da placa criada (após criar placa)
- `access_log_id`: ID do log criado (após registrar acesso)
- `image_filename`: Nome do arquivo de imagem (após registrar acesso)
- `connected_device_id`: ID do dispositivo conectado (após conectar)

## Exemplos de Uso

### Fluxo Completo de Teste

1. **Verificar API está online**
   - Execute: `Root - API Status`

2. **Fazer Login**
   - Execute: `Login - Obter Token`
   - Token será salvo automaticamente

3. **Criar uma placa autorizada**
   - Execute: `Criar Placa`
   - Use formato: `ABC-1234` ou `ABC1D23` (Mercosul)
   - ID será salvo automaticamente

4. **Registrar um acesso**
   - Execute: `Registrar Acesso (IoT)`
   - Selecione uma imagem (JPG, PNG)
   - Informe a placa detectada
   - Verifique o status retornado (Authorized/Denied)

5. **Visualizar logs**
   - Execute: `Listar Logs de Acesso`
   - Use filtros opcionais (status, placa, datas)

6. **Acionar portão**
   - Execute: `Acionar Portão`
   - Simula abertura remota do portão

## Formatos de Placa Aceitos

- **Formato Antigo:** `ABC1234` (3 letras + 4 dígitos)
- **Formato Mercosul:** `ABC1D23` (3 letras + 1 dígito + 1 letra + 2 dígitos)

A API normaliza automaticamente as placas (remove hífens e espaços, converte para maiúsculas).

## Troubleshooting

### Erro 401 (Unauthorized)
- Verifique se o token está válido
- Execute novamente o login para obter um novo token

### Erro 400 (Bad Request)
- Verifique o formato da placa
- Verifique se todos os campos obrigatórios foram preenchidos

### Erro 404 (Not Found)
- Verifique se o ID usado existe no banco de dados
- Verifique se a URL base está correta

### Rate Limit Excedido
- Aguarde 1 minuto antes de tentar novamente
- O limite é de 5 tentativas por minuto no endpoint de login

## Notas Importantes

- O endpoint **"Registrar Acesso (IoT)"** não requer autenticação, pois é usado pelos dispositivos IoT
- Todos os outros endpoints requerem autenticação via Bearer Token
- As imagens são armazenadas no diretório `uploads/` (configurável via `UPLOAD_DIR`)
- O tamanho máximo de arquivo é 10MB (configurável via `MAX_FILE_SIZE_MB`)

