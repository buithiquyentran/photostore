@echo off
REM Quick start script cho PhotoStore Backend

echo ========================================
echo 🚀 Starting PhotoStore Backend...
echo ========================================

REM Check if .env exists
if not exist .env (
    echo 📝 Creating .env from env.example...
    copy env.example .env
    echo ✅ Created .env file
    echo ⚠️  Please review .env file and update if needed
)

REM Start Docker Compose
echo 🐳 Starting Docker containers...
docker-compose up -d

REM Wait for services
echo ⏳ Waiting for services to start...
timeout /t 5 /nobreak >nul

REM Check status
echo.
echo 📊 Container Status:
docker-compose ps

echo.
echo ✅ Backend is starting!
echo.
echo 📍 Available at:
echo    • Backend API:  http://localhost:8000
echo    • API Docs:     http://localhost:8000/docs
echo    • Keycloak:     http://localhost:8080 (admin/admin)
echo    • Adminer:      http://localhost:8081
echo.
echo 🔍 View logs: docker-compose logs -f
echo 🛑 Stop all:  docker-compose down
echo.
pause
