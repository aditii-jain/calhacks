#!/bin/bash

echo "🚀 Railway CLI Deployment from Backend Directory"
echo "==============================================="

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    echo "Please run one of these commands first:"
    echo "  npm install -g @railway/cli"
    echo "  # or"
    echo "  curl -fsSL https://railway.app/install.sh | sh"
    exit 1
fi

echo "✅ Railway CLI found"

# Make sure we're in the backend directory
if [[ ! -f "main.py" ]]; then
    echo "❌ Please run this script from the backend directory"
    echo "Current directory: $(pwd)"
    exit 1
fi

echo "✅ In backend directory: $(pwd)"

# Login to Railway
echo "🔐 Logging into Railway..."
railway login

# Initialize Railway project in this directory
echo "🎯 Initializing Railway project..."
railway init

# Create or update railway.toml to specify this as the root
echo "📝 Configuring Railway to use backend as root directory..."
cat > railway.toml << EOF
[build]
builder = "nixpacks"

[deploy]
startCommand = "uvicorn main:app --host 0.0.0.0 --port \$PORT"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
EOF

echo "✅ Railway configuration updated"

# Deploy from this directory
echo "🚀 Deploying backend to Railway..."
railway up

echo ""
echo "✅ Deployment initiated from backend directory!"
echo ""
echo "📋 Next steps:"
echo "1. Go to railway.app dashboard"
echo "2. Click on your project"
echo "3. Go to Variables tab and add environment variables"
echo "4. Your app will automatically redeploy"
echo ""
echo "🎉 Backend deployment complete!" 