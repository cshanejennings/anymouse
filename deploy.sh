#!/bin/bash

# Anymouse deployment script
set -e

STAGE=${1:-dev}
AWS_REGION=${AWS_REGION:-us-east-1}
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPO_NAME="anymouse"
IMAGE_TAG="latest"

echo "🚀 Deploying Anymouse to stage: $STAGE"
echo "📍 Region: $AWS_REGION"
echo "🔑 Account: $AWS_ACCOUNT_ID"

# Create ECR repository if it doesn't exist
echo "📦 Setting up ECR repository..."
aws ecr describe-repositories --repository-names $ECR_REPO_NAME --region $AWS_REGION >/dev/null 2>&1 || \
aws ecr create-repository --repository-name $ECR_REPO_NAME --region $AWS_REGION

# Get ECR login token
echo "🔐 Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Build Docker image
echo "🔨 Building Docker image..."
docker build -t $ECR_REPO_NAME:$IMAGE_TAG .

# Tag and push to ECR
ECR_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:$IMAGE_TAG"
echo "📤 Pushing to ECR: $ECR_URI"
docker tag $ECR_REPO_NAME:$IMAGE_TAG $ECR_URI
docker push $ECR_URI

# Deploy with SAM
echo "☁️ Deploying SAM stack..."
sam deploy \
  --template-file template.yaml \
  --stack-name "anymouse-$STAGE" \
  --parameter-overrides Stage=$STAGE \
  --capabilities CAPABILITY_IAM \
  --region $AWS_REGION \
  --no-confirm-changeset

# Get outputs
echo "📋 Deployment outputs:"
aws cloudformation describe-stacks \
  --stack-name "anymouse-$STAGE" \
  --region $AWS_REGION \
  --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
  --output table

echo "✅ Deployment complete!"
echo ""
echo "🔗 Next steps:"
echo "1. Test the API endpoints using the API key from outputs"
echo "2. Upload configuration files to the S3 bucket if needed"
echo "3. Monitor CloudWatch logs for any issues"