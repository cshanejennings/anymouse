#!/bin/bash

# Test deployment script for Anymouse
set -e

STAGE=${1:-dev}
AWS_REGION=${AWS_REGION:-us-east-1}

echo "🧪 Testing Anymouse deployment for stage: $STAGE"

# Get API endpoint and key from CloudFormation outputs
API_URL=$(aws cloudformation describe-stacks \
  --stack-name "anymouse-$STAGE" \
  --region $AWS_REGION \
  --query 'Stacks[0].Outputs[?OutputKey==`AnymouseApi`].OutputValue' \
  --output text)

API_KEY=$(aws cloudformation describe-stacks \
  --stack-name "anymouse-$STAGE" \
  --region $AWS_REGION \
  --query 'Stacks[0].Outputs[?OutputKey==`AnymouseApiKey`].OutputValue' \
  --output text)

if [ -z "$API_URL" ] || [ -z "$API_KEY" ]; then
  echo "❌ Could not retrieve API URL or key from CloudFormation stack"
  exit 1
fi

echo "🔗 API URL: $API_URL"
echo "🔑 API Key: ${API_KEY:0:8}..."

# Test anonymize endpoint with free-form text
echo ""
echo "🔒 Testing /anonymize endpoint with free-form text..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
  "$API_URL/anonymize" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "payload": "Hello, I have a question for Dr. McCulloch regarding my prescription. Thank you, Jane Smith"
  }')

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n -1)

if [ "$HTTP_CODE" = "200" ]; then
  echo "✅ Anonymize test passed"
  echo "📄 Response: $BODY"
else
  echo "❌ Anonymize test failed with HTTP $HTTP_CODE"
  echo "📄 Response: $BODY"
  exit 1
fi

# Extract tokens for deanonymize test
TOKENS=$(echo "$BODY" | jq -r '.tokens')
MESSAGE=$(echo "$BODY" | jq -r '.message')

# Test deanonymize endpoint
echo ""
echo "🔓 Testing /deanonymize endpoint..."
DEANO_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
  "$API_URL/deanonymize" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "{
    \"message\": $(echo "$MESSAGE" | jq -R .),
    \"tokens\": $TOKENS
  }")

DEANO_HTTP_CODE=$(echo "$DEANO_RESPONSE" | tail -n1)
DEANO_BODY=$(echo "$DEANO_RESPONSE" | head -n -1)

if [ "$DEANO_HTTP_CODE" = "200" ]; then
  echo "✅ Deanonymize test passed"
  echo "📄 Response: $DEANO_BODY"
else
  echo "❌ Deanonymize test failed with HTTP $DEANO_HTTP_CODE"
  echo "📄 Response: $DEANO_BODY"
  exit 1
fi

# Test config/test endpoint
echo ""
echo "⚙️ Testing /config/test endpoint..."
CONFIG_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
  "$API_URL/config/test" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "config": {
      "fields": ["name", "email"]
    }
  }')

CONFIG_HTTP_CODE=$(echo "$CONFIG_RESPONSE" | tail -n1)
CONFIG_BODY=$(echo "$CONFIG_RESPONSE" | head -n -1)

if [ "$CONFIG_HTTP_CODE" = "200" ]; then
  echo "✅ Config test passed"
  echo "📄 Response: $CONFIG_BODY"
else
  echo "❌ Config test failed with HTTP $CONFIG_HTTP_CODE"
  echo "📄 Response: $CONFIG_BODY"
  exit 1
fi

echo ""
echo "🎉 All tests passed! Deployment is working correctly."