# Script para testar a API SISCAV
$baseUrl = "http://localhost:8000"

Write-Host "=== Testando API SISCAV ===" -ForegroundColor Cyan
Write-Host ""

# 1. Endpoint raiz
Write-Host "1. GET /" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/" -Method Get
    Write-Host "   OK: $($response.message)" -ForegroundColor Green
} catch {
    Write-Host "   ERRO: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 2. Health check
Write-Host "2. GET /api/v1/health" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/health" -Method Get
    Write-Host "   OK: Status = $($response.status)" -ForegroundColor Green
} catch {
    Write-Host "   ERRO: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 3. Swagger UI
Write-Host "3. GET /docs (Swagger UI)" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/docs" -Method Get -UseBasicParsing
    Write-Host "   OK: Status Code = $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "   ERRO: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 4. Endpoint protegido sem token
Write-Host "4. GET /api/v1/whitelist/ (sem autenticacao)" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/whitelist/" -Method Get
    Write-Host "   ERRO: Deveria ter retornado 401!" -ForegroundColor Red
} catch {
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host "   OK: Retornou 401 Unauthorized (esperado)" -ForegroundColor Green
    } else {
        Write-Host "   ERRO: Retornou $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    }
}
Write-Host ""

# 5. Login com credenciais invalidas
Write-Host "5. POST /api/v1/login/access-token (credenciais invalidas)" -ForegroundColor Yellow
try {
    $loginBody = @{
        username = "inexistente@example.com"
        password = "senhaerrada"
    }
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/login/access-token" -Method Post -Body $loginBody -ContentType "application/x-www-form-urlencoded"
    Write-Host "   ERRO: Deveria ter retornado 401!" -ForegroundColor Red
} catch {
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host "   OK: Retornou 401 Unauthorized (esperado)" -ForegroundColor Green
    } else {
        Write-Host "   ERRO: Retornou $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    }
}
Write-Host ""

Write-Host "=== Resumo ===" -ForegroundColor Cyan
Write-Host "Endpoints publicos testados!" -ForegroundColor Green
Write-Host ""
Write-Host "Documentacao: $baseUrl/docs" -ForegroundColor Cyan


