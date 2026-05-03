# Script para testar a API SISCAV usando Invoke-RestMethod
# Uso: .\test_api_rest.ps1

$baseUrl = "http://localhost:8000"
$token = $null

Write-Host "=== Testando API SISCAV ===" -ForegroundColor Cyan
Write-Host ""

# 1. Teste do endpoint raiz
Write-Host "1. Testando endpoint raiz (GET /)" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/" -Method Get -ContentType "application/json"
    Write-Host "Resposta: $($response | ConvertTo-Json)" -ForegroundColor Green
} catch {
    Write-Host "ERRO: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 2. Teste do health check
Write-Host "2. Testando health check (GET /api/v1/health)" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/health" -Method Get -ContentType "application/json"
    Write-Host "Resposta: $($response | ConvertTo-Json)" -ForegroundColor Green
} catch {
    Write-Host "ERRO: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 3. Teste de registro de usuário
Write-Host "3. Testando registro de usuário (POST /api/v1/register)" -ForegroundColor Yellow
$email = "teste_$(Get-Random)@example.com"
$password = "teste123456"
$body = @{
    email = $email
    password = $password
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/register" -Method Post -Body $body -ContentType "application/json"
    Write-Host "Resposta: $($response | ConvertTo-Json)" -ForegroundColor Green
    Write-Host "Email criado: $email" -ForegroundColor Gray
} catch {
    Write-Host "ERRO: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Detalhes: $responseBody" -ForegroundColor Red
    }
}
Write-Host ""

# 4. Teste de login
Write-Host "4. Testando login (POST /api/v1/login/access-token)" -ForegroundColor Yellow
$loginBody = @{
    username = $email
    password = $password
}

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/login/access-token" -Method Post -Body $loginBody -ContentType "application/x-www-form-urlencoded"
    $token = $response.access_token
    Write-Host "Token obtido com sucesso!" -ForegroundColor Green
    Write-Host "Access Token: $($token.Substring(0, [Math]::Min(50, $token.Length)))..." -ForegroundColor Gray
} catch {
    Write-Host "ERRO: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Detalhes: $responseBody" -ForegroundColor Red
    }
    Write-Host "Tentando com usuário existente..." -ForegroundColor Yellow
    
    # Tentar com um usuário que pode já existir
    $loginBody = @{
        username = "teste@example.com"
        password = "teste123456"
    }
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/login/access-token" -Method Post -Body $loginBody -ContentType "application/x-www-form-urlencoded"
        $token = $response.access_token
        Write-Host "Token obtido com usuário existente!" -ForegroundColor Green
    } catch {
        Write-Host "ERRO: Não foi possível fazer login" -ForegroundColor Red
        exit 1
    }
}
Write-Host ""

if (-not $token) {
    Write-Host "ERRO: Não foi possível obter token. Abortando testes que requerem autenticação." -ForegroundColor Red
    exit 1
}

# 5. Teste de listar whitelist (requer autenticação)
Write-Host "5. Testando listar whitelist (GET /api/v1/whitelist/)" -ForegroundColor Yellow
try {
    $headers = @{
        "Authorization" = "Bearer $token"
    }
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/whitelist/" -Method Get -Headers $headers -ContentType "application/json"
    Write-Host "Resposta: $($response | ConvertTo-Json -Depth 3)" -ForegroundColor Green
} catch {
    Write-Host "ERRO: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 6. Teste de criar placa na whitelist
Write-Host "6. Testando criar placa na whitelist (POST /api/v1/whitelist/)" -ForegroundColor Yellow
$plateBody = @{
    plate = "XYZ-9876"
    description = "Veículo de teste via API"
} | ConvertTo-Json

try {
    $headers = @{
        "Authorization" = "Bearer $token"
    }
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/whitelist/" -Method Post -Body $plateBody -Headers $headers -ContentType "application/json"
    Write-Host "Resposta: $($response | ConvertTo-Json)" -ForegroundColor Green
    $plateId = $response.id
} catch {
    Write-Host "ERRO: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Detalhes: $responseBody" -ForegroundColor Red
    }
}
Write-Host ""

# 7. Teste de listar access logs
Write-Host "7. Testando listar access logs (GET /api/v1/access_logs/)" -ForegroundColor Yellow
try {
    $headers = @{
        "Authorization" = "Bearer $token"
    }
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/access_logs/" -Method Get -Headers $headers -ContentType "application/json"
    Write-Host "Total de logs: $($response.Count)" -ForegroundColor Green
    if ($response.Count -gt 0) {
        Write-Host "Primeiro log: $($response[0] | ConvertTo-Json -Depth 2)" -ForegroundColor Gray
    }
} catch {
    Write-Host "ERRO: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 8. Teste de status de dispositivos
Write-Host "8. Testando status de dispositivos (GET /api/v1/devices/status)" -ForegroundColor Yellow
try {
    $headers = @{
        "Authorization" = "Bearer $token"
    }
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/devices/status" -Method Get -Headers $headers -ContentType "application/json"
    Write-Host "Resposta: $($response | ConvertTo-Json)" -ForegroundColor Green
} catch {
    Write-Host "ERRO: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 9. Teste de acionar portão
Write-Host "9. Testando acionar portão (POST /api/v1/gate_control/trigger)" -ForegroundColor Yellow
try {
    $headers = @{
        "Authorization" = "Bearer $token"
    }
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/gate_control/trigger" -Method Post -Headers $headers -ContentType "application/json"
    Write-Host "Resposta: $($response | ConvertTo-Json)" -ForegroundColor Green
} catch {
    Write-Host "ERRO: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 10. Teste sem autenticação (deve falhar)
Write-Host "10. Testando acesso sem autenticação (deve retornar 401)" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/whitelist/" -Method Get -ContentType "application/json"
    Write-Host "ERRO: Deveria ter falhado!" -ForegroundColor Red
} catch {
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host "SUCESSO: Retornou 401 Unauthorized como esperado" -ForegroundColor Green
    } else {
        Write-Host "ERRO: Retornou $($_.Exception.Response.StatusCode) em vez de 401" -ForegroundColor Red
    }
}
Write-Host ""

Write-Host "=== Testes concluídos ===" -ForegroundColor Cyan


