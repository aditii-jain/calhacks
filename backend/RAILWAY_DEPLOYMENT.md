# Railway Deployment Guide

This guide will help you deploy the Crisis-MMD Backend to Railway.

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Account**: Your code should be in a GitHub repository
3. **Supabase Project**: You'll need your Supabase credentials

## Required Environment Variables

Set these in your Railway project settings:

### Required Variables
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key-here
USE_SUPABASE=true
DEBUG=false
```

### Optional Variables
```
VAPI_API_KEY=your-vapi-api-key-here
CLAUDE_API_KEY=your-claude-api-key-here
GEMINI_API_KEY=your-gemini-api-key-here
SERIOUSNESS_THRESHOLD=0.7
MAX_BATCH_SIZE=1000
```

## Deployment Steps

### Method 1: Deploy from GitHub (Recommended)

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for Railway deployment"
   git push origin main
   ```

2. **Create Railway Project**
   - Go to [railway.app](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Select the `backend` folder as the root directory

3. **Configure Environment Variables**
   - In Railway dashboard, go to your project
   - Click on your service
   - Go to "Variables" tab
   - Add all the required environment variables listed above

4. **Deploy**
   - Railway will automatically detect the Python app and deploy it
   - The deployment will use the `Procfile` and `nixpacks.toml` we created

### Method 2: Deploy from CLI

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   # or
   curl -fsSL https://railway.app/install.sh | sh
   ```

2. **Login to Railway**
   ```bash
   railway login
   ```

3. **Initialize and Deploy**
   ```bash
   cd backend
   railway init
   railway up
   ```

4. **Set Environment Variables**
   ```bash
   railway variables set SUPABASE_URL=https://your-project.supabase.co
   railway variables set SUPABASE_ANON_KEY=your-anon-key
   railway variables set SUPABASE_SERVICE_KEY=your-service-key
   railway variables set USE_SUPABASE=true
   railway variables set DEBUG=false
   # Add other variables as needed
   ```

## Configuration Files Explained

- **`Procfile`**: Tells Railway how to start your app
- **`nixpacks.toml`**: Specifies Python version and build commands
- **`railway.json`**: Railway-specific configuration
- **`requirements.txt`**: Python dependencies

## Post-Deployment Steps

1. **Get your Railway URL**: Railway will provide a public URL like `https://your-app.railway.app`

2. **Test the deployment**:
   ```bash
   curl https://your-app.railway.app/health
   ```

3. **Update your frontend**: Update your frontend to use the Railway URL instead of `localhost:8000`

4. **Monitor logs**: Check Railway dashboard for deployment logs and any errors

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check that all dependencies are in `requirements.txt`
   - Verify Python version compatibility

2. **Runtime Errors**
   - Check environment variables are set correctly
   - Verify Supabase credentials
   - Check Railway logs for specific error messages

3. **Connection Issues**
   - Ensure your frontend CORS settings allow the Railway domain
   - Update any hardcoded localhost URLs

### Getting Help

- Railway Documentation: [docs.railway.app](https://docs.railway.app)
- Railway Discord: Join their community for support
- Check Railway logs in the dashboard for detailed error messages

## Security Notes

- Never commit `.env` files with real credentials
- Use Railway's environment variables for all secrets
- Set `DEBUG=false` in production
- Consider restricting CORS origins for production use 