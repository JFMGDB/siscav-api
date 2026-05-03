# Script para testar todos os endpoints e identificar erros 500
$baseUrl = "http://localhost:8000"
$token = $null
$results = @()

Write-Host "=== Testando TODOS os Endpoints da API ===" -ForegroundColor Cyan
Write-Host ""

# 1. Endpoint raiz
Write-Host "1. GET /" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/" -Method Get
    $results += [PSCustomObject]@{Endpoint="GET /"; Status="OK"; Details=$response.message}
    Write-Host "   OK" -ForegroundColor Green
} catch {
    $results += [PSCustomObject]@{Endpoint="GET /"; Status="ERRO"; Details=$_.Exception.Message}
    Write-Host "   ERRO: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 2. Health check
Write-Host "2. GET /api/v1/health" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/health" -Method Get
    $results += [PSCustomObject]@{Endpoint="GET /api/v1/health"; Status="OK"; Details=$response.status}
    Write-Host "   OK" -ForegroundColor Green
} catch {
    $results += [PSCustomObject]@{Endpoint="GET /api/v1/health"; Status="ERRO"; Details=$_.Exception.Message}
    Write-Host "   ERRO: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 3. Registro de usuário
Write-Host "3. POST /api/v1/register" -ForegroundColor Yellow
$email = "teste_$(Get-Random)@example.com"
$body = @{email=$email;password="teste123456"} | ConvertTo-Json
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/register" -Method Post -Body $body -ContentType "application/json"
    $results += [PSCustomObject]@{Endpoint="POST /api/v1/register"; Status="OK"; Details="Usuario criado: $email"}
    Write-Host "   OK: Usuario criado" -ForegroundColor Green
} catch {
    $status = if ($_.Exception.Response) { $_.Exception.Response.StatusCode } else { "Unknown" }
    $details = if ($_.Exception.Response) { 
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $reader.ReadToEnd()
    } else { $_.Exception.Message }
    $results += [PSCustomObject]@{Endpoint="POST /api/v1/register"; Status="ERRO $status"; Details=$details}
    Write-Host "   ERRO $status" -ForegroundColor Red
    if ($status -eq 500) {
        Write-Host "   Detalhes: $details" -ForegroundColor Red
    }
}
Write-Host ""

# 4. Login (usar usuário existente)
Write-Host "4. POST /api/v1/login/access-token" -ForegroundColor Yellow
$loginBody = @{username="teste_final@example.com";password="teste123456"}
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/login/access-token" -Method Post -Body $loginBody -ContentType "application/x-www-form-urlencoded"
    $token = $response.access_token
    $results += [PSCustomObject]@{Endpoint="POST /api/v1/login/access-token"; Status="OK"; Details="Token obtido"}
    Write-Host "   OK: Token obtido" -ForegroundColor Green
} catch {
    $status = if ($_.Exception.Response) { $_.Exception.Response.StatusCode } else { "Unknown" }
    $results += [PSCustomObject]@{Endpoint="POST /api/v1/login/access-token"; Status="ERRO $status"; Details=$_.Exception.Message}
    Write-Host "   ERRO $status" -ForegroundColor Red
}
Write-Host ""

if (-not $token) {
    Write-Host "Nao foi possivel obter token. Testando endpoints publicos apenas." -ForegroundColor Yellow
    $results | Format-Table -AutoSize
    exit
}

# 5. Listar whitelist
Write-Host "5. GET /api/v1/whitelist/" -ForegroundColor Yellow
try {
    $headers = @{Authorization="Bearer $token"}
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/whitelist/" -Method Get -Headers $headers
    $results += [PSCustomObject]@{Endpoint="GET /api/v1/whitelist/"; Status="OK"; Details="Total: $($response.Count)"}
    Write-Host "   OK" -ForegroundColor Green
} catch {
    $status = if ($_.Exception.Response) { $_.Exception.Response.StatusCode } else { "Unknown" }
    $results += [PSCustomObject]@{Endpoint="GET /api/v1/whitelist/"; Status="ERRO $status"; Details=$_.Exception.Message}
    Write-Host "   ERRO $status" -ForegroundColor Red
}
Write-Host ""

