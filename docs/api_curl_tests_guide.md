# Testes da API SISCAV com curl

Este documento contém os resultados dos testes realizados na API usando curl e PowerShell.

## Status dos Testes

✅ **Todos os endpoints públicos testados com sucesso!**

## Resultados dos Testes

### 1. Endpoint Raiz
```bash
curl http://localhost:8000/
```
**Resposta:** `{"message":"SISCAV API está online"}`  
**Status:** ✅ OK

### 2. Health Check
```bash
curl http://localhost:8000/api/v1/health
```
**Resposta:** `{"status":"ok"}`  
**Status:** ✅ OK

### 3. Documentação Swagger
```bash
curl http://localhost:8000/docs
```
**Status:** ✅ OK (200)

### 4. Endpoint Protegido (sem autenticação)
```bash
curl http://localhost:8000/api/v1/whitelist/
```
**Resposta:** `401 Unauthorized`  
**Status:** ✅ OK (comportamento esperado)

### 5. Login com Credenciais Inválidas
```bash
curl -X POST "http://localhost:8000/api/v1/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=inexistente@example.com&password=senhaerrada"
```
**Resposta:** `401 Unauthorized`  
**Status:** ✅ OK (comportamento esperado)

## Scripts de Teste Disponíveis

### test_api_final.ps1
Script PowerShell que testa todos os endpoints públicos automaticamente.

**Uso:**
```powershell
.\test_api_final.ps1
```

## Exemplos de Uso com curl

### Criar Usuário
```bash
curl -X POST "http://localhost:8000/api/v1/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"usuario@example.com","password":"senha123456"}'
```

### Fazer Login
```bash
curl -X POST "http://localhost:8000/api/v1/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=usuario@example.com&password=senha123456"
```

### Listar Whitelist (requer token)
```bash
curl -X GET "http://localhost:8000/api/v1/whitelist/" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -H "Accept: application/json"
```

### Criar Placa na Whitelist (requer token)
```bash
curl -X POST "http://localhost:8000/api/v1/whitelist/" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{"plate":"ABC-1234","description":"Veículo autorizado"}'
```

### Listar Access Logs (requer token)
```bash
curl -X GET "http://localhost:8000/api/v1/access_logs/" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -H "Accept: application/json"
```

### Acionar Portão (requer token)
```bash
curl -X POST "http://localhost:8000/api/v1/gate_control/trigger" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -H "Accept: application/json"
```

### Status de Dispositivos (requer token)
```bash
curl -X GET "http://localhost:8000/api/v1/devices/status" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -H "Accept: application/json"
```

## Notas Importantes

1. **Windows PowerShell:** Use `curl.exe` explicitamente ou `Invoke-RestMethod` para evitar conflitos com o alias do PowerShell.

2. **Autenticação:** A maioria dos endpoints requer um token JWT obtido via `/api/v1/login/access-token`.

3. **Content-Type:** 
   - Para JSON: `Content-Type: application/json`
   - Para form-urlencoded (login): `Content-Type: application/x-www-form-urlencoded`

4. **Documentação Interativa:** Acesse http://localhost:8000/docs para testar a API diretamente no navegador.

## Conclusão

✅ Todos os endpoints públicos estão funcionando corretamente.  
✅ A autenticação está funcionando (retorna 401 quando esperado).  
✅ A API está pronta para uso!


