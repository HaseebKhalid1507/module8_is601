#!/bin/bash

# Test script for User Endpoints
# Usage: ./test_endpoints.sh

BASE_URL="http://localhost:8000"

echo "=========================================="
echo "Testing User Endpoints"
echo "=========================================="

# Generate unique username/email to avoid conflicts
TIMESTAMP=$(date +%s)
USERNAME="testuser_${TIMESTAMP}"
EMAIL="test_${TIMESTAMP}@example.com"
PASSWORD="password123"

echo ""
echo "1. Testing POST /users/register"
echo "-------------------------------------------"
REGISTER_RESPONSE=$(curl -s -X POST "${BASE_URL}/users/register" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"${USERNAME}\", \"email\": \"${EMAIL}\", \"password\": \"${PASSWORD}\"}")
echo "Request: POST /users/register"
echo "Body: {\"username\": \"${USERNAME}\", \"email\": \"${EMAIL}\", \"password\": \"${PASSWORD}\"}"
echo "Response: ${REGISTER_RESPONSE}"

# Extract user ID from response
USER_ID=$(echo $REGISTER_RESPONSE | grep -o '"id":[0-9]*' | grep -o '[0-9]*')
echo "Created User ID: ${USER_ID}"

echo ""
echo "2. Testing POST /users/login (valid credentials)"
echo "-------------------------------------------"
LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}/users/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"${USERNAME}\", \"password\": \"${PASSWORD}\"}")
echo "Request: POST /users/login"
echo "Body: {\"username\": \"${USERNAME}\", \"password\": \"${PASSWORD}\"}"
echo "Response: ${LOGIN_RESPONSE}"

echo ""
echo "3. Testing POST /users/login (invalid credentials)"
echo "-------------------------------------------"
INVALID_LOGIN=$(curl -s -X POST "${BASE_URL}/users/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"${USERNAME}\", \"password\": \"wrongpassword\"}")
echo "Request: POST /users/login"
echo "Body: {\"username\": \"${USERNAME}\", \"password\": \"wrongpassword\"}"
echo "Response: ${INVALID_LOGIN}"

echo ""
echo "4. Testing GET /users/ (list all users)"
echo "-------------------------------------------"
LIST_RESPONSE=$(curl -s -X GET "${BASE_URL}/users/")
echo "Request: GET /users/"
echo "Response: ${LIST_RESPONSE}"

echo ""
echo "5. Testing GET /users/{id} (get user by ID)"
echo "-------------------------------------------"
if [ -n "$USER_ID" ]; then
  GET_USER_RESPONSE=$(curl -s -X GET "${BASE_URL}/users/${USER_ID}")
  echo "Request: GET /users/${USER_ID}"
  echo "Response: ${GET_USER_RESPONSE}"
else
  echo "Skipped - No user ID available"
fi

echo ""
echo "6. Testing POST /users/register (duplicate username)"
echo "-------------------------------------------"
DUP_RESPONSE=$(curl -s -X POST "${BASE_URL}/users/register" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"${USERNAME}\", \"email\": \"other@example.com\", \"password\": \"${PASSWORD}\"}")
echo "Request: POST /users/register (duplicate username)"
echo "Response: ${DUP_RESPONSE}"

echo ""
echo "7. Testing DELETE /users/{id}"
echo "-------------------------------------------"
if [ -n "$USER_ID" ]; then
  DELETE_RESPONSE=$(curl -s -w "\nHTTP Status: %{http_code}" -X DELETE "${BASE_URL}/users/${USER_ID}")
  echo "Request: DELETE /users/${USER_ID}"
  echo "Response: ${DELETE_RESPONSE}"
else
  echo "Skipped - No user ID available"
fi

echo ""
echo "8. Testing GET /users/{id} (after deletion - should 404)"
echo "-------------------------------------------"
if [ -n "$USER_ID" ]; then
  GET_DELETED=$(curl -s -X GET "${BASE_URL}/users/${USER_ID}")
  echo "Request: GET /users/${USER_ID}"
  echo "Response: ${GET_DELETED}"
else
  echo "Skipped - No user ID available"
fi

echo ""
echo "=========================================="
echo "Calculator Endpoints Test"
echo "=========================================="

echo ""
echo "9. Testing POST /add"
echo "-------------------------------------------"
ADD_RESPONSE=$(curl -s -X POST "${BASE_URL}/add" \
  -H "Content-Type: application/json" \
  -d '{"a": 10, "b": 5}')
echo "Request: POST /add"
echo "Body: {\"a\": 10, \"b\": 5}"
echo "Response: ${ADD_RESPONSE}"

echo ""
echo "10. Testing POST /subtract"
echo "-------------------------------------------"
SUB_RESPONSE=$(curl -s -X POST "${BASE_URL}/subtract" \
  -H "Content-Type: application/json" \
  -d '{"a": 10, "b": 5}')
echo "Request: POST /subtract"
echo "Body: {\"a\": 10, \"b\": 5}"
echo "Response: ${SUB_RESPONSE}"

echo ""
echo "11. Testing POST /multiply"
echo "-------------------------------------------"
MUL_RESPONSE=$(curl -s -X POST "${BASE_URL}/multiply" \
  -H "Content-Type: application/json" \
  -d '{"a": 10, "b": 5}')
echo "Request: POST /multiply"
echo "Body: {\"a\": 10, \"b\": 5}"
echo "Response: ${MUL_RESPONSE}"

echo ""
echo "12. Testing POST /divide"
echo "-------------------------------------------"
DIV_RESPONSE=$(curl -s -X POST "${BASE_URL}/divide" \
  -H "Content-Type: application/json" \
  -d '{"a": 10, "b": 5}')
echo "Request: POST /divide"
echo "Body: {\"a\": 10, \"b\": 5}"
echo "Response: ${DIV_RESPONSE}"

echo ""
echo "13. Testing POST /divide (division by zero)"
echo "-------------------------------------------"
DIV_ZERO=$(curl -s -X POST "${BASE_URL}/divide" \
  -H "Content-Type: application/json" \
  -d '{"a": 10, "b": 0}')
echo "Request: POST /divide"
echo "Body: {\"a\": 10, \"b\": 0}"
echo "Response: ${DIV_ZERO}"

echo ""
echo "=========================================="
echo "All tests completed!"
echo "=========================================="
