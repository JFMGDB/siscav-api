# Script para testar a API SISCAV com curl
# Uso: .\test_api.ps1

$baseUrl = "http://localhost:8000"
$token = $null

Write-Host "=== Testando API SISCAV ===" -ForegroundColor Cyan
Write-Host ""

# 1. Teste do endpoint raiz
Write-Host "1. Testando endpoint raiz (GET /)" -ForegroundColor Yellow
$response = curl.exe -s -X GET "$baseUrl/" -H "Accept: application/json"
Write-Host "Resposta: $response" -ForegroundColor Green
Write-Host ""

# 2. Teste do health check
Write-Host "2. Testando health check (GET /api/v1/health)" -ForegroundColor Yellow
$response = curl.exe -s -X GET "$baseUrl/api/v1/health" -H "Accept: application/json"
Write-Host "Resposta: $response" -ForegroundColor Green
Write-Host ""

# 3. Teste de registro de usuário
Write-Host "3. Testando registro de usuário (POST /api/v1/register)" -ForegroundColor Yellow
$email = "teste_$(Get-Random)@example.com"
$password = "teste123456"
$body = "{`"email`":`"$email`",`"password`":`"$password`"}"

$response = curl.exe -s -X POST "$baseUrl/api/v1/register" `
    -H "Content-Type: application/json" `
    -d $body
Write-Host "Resposta: $response" -ForegroundColor Green
Write-Host "Email criado: $email" -ForegroundColor Gray
Write-Host ""

# 4. Teste de login
Write-Host "4. Testando login (POST /api/v1/login/access-token)" -ForegroundColor Yellow
$loginData = "username=$email&password=$password"
$response = curl.exe -s -X POST "$baseUrl/api/v1/login/access-token" `
    -H "Content-Type: application/x-www-form-urlencoded" `
    -d $loginData

Write-Host "Resposta: $response" -ForegroundColor Green

# Extrair token
if ($response -match '"access_token":"([^"]+)"') {
    $token = $matches[1]
    Write-Host "Token obtido com sucesso!" -ForegroundColor Green
} else {
    Write-Host "ERRO: Não foi possível obter o token" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 5. Teste de listar whitelist (requer autenticação)
Write-Host "5. Testando listar whitelist (GET /api/v1/whitelist/)" -ForegroundColor Yellow
$response = curl.exe -s -X GET "$baseUrl/api/v1/whitelist/" `
    -H "Authorization: Bearer $token" `
    -H "Accept: application/json"
Write-Host "Resposta: $response" -ForegroundColor Green
Write-Host ""

# 6. Teste de criar placa na whitelist
Write-Host "6. Testando criar placa na whitelist (POST /api/v1/whitelist/)" -ForegroundColor Yellow
$plateBody = "{`"plate`":`"ABC-1234`",`"description`":`"Veículo de teste`"}"

$response = curl.exe -s -X POST "$baseUrl/api/v1/whitelist/" `
    -H "Authorization: Bearer $token" `
    -H "Content-Type: application/json" `
    -d $plateBody
Write-Host "Resposta: $response" -ForegroundColor Green
Write-Host ""

# 7. Teste de listar access logs
Write-Host "7. Testando listar access logs (GET /api/v1/access_logs/)" -ForegroundColor Yellow
$response = curl.exe -s -X GET "$baseUrl/api/v1/access_logs/" `
    -H "Authorization: Bearer $token" `
    -H "Accept: application/json"
Write-Host "Resposta: $response" -ForegroundColor Green
Write-Host ""

# 8. Teste de status de dispositivos
Write-Host "8. Testando status de dispositivos (GET /api/v1/devices/status)" -ForegroundColor Yellow
$response = curl.exe -s -X GET "$baseUrl/api/v1/devices/status" `
    -H "Authorization: Bearer $token" `
    -H "Accept: application/json"
Write-Host "Resposta: $response" -ForegroundColor Green
Write-Host ""

# 9. Teste de acionar portão
Write-Host "9. Testando acionar portão (POST /api/v1/gate_control/trigger)" -ForegroundColor Yellow
$response = curl.exe -s -X POST "$baseUrl/api/v1/gate_control/trigger" `
    -H "Authorization: Bearer $token" `
    -H "Accept: application/json"
Write-Host "Resposta: $response" -ForegroundColor Green
Write-Host ""

# 10. Teste sem autenticação (deve falhar)
Write-Host "10. Testando acesso sem autenticação (deve retornar 401)" -ForegroundColor Yellow
$response = curl.exe -s -w "`nHTTP Status: %{http_code}`n" -X GET "$baseUrl/api/v1/whitelist/" `
    -H "Accept: application/json"
Write-Host "Resposta: $response" -ForegroundColor $(if ($response -match "401") { "Green" } else { "Red" })
Write-Host ""

Write-Host "=== Testes concluídos ===" -ForegroundColor Cyan