# 6. Criar placa
Write-Host "6. POST /api/v1/whitelist/" -ForegroundColor Yellow
$plateBody = @{plate="TEST-5001";description="Teste de endpoint"} | ConvertTo-Json
try {
    $headers = @{Authorization="Bearer $token"}
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/whitelist/" -Method Post -Body $plateBody -Headers $headers -ContentType "application/json"
    $results += [PSCustomObject]@{Endpoint="POST /api/v1/whitelist/"; Status="OK"; Details="Placa criada: $($response.plate)"}
    Write-Host "   OK" -ForegroundColor Green
} catch {
    $status = if ($_.Exception.Response) { $_.Exception.Response.StatusCode } else { "Unknown" }
    $details = if ($_.Exception.Response) { 
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $reader.ReadToEnd()
    } else { $_.Exception.Message }
    $results += [PSCustomObject]@{Endpoint="POST /api/v1/whitelist/"; Status="ERRO $status"; Details=$details}
    Write-Host "   ERRO $status" -ForegroundColor Red
    if ($status -eq 500) {
        Write-Host "   Detalhes: $details" -ForegroundColor Red
    }
}
Write-Host ""

# 7. Listar access logs
Write-Host "7. GET /api/v1/access_logs/" -ForegroundColor Yellow
try {
    $headers = @{Authorization="Bearer $token"}
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/access_logs/" -Method Get -Headers $headers
    $results += [PSCustomObject]@{Endpoint="GET /api/v1/access_logs/"; Status="OK"; Details="Total: $($response.Count)"}
    Write-Host "   OK" -ForegroundColor Green
} catch {
    $status = if ($_.Exception.Response) { $_.Exception.Response.StatusCode } else { "Unknown" }
    $results += [PSCustomObject]@{Endpoint="GET /api/v1/access_logs/"; Status="ERRO $status"; Details=$_.Exception.Message}
    Write-Host "   ERRO $status" -ForegroundColor Red
}
Write-Host ""

# 8. Status de dispositivos
Write-Host "8. GET /api/v1/devices/status" -ForegroundColor Yellow
try {
    $headers = @{Authorization="Bearer $token"}
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/devices/status" -Method Get -Headers $headers
    $results += [PSCustomObject]@{Endpoint="GET /api/v1/devices/status"; Status="OK"; Details=$($response | ConvertTo-Json -Compress)}
    Write-Host "   OK" -ForegroundColor Green
} catch {
    $status = if ($_.Exception.Response) { $_.Exception.Response.StatusCode } else { "Unknown" }
    $results += [PSCustomObject]@{Endpoint="GET /api/v1/devices/status"; Status="ERRO $status"; Details=$_.Exception.Message}
    Write-Host "   ERRO $status" -ForegroundColor Red
}
Write-Host ""

# 9. Acionar portão
Write-Host "9. POST /api/v1/gate_control/trigger" -ForegroundColor Yellow
try {
    $headers = @{Authorization="Bearer $token"}
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/gate_control/trigger" -Method Post -Headers $headers
    $results += [PSCustomObject]@{Endpoint="POST /api/v1/gate_control/trigger"; Status="OK"; Details=$($response | ConvertTo-Json -Compress)}
    Write-Host "   OK" -ForegroundColor Green
} catch {
    $status = if ($_.Exception.Response) { $_.Exception.Response.StatusCode } else { "Unknown" }
    $results += [PSCustomObject]@{Endpoint="POST /api/v1/gate_control/trigger"; Status="ERRO $status"; Details=$_.Exception.Message}
    Write-Host "   ERRO $status" -ForegroundColor Red
}
Write-Host ""

Write-Host "=== Resumo dos Testes ===" -ForegroundColor Cyan
$results | Format-Table -AutoSize

Write-Host "`n=== Endpoints com ERRO 500 ===" -ForegroundColor Red
$error500 = $results | Where-Object { $_.Status -like "*500*" }
if ($error500) {
    $error500 | Format-Table -AutoSize
} else {
    Write-Host "Nenhum endpoint retornou erro 500!" -ForegroundColor Green
}


