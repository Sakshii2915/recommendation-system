#!/bin/bash
# Deployment script for recommendation system

set -e

echo "🚀 Deploying Recommendation System..."

# Check if AWS SAM CLI is installed
if ! command -v sam &> /dev/null; then
    echo "❌ AWS SAM CLI is not installed. Please install it first."
    echo "Visit: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html"
    exit 1
fi

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS CLI is not configured. Please run 'aws configure' first."
    exit 1
fi

# Build the application
echo "📦 Building application..."
sam build

# Deploy
echo "☁️  Deploying to AWS..."
sam deploy --guided

echo "✅ Deployment complete!"
echo ""
echo "📊 Access CloudWatch Dashboard:"
echo "https://console.aws.amazon.com/cloudwatch/home?region=$(aws configure get region)#dashboards:name=RecommendationSystemDashboard"

