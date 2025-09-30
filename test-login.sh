#!/bin/bash
# Bash script để test login

echo "🧪 Testing PhotoStore Login..."

echo ""
echo "📤 Sending login request..."
echo "   URL: http://localhost:8000/api/v1/auth/login"

response=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "Test@123"
  }')

echo ""
if echo "$response" | grep -q "access_token"; then
    echo "✅ LOGIN SUCCESSFUL!"
    echo ""
    echo "📝 Response:"
    echo "$response" | jq '.'
    echo ""
    echo "🎟️ Access Token (first 50 chars):"
    echo "$response" | jq -r '.access_token' | cut -c1-50
else
    echo "❌ LOGIN FAILED!"
    echo ""
    echo "📝 Error:"
    echo "$response" | jq '.'
fi

echo ""
echo "💡 Troubleshooting:"
echo "   1. Đảm bảo user 'testuser' đã được tạo trong Keycloak"
echo "   2. User có password là 'Test@123'"
echo "   3. User được enable và email verified"
echo "   4. Backend đang chạy: docker-compose ps"
