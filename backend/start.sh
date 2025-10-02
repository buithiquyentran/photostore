#!/bin/bash
# Quick start script cho PhotoStore Backend

echo "🚀 Starting PhotoStore Backend..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env from env.example..."
    cp env.example .env
    echo "✅ Created .env file"
    echo "⚠️  Please review .env file and update if needed"
fi

# Start Docker Compose
echo "🐳 Starting Docker containers..."
docker-compose up -d

# Wait a bit for services to start
echo "⏳ Waiting for services to start..."
sleep 5

# Check status
echo ""
echo "📊 Container Status:"
docker-compose ps

echo ""
echo "✅ Backend is starting!"
echo ""
echo "📍 Available at:"
echo "   • Backend API:  http://localhost:8000"
echo "   • API Docs:     http://localhost:8000/docs"
echo "   • Keycloak:     http://localhost:8080 (admin/admin)"
echo "   • Adminer:      http://localhost:8081"
echo ""
echo "🔍 View logs: docker-compose logs -f"
echo "🛑 Stop all:  docker-compose down"
