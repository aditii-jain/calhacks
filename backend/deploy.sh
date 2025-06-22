#!/bin/bash

echo "🚀 Crisis-MMD Backend Railway Deployment Script"
echo "================================================"

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

# Check if we're in the backend directory
if [[ ! -f "main.py" ]]; then
    echo "❌ Please run this script from the backend directory"
    exit 1
fi

echo "✅ In backend directory"

# Check for required files
echo "🔍 Checking deployment files..."
required_files=("Procfile" "requirements.txt" "nixpacks.toml" "railway.json")
for file in "${required_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo "✅ $file exists"
    else
        echo "❌ $file missing"
        exit 1
    fi
done

echo ""
echo "🚨 IMPORTANT: Make sure you have these environment variables ready:"
echo "   - SUPABASE_URL"
echo "   - SUPABASE_ANON_KEY" 
echo "   - SUPABASE_SERVICE_KEY"
echo ""

read -p "Have you set up your Supabase credentials? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Please set up Supabase first, then run this script again"
    exit 1
fi

# Login to Railway
echo "🔐 Logging into Railway..."
railway login

# Initialize Railway project
echo "🎯 Initializing Railway project..."
railway init

# Deploy
echo "🚀 Deploying to Railway..."
railway up

echo ""
echo "✅ Deployment initiated!"
echo ""
echo "📋 Next steps:"
echo "1. Go to railway.app dashboard"
echo "2. Click on your project"
echo "3. Go to Variables tab and add:"
echo "   - SUPABASE_URL=https://your-project.supabase.co"
echo "   - SUPABASE_ANON_KEY=your-anon-key"
echo "   - SUPABASE_SERVICE_KEY=your-service-key"
echo "   - USE_SUPABASE=true"
echo "   - DEBUG=false"
echo "4. Your app will automatically redeploy"
echo "5. Test with: curl https://your-app.railway.app/health"
echo ""
echo "🎉 Happy deploying!" 