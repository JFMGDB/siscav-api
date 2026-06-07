"""Centralized pt-BR error messages for client-facing API responses."""

# Auth & credentials
CREDENTIALS_INVALID = "Não foi possível validar as credenciais."
INVALID_ACCESS_TOKEN_TYPE = (
    "Tipo de token inválido. Use o token de acesso nas requisições autenticadas."
)
INVALID_USER_ID_IN_TOKEN = "Identificador de usuário inválido no token."
USER_NOT_FOUND = "Usuário não encontrado."
EMAIL_EMPTY = "Informe o e-mail."
PASSWORD_EMPTY = "Informe a senha."
INCORRECT_EMAIL_OR_PASSWORD = "E-mail ou senha inválidos."
EMAIL_ALREADY_REGISTERED = "Este e-mail já está registrado."
INVALID_DATA = "Dados inválidos. Verifique as informações enviadas."
REFRESH_TOKEN_EMPTY = "Informe o token de atualização."
REFRESH_TOKEN_INVALID = "Não foi possível validar o token de atualização."
INVALID_TOKEN_TYPE = "Tipo de token inválido."
INVALID_RESET_TOKEN = "Token de redefinição inválido ou expirado."
INVALID_USER_IN_RESET_TOKEN = "Usuário inválido no token de redefinição."
RESET_TOKEN_EMPTY = "Informe o token de redefinição."
PASSWORD_RESET_REQUESTED = (
    "Se existir uma conta com este e-mail, instruções de redefinição foram enviadas."
)
PASSWORD_RESET_SUCCESS = "Senha redefinida com sucesso."

# Authorization
PLATFORM_ADMIN_CLIENT_FORBIDDEN = (
    "Administradores da plataforma não podem acessar endpoints do cliente."
)
CLIENT_ADMIN_REQUIRED = "Privilégios de administrador do cliente são necessários."
SUPERADMIN_REQUIRED = "Privilégios de superadministrador são necessários."
CANNOT_DELETE_OWN_ACCOUNT = "Não é possível excluir a própria conta."
CANNOT_DELETE_LAST_SUPERADMIN = "Não é possível excluir o último superadministrador."

# Users
UPDATE_FIELD_REQUIRED = "Informe ao menos um campo (e-mail ou senha) para atualizar."

# Plates
PLATE_NOT_FOUND = "Placa não encontrada."
PLATE_ALREADY_EXISTS = "Esta placa já está na lista de autorizados."

# Access logs
ACCESS_LOG_NOT_FOUND = "Registro de acesso não encontrado."
ONLY_DENIED_LOG_WHITELIST = (
    "Somente registros de acesso negados podem ser autorizados por este endpoint."
)
FILE_MUST_BE_IMAGE = "Arquivo deve ser uma imagem."
FILE_TOO_LARGE = "Arquivo muito grande. Máximo: {max_mb} MB."
INVALID_FILENAME = "Nome de arquivo inválido."
IMAGE_NOT_FOUND = "Imagem não encontrada."

# ML
UNSUPPORTED_IMAGE_TYPE = "Tipo de arquivo não suportado. Use JPEG, PNG ou WebP."
IMAGE_EXCEEDS_MAX = "Imagem excede {max_mb} MB."
IMAGE_DECODE_FAILED = "Não foi possível decodificar a imagem."
OCR_UNAVAILABLE = "OCR indisponível: dependências ML não carregadas no servidor."
OCR_PROCESS_FAILED = "Falha ao processar OCR."
CLASSIFICATION_UNAVAILABLE = "Classificação veicular indisponível."
CLASSIFICATION_ONNX_UNAVAILABLE = (
    "Classificação veicular indisponível: instale as dependências ONNX "
    "(uv sync --extra onnx) e reinicie o servidor."
)
CLASSIFICATION_PROCESS_FAILED = "Falha ao processar a classificação veicular."

# Common
INTERNAL_SERVER_ERROR = "Erro interno do servidor. Tente novamente mais tarde."
DATABASE_ERROR_CREATING_USER = "Erro ao salvar usuário. Tente novamente mais tarde."
ERROR_CREATING_USER = "Erro ao criar usuário. Tente novamente mais tarde."
DATABASE_CONFIG_ERROR = (
    "Erro de configuração do banco de dados. Verifique a instalação."
)
DATABASE_CONNECTION_ERROR = (
    "Erro de conexão com o banco de dados. Verifique a configuração."
)
PLATE_CREATE_INTERNAL_ERROR = "Erro interno ao criar placa autorizada."
RATE_LIMIT_EXCEEDED = "Muitas tentativas. Aguarde 1 minuto antes de tentar novamente."
