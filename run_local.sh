#!/bin/bash
# Run FastAPI application locally

set -e

echo "🔧 Setting up local environment..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "⚠️  No .env file found. Using defaults."
    export AWS_REGION=us-east-1
    export EVENTS_TABLE_NAME=UserEvents
    export RECOMMENDATIONS_TABLE_NAME=UserRecommendations
    export CACHE_TABLE_NAME=RecommendationCache
fi

# Run the application
echo "🚀 Starting FastAPI server..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

