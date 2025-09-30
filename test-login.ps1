# PowerShell script để test login
Write-Host "🧪 Testing PhotoStore Login..." -ForegroundColor Cyan

$body = @{
    username = "testuser"
    password = "Test@123"
} | ConvertTo-Json

Write-Host "`n📤 Sending login request..." -ForegroundColor Yellow
Write-Host "   URL: http://localhost:8000/api/v1/auth/login" -ForegroundColor Gray

try {
    $response = Invoke-RestMethod -Method Post `
        -Uri "http://localhost:8000/api/v1/auth/login" `
        -ContentType "application/json" `
        -Body $body
    
    Write-Host "`n✅ LOGIN SUCCESSFUL!" -ForegroundColor Green
    Write-Host "`n📝 Response:" -ForegroundColor Cyan
    $response | ConvertTo-Json -Depth 10
    
    Write-Host "`n🎟️ Access Token (first 50 chars):" -ForegroundColor Yellow
    $response.access_token.Substring(0, [Math]::Min(50, $response.access_token.Length))
    
} catch {
    Write-Host "`n❌ LOGIN FAILED!" -ForegroundColor Red
    Write-Host "`n📝 Error:" -ForegroundColor Yellow
    $_.Exception.Message
    
    if ($_.ErrorDetails.Message) {
        Write-Host "`n📋 Details:" -ForegroundColor Yellow
        $_.ErrorDetails.Message
    }
}

Write-Host "`n" -ForegroundColor Gray
Write-Host "💡 Troubleshooting:" -ForegroundColor Cyan
Write-Host "   1. Đảm bảo user 'testuser' đã được tạo trong Keycloak" -ForegroundColor Gray
Write-Host "   2. User có password là 'Test@123'" -ForegroundColor Gray
Write-Host "   3. User được enable và email verified" -ForegroundColor Gray
Write-Host "   4. Backend đang chạy: docker-compose ps" -ForegroundColor Gray
