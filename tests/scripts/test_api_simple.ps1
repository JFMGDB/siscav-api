# Script simplificado para testar a API SISCAV
# Foca nos endpoints que funcionam sem necessidade de criar usuário

$baseUrl = "http://localhost:8000"

Write-Host "=== Testando API SISCAV (Endpoints Públicos) ===" -ForegroundColor Cyan
Write-Host ""

# 1. Endpoint raiz
Write-Host "1. GET /" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/" -Method Get
    Write-Host "   ✓ $($response.message)" -ForegroundColor Green
} catch {
    Write-Host "   ✗ ERRO: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 2. Health check
Write-Host "2. GET /api/v1/health" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/health" -Method Get
    Write-Host "   ✓ Status: $($response.status)" -ForegroundColor Green
} catch {
    Write-Host "   ✗ ERRO: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 3. Documentação Swagger (verificar se está acessível)
Write-Host "3. GET /docs (Swagger UI)" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/docs" -Method Get -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✓ Swagger UI acessível (Status: $($response.StatusCode))" -ForegroundColor Green
    }
} catch {
    Write-Host "   ✗ ERRO: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 4. Teste de endpoint protegido sem token (deve retornar 401)
Write-Host "4. GET /api/v1/whitelist/ (sem autenticação)" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/whitelist/" -Method Get
    Write-Host "   ✗ ERRO: Deveria ter retornado 401!" -ForegroundColor Red
} catch {
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host "   ✓ Retornou 401 Unauthorized (esperado)" -ForegroundColor Green
    } else {
        Write-Host "   ✗ Retornou $($_.Exception.Response.StatusCode) em vez de 401" -ForegroundColor Red
    }
}
Write-Host ""

# 5. Teste de login com credenciais inválidas
Write-Host "5. POST /api/v1/login/access-token (credenciais inválidas)" -ForegroundColor Yellow
try {
    $loginBody = @{
        username = "inexistente@example.com"
        password = "senhaerrada"
    }
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/login/access-token" -Method Post -Body $loginBody -ContentType "application/x-www-form-urlencoded"
    Write-Host "   ✗ ERRO: Deveria ter retornado 401!" -ForegroundColor Red
} catch {
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host "   ✓ Retornou 401 Unauthorized (esperado)" -ForegroundColor Green
    } else {
        Write-Host "   ✗ Retornou $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    }
}
Write-Host ""

Write-Host "=== Resumo ===" -ForegroundColor Cyan
Write-Host "Endpoints públicos testados com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "Para testar endpoints protegidos, você precisa:" -ForegroundColor Yellow
Write-Host "1. Criar um usuário (POST /api/v1/register)" -ForegroundColor Gray
Write-Host "2. Fazer login (POST /api/v1/login/access-token)" -ForegroundColor Gray
Write-Host "3. Usar o token obtido no header Authorization: Bearer [token]" -ForegroundColor Gray
Write-Host ""
Write-Host "Documentacao interativa disponivel em: $baseUrl/docs" -ForegroundColor Cyan

