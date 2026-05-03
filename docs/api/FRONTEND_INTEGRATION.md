# Documentação de Integração - Frontend (autenticação e API)

Esta documentação descreve como integrar **autenticação JWT** e **recursos da API** usados pelo frontend (incluindo **OCR de placa no servidor** para o posto do operador).

## Índice

1. [Visão Geral](#visão-geral)
2. [OCR de placa no servidor (operador)](#ocr-de-placa-no-servidor-operador)
3. [Endpoints de Autenticação](#endpoints-de-autenticação)
4. [Fluxo de Autenticação](#fluxo-de-autenticação)
5. [Gerenciamento de Tokens](#gerenciamento-de-tokens)
6. [Exemplos de Implementação](#exemplos-de-implementação)
7. [Tratamento de Erros](#tratamento-de-erros)
8. [Segurança](#segurança)

## Visão Geral

A API SISCAV utiliza autenticação baseada em JWT (JSON Web Tokens) com dois tipos de tokens:

- **Access Token**: Token de acesso de curta duração (15 minutos por padrão)
- **Refresh Token**: Token de renovação de longa duração (30 dias por padrão)

### Configurações Padrão

- **Access Token Expiração**: 15 minutos (configurável via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- **Refresh Token Expiração**: 30 dias (configurável via `REFRESH_TOKEN_EXPIRE_DAYS`)
- **Rate Limiting**: 5 tentativas de login por minuto por IP

## Pré-visualização de câmara (operador — Next.js)

A interface para **ligar câmara por USB ou por URL (Wi‑Fi / IP)** e ver **vídeo em tempo real** é implementada num **repositório separado** com **Next.js** e **TypeScript**. O fluxo de vídeo é sobretudo **no browser** (por exemplo `getUserMedia` para USB, ou `<img>`/`<video>` para streams MJPEG/HLS); **não** depende de endpoints de streaming nesta API.

- **Guia completo (implementação no repo frontend):** [camera-preview-nextjs.md](../frontend/camera-preview-nextjs.md)
- **Índice `docs/frontend/`:** [README.md](../frontend/README.md)

A **autenticação** do operador contra esta API (registo, login, refresh, `Authorization: Bearer`) segue as secções abaixo neste documento. A pré-visualização em si **não** exige JWT.

**OCR no servidor** (`POST /api/v1/ml/recognize-plate`) **exige JWT** — ver secção seguinte.

Em desenvolvimento, a API já permite origem Next.js em `http://localhost:3000` — ver `CORSMiddleware` em `apps/api/src/main.py`.

## OCR de placa no servidor (operador)

O frontend pode enviar um **frame ou recorte** (JPEG, PNG ou WebP) para a API executar deteção de regiões + **EasyOCR** (mesma família de lógica que o script em `apps/api/src/api/v1/ml/recognize-plate.py`). O resultado é uma **lista de candidatos** com texto de 7 caracteres alfanuméricos; o operador pode escolher um valor e depois registar acesso com `POST /api/v1/access_logs/` (ou outro fluxo da vossa UI).

### Pré-requisito no servidor

A rota só funciona se o ambiente tiver as dependências ML instaladas:

```bash
pip install -r requirements-ml.txt
```

Sem isso, a API responde **503** com mensagem a indicar a instalação. O arranque normal da API **não** exige estes pacotes.

### Endpoint

| Método | Caminho | Autenticação |
|--------|---------|--------------|
| `POST` | `/api/v1/ml/recognize-plate` | `Authorization: Bearer {access_token}` |

### Pedido

- **Content-Type:** `multipart/form-data`
- **Campo do ficheiro:** `file` (nome exato esperado pelo FastAPI `UploadFile`)
- **Tipos MIME aceites:** `image/jpeg`, `image/jpg`, `image/png`, `image/webp`
- **Tamanho máximo:** `MAX_FILE_SIZE_MB` (variável de ambiente; predefinição **10** MB), igual à política usada noutros uploads da API

### Resposta de sucesso (200)

```json
{
  "candidates": [
    {
      "plate_raw": "ABC1D23",
      "normalized_plate": "ABC1D23",
      "plate_color_hint": "branca"
    }
  ]
}
```

- `candidates` pode ser uma lista **vazia** se nenhuma região válida for encontrada.
- `plate_color_hint` é heurística (`branca`, `amarela`, `cinza`, `desconhecida`).
- `normalized_plate` segue `normalize_plate()` (alfanumérico em maiúsculas), útil para comparar com a whitelist no cliente ou antes de submeter o log.

### Erros relevantes

| HTTP | Situação |
|------|----------|
| **401** | Sem `Authorization` ou token inválido |
| **400** | Tipo de ficheiro não suportado ou imagem que o OpenCV não consegue decodificar |
| **413** | Ficheiro acima do limite configurado |
| **503** | Stack ML não instalada ou indisponível |
| **500** | Falha interna no pipeline OCR |

### Exemplo TypeScript (fetch + FormData)

```typescript
const baseUrl = process.env.NEXT_PUBLIC_SISCAV_API_URL ?? 'http://127.0.0.1:8000';

/** Blob a partir de um <canvas> (frame do vídeo) — qualidade JPEG ajustável */
export async function canvasToJpegBlob(canvas: HTMLCanvasElement, quality = 0.92): Promise<Blob> {
  return new Promise((resolve, reject) => {
    canvas.toBlob(
      (b) => (b ? resolve(b) : reject(new Error('toBlob falhou'))),
      'image/jpeg',
      quality
    );
  });
}

export type PlateCandidate = {
  plate_raw: string;
  normalized_plate: string;
  plate_color_hint: string;
};

export type RecognizePlateResponse = {
  candidates: PlateCandidate[];
};

export async function recognizePlateFromImage(
  accessToken: string,
  imageBlob: Blob,
  fileName = 'frame.jpg'
): Promise<RecognizePlateResponse> {
  const form = new FormData();
  form.append('file', imageBlob, fileName);

  const res = await fetch(`${baseUrl}/api/v1/ml/recognize-plate`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
    body: form,
  });

  if (res.status === 503) {
    throw new Error('OCR não disponível no servidor (instalar requirements-ml.txt).');
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(typeof err.detail === 'string' ? err.detail : `HTTP ${res.status}`);
  }

  return res.json();
}
```

Fluxo típico: **login** → capturar frame (por exemplo `drawImage` de `<video>` para `<canvas>`) → `canvasToJpegBlob` → `recognizePlateFromImage` → mostrar candidatos ao operador → confirmar e chamar `POST /api/v1/access_logs/` com a placa escolhida (e imagem, se aplicável). Detalhes de câmara USB / URL: [camera-preview-nextjs.md](../frontend/camera-preview-nextjs.md).

### Documentação interativa

No servidor em execução: tag **`ml`** em [Swagger UI](http://127.0.0.1:8000/docs) ou ReDoc.

## Endpoints de Autenticação

### 1. Registrar - Criar Conta

**Endpoint:** `POST /api/v1/register`

**Descrição:** Cria uma nova conta de usuário no sistema.

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "email": "usuario@example.com",
  "password": "senha123456"
}
```

**Resposta de Sucesso (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "usuario@example.com",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

**Respostas de Erro:**

- **400 Bad Request**: Email inválido ou senha com menos de 8 caracteres
- **409 Conflict**: Email já está registrado
- **429 Too Many Requests**: Rate limit excedido (3 tentativas/minuto)

**Validações:**
- Email deve ser válido (formato email)
- Senha deve ter no mínimo 8 caracteres
- Email deve ser único no sistema

### 2. Login - Obter Tokens

**Endpoint:** `POST /api/v1/login/access-token`

**Descrição:** Autentica o usuário e retorna um par de tokens (access e refresh).

**Headers:**
```
Content-Type: application/x-www-form-urlencoded
```

**Body (form-data):**
```
username: string (email do usuário)
password: string (senha do usuário)
```

**Resposta de Sucesso (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Respostas de Erro:**

- **400 Bad Request**: Email ou senha vazios
- **401 Unauthorized**: Credenciais inválidas
- **429 Too Many Requests**: Rate limit excedido (5 tentativas/minuto)

### 3. Refresh Token - Renovar Tokens

**Endpoint:** `POST /api/v1/login/refresh-token`

**Descrição:** Renova os tokens usando um refresh token válido.

**Headers:**
```
Content-Type: application/x-www-form-urlencoded
```

**Body (form-data):**
```
refresh_token: string (refresh token obtido no login)
```

**Resposta de Sucesso (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Respostas de Erro:**

- **400 Bad Request**: Refresh token vazio
- **403 Forbidden**: Refresh token inválido, expirado ou tipo incorreto
- **404 Not Found**: Usuário não encontrado

## Fluxo de Autenticação

### Fluxo de Registro

```
1. Usuário insere email e senha
2. Frontend valida formato de email e tamanho mínimo da senha
3. Frontend envia POST /api/v1/register
4. API valida dados e verifica se email já existe
5. API cria usuário e retorna dados (sem senha)
6. Frontend pode redirecionar para login ou fazer login automático
```

### Fluxo Inicial (Login)

```
1. Usuário insere email e senha
2. Frontend envia POST /api/v1/login/access-token
3. API valida credenciais
4. API retorna access_token e refresh_token
5. Frontend armazena ambos os tokens (localStorage/sessionStorage)
6. Frontend usa access_token em requisições subsequentes
```

### Fluxo de Renovação (Refresh)

```
1. Access token expira (ou está próximo de expirar)
2. Frontend detecta token expirado (401/403)
3. Frontend envia POST /api/v1/login/refresh-token com refresh_token
4. API valida refresh_token
5. API retorna novos access_token e refresh_token
6. Frontend atualiza tokens armazenados
7. Frontend repete requisição original com novo access_token
```

### Fluxo de Logout

```
1. Usuário solicita logout
2. Frontend remove tokens do armazenamento
3. Frontend redireciona para página de login
```

## Gerenciamento de Tokens

### Armazenamento

**Recomendações:**

- **Access Token**: Armazenar em memória (variável JavaScript) ou sessionStorage
- **Refresh Token**: Armazenar em localStorage ou httpOnly cookie (mais seguro)

**⚠️ Importante:** Nunca armazene tokens em cookies não-httpOnly ou em locais facilmente acessíveis via JavaScript, especialmente em produção.

### Envio em Requisições

Todos os endpoints protegidos requerem o access token no header Authorization:

```
Authorization: Bearer {access_token}
```

### Validação e Renovação Automática

Implemente um interceptor/middleware que:

1. Intercepta todas as requisições HTTP
2. Adiciona o access_token no header Authorization
3. Intercepta respostas 401/403
4. Tenta renovar tokens automaticamente
5. Repete a requisição original com novo token

## Exemplos de Implementação

### JavaScript/TypeScript (Fetch API)

```typescript
// auth.service.ts
class AuthService {
  private baseUrl = 'http://localhost:8000/api/v1';
  private accessToken: string | null = null;
  private refreshToken: string | null = null;

  // Registrar novo usuário
  async register(email: string, password: string): Promise<{ id: string; email: string }> {
    const response = await fetch(`${this.baseUrl}/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      if (response.status === 409) {
        throw new Error('Email já está registrado');
      }
      if (response.status === 429) {
        throw new Error('Muitas tentativas. Aguarde 1 minuto.');
      }
      if (response.status === 400) {
        const error = await response.json();
        throw new Error(error.detail || 'Dados inválidos');
      }
      throw new Error('Erro ao criar conta');
    }

    return await response.json();
  }

  // Login
  async login(email: string, password: string): Promise<void> {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch(`${this.baseUrl}/login/access-token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('Credenciais inválidas');
      }
      if (response.status === 429) {
        throw new Error('Muitas tentativas. Aguarde 1 minuto.');
      }
      throw new Error('Erro ao fazer login');
    }

    const data = await response.json();
    this.accessToken = data.access_token;
    this.refreshToken = data.refresh_token;
    
    // Armazenar tokens
    localStorage.setItem('refresh_token', data.refresh_token);
    sessionStorage.setItem('access_token', data.access_token);
  }

  // Refresh Token
  async refreshTokens(): Promise<void> {
    const storedRefreshToken = localStorage.getItem('refresh_token');
    
    if (!storedRefreshToken) {
      throw new Error('Refresh token não encontrado');
    }

    const formData = new URLSearchParams();
    formData.append('refresh_token', storedRefreshToken);

    const response = await fetch(`${this.baseUrl}/login/refresh-token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });

    if (!response.ok) {
      // Refresh token expirado, fazer logout
      this.logout();
      throw new Error('Sessão expirada. Faça login novamente.');
    }

    const data = await response.json();
    this.accessToken = data.access_token;
    this.refreshToken = data.refresh_token;
    
    localStorage.setItem('refresh_token', data.refresh_token);
    sessionStorage.setItem('access_token', data.access_token);
  }

  // Logout
  logout(): void {
    this.accessToken = null;
    this.refreshToken = null;
    localStorage.removeItem('refresh_token');
    sessionStorage.removeItem('access_token');
  }

  // Obter access token
  getAccessToken(): string | null {
    return this.accessToken || sessionStorage.getItem('access_token');
  }

  // Fazer requisição autenticada
  async authenticatedFetch(url: string, options: RequestInit = {}): Promise<Response> {
    const token = this.getAccessToken();
    
    if (!token) {
      throw new Error('Não autenticado');
    }

    const headers = {
      ...options.headers,
      'Authorization': `Bearer ${token}`,
    };

    let response = await fetch(url, { ...options, headers });

    // Se token expirado, tentar renovar
    if (response.status === 401 || response.status === 403) {
      try {
        await this.refreshTokens();
        const newToken = this.getAccessToken();
        headers['Authorization'] = `Bearer ${newToken}`;
        response = await fetch(url, { ...options, headers });
      } catch (error) {
        this.logout();
        throw error;
      }
    }

    return response;
  }
}

export const authService = new AuthService();
```

### React Hook Example

```typescript
// useAuth.ts
import { useState, useEffect, useCallback } from 'react';
import { authService } from './auth.service';

export function useAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Verificar se há tokens armazenados
    const accessToken = authService.getAccessToken();
    setIsAuthenticated(!!accessToken);
    setIsLoading(false);
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    try {
      await authService.login(email, password);
      setIsAuthenticated(true);
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error instanceof Error ? error.message : 'Erro ao fazer login' 
      };
    }
  }, []);

  const logout = useCallback(() => {
    authService.logout();
    setIsAuthenticated(false);
  }, []);

  return {
    isAuthenticated,
    isLoading,
    login,
    logout,
  };
}
```

### Axios Interceptor Example

```typescript
// api.client.ts
import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { authService } from './auth.service';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
});

// Interceptor para adicionar token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = authService.getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para renovar token automaticamente
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // Se erro 401/403 e ainda não tentou renovar
    if (
      (error.response?.status === 401 || error.response?.status === 403) &&
      !originalRequest._retry
    ) {
      originalRequest._retry = true;

      try {
        await authService.refreshTokens();
        const newToken = authService.getAccessToken();
        
        if (newToken && originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        authService.logout();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
```

## Tratamento de Erros

### Códigos de Status HTTP

| Código | Significado | Ação Recomendada |
|--------|-------------|------------------|
| 200 | Sucesso | Continuar normalmente |
| 400 | Bad Request | Validar dados enviados |
| 401 | Unauthorized | Credenciais inválidas ou token expirado |
| 403 | Forbidden | Token inválido ou tipo incorreto |
| 404 | Not Found | Recurso não encontrado |
| 413 | Content Too Large | Ficheiro acima do limite (ex.: OCR / uploads) |
| 429 | Too Many Requests | Aguardar antes de tentar novamente |
| 503 | Service Unavailable | OCR: dependências ML não instaladas no servidor |

### Mensagens de Erro

```typescript
interface ApiError {
  detail: string;
}

// Exemplo de tratamento
try {
  await authService.login(email, password);
} catch (error) {
  if (error instanceof Error) {
    switch (error.message) {
      case 'Credenciais inválidas':
        // Mostrar mensagem ao usuário
        break;
      case 'Muitas tentativas. Aguarde 1 minuto.':
        // Mostrar contador de espera
        break;
      default:
        // Erro genérico
    }
  }
}
```

## Segurança

### Boas Práticas

1. **HTTPS em Produção**: Sempre use HTTPS em produção para proteger tokens em trânsito
2. **Armazenamento Seguro**: Prefira httpOnly cookies para refresh tokens
3. **Validação de Token**: Valide expiração do token antes de fazer requisições
4. **Logout Automático**: Implemente logout automático quando refresh token expirar
5. **Rate Limiting**: Respeite o rate limiting do servidor (5 tentativas/minuto)
6. **XSS Protection**: Sanitize inputs para prevenir XSS attacks
7. **CSRF Protection**: Implemente proteção CSRF se usar cookies

### Validação de Expiração (Opcional)

```typescript
// Decodificar JWT sem verificar assinatura (apenas para ler exp)
function getTokenExpiration(token: string): number | null {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.exp * 1000; // Converter para milissegundos
  } catch {
    return null;
  }
}

function isTokenExpired(token: string): boolean {
  const expiration = getTokenExpiration(token);
  if (!expiration) return true;
  
  // Considerar expirado se faltar menos de 1 minuto
  return Date.now() >= (expiration - 60000);
}

// Usar antes de fazer requisições
if (isTokenExpired(accessToken)) {
  await authService.refreshTokens();
}
```

## Exemplo Completo - React Component

```typescript
// LoginForm.tsx
import React, { useState } from 'react';
import { useAuth } from './useAuth';

export function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    const result = await login(email, password);
    
    if (!result.success) {
      setError(result.error || 'Erro ao fazer login');
    } else {
      // Redirecionar para dashboard
      window.location.href = '/dashboard';
    }
    
    setIsLoading(false);
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Email:</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
      </div>
      <div>
        <label>Senha:</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </div>
      {error && <div className="error">{error}</div>}
      <button type="submit" disabled={isLoading}>
        {isLoading ? 'Entrando...' : 'Entrar'}
      </button>
    </form>
  );
}
```

## Resumo

1. **Registro**: Use `POST /api/v1/register` para criar nova conta (email e senha)
2. **Login**: Use `POST /api/v1/login/access-token` com email e senha
3. **Armazenamento**: Guarde access_token e refresh_token de forma segura
4. **Requisições**: Inclua `Authorization: Bearer {access_token}` em todas as requisições protegidas
5. **OCR (operador)**: `POST /api/v1/ml/recognize-plate` com `multipart/form-data` campo `file` — requer JWT e `requirements-ml.txt` no servidor
6. **Renovação**: Use `POST /api/v1/login/refresh-token` quando access_token expirar
7. **Erros**: Trate 401/403 renovando tokens ou fazendo logout; trate 503 no OCR conforme mensagem do servidor
8. **Segurança**: Use HTTPS, valide tokens e implemente proteções adequadas

## Suporte

Para dúvidas ou problemas, consulte:
- Documentação técnica: `apps/api/docs/technical-documentation.md`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

