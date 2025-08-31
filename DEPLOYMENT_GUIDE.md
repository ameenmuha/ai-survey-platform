# 🚀 Deployment Guide - AI-Powered Multilingual Survey Platform

This guide provides step-by-step instructions for deploying the platform to production.

## 📋 Prerequisites

- Git repository initialized and committed
- Node.js 18+ and npm
- Python 3.11+ and pip
- Vercel account (for frontend)
- Render account (for backend)
- PostgreSQL database (Render provides this)

## 🎯 Deployment Strategy

We'll deploy:
- **Frontend**: Vercel (Next.js optimized)
- **Backend**: Render (FastAPI with PostgreSQL)
- **Database**: Render PostgreSQL (free tier)

## 🚀 Step 1: Frontend Deployment (Vercel)

### Option A: Using Vercel CLI (Recommended)

1. **Install Vercel CLI** (if not already installed):
   ```bash
   npm i -g vercel@latest
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```
   Choose your preferred login method (GitHub, GitLab, etc.)

3. **Deploy from frontend directory**:
   ```bash
   cd frontend
   vercel --prod
   ```

4. **Configure environment variables** in Vercel dashboard:
   - `NEXT_PUBLIC_API_URL`: Your backend URL (e.g., https://your-backend.onrender.com)

### Option B: Using Vercel Dashboard

1. **Push to GitHub**:
   ```bash
   git remote add origin https://github.com/yourusername/ai-survey-platform.git
   git push -u origin main
   ```

2. **Connect to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Set root directory to `frontend`
   - Configure environment variables

## 🚀 Step 2: Backend Deployment (Render)

### Option A: Using Render Dashboard (Recommended)

1. **Prepare for deployment**:
   ```bash
   cd backend
   ```

2. **Create render.yaml** (create this file in backend directory):
   ```yaml
   services:
     - type: web
       name: ai-survey-backend
       env: python
       plan: free
       buildCommand: pip install -r requirements.txt
       startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
       envVars:
         - key: DATABASE_URL
           fromDatabase:
             name: ai-survey-db
             property: connectionString
         - key: SECRET_KEY
           generateValue: true
         - key: DEBUG
           value: false
         - key: ENVIRONMENT
           value: production
         - key: CORS_ORIGINS
           value: ["https://your-frontend.vercel.app"]
         - key: GOOGLE_AI_API_KEY
           sync: false
         - key: OPENAI_API_KEY
           sync: false
         - key: TWILIO_ACCOUNT_SID
           sync: false
         - key: TWILIO_AUTH_TOKEN
           sync: false
         - key: TWILIO_PHONE_NUMBER
           sync: false

   databases:
     - name: ai-survey-db
       plan: free
   ```

3. **Deploy to Render**:
   - Go to [render.com](https://render.com)
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect the render.yaml and deploy

### Option B: Manual Deployment

1. **Create Web Service**:
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Set root directory to `backend`

2. **Configure Build Settings**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Add Environment Variables**:
   ```
   DATABASE_URL=postgresql://... (from Render PostgreSQL)
   SECRET_KEY=your-super-secret-key-here
   DEBUG=false
   ENVIRONMENT=production
   CORS_ORIGINS=["https://your-frontend.vercel.app"]
   GOOGLE_AI_API_KEY=your-google-ai-key
   OPENAI_API_KEY=your-openai-key
   TWILIO_ACCOUNT_SID=your-twilio-sid
   TWILIO_AUTH_TOKEN=your-twilio-token
   TWILIO_PHONE_NUMBER=your-twilio-number
   ```

4. **Create PostgreSQL Database**:
   - Click "New +" → "PostgreSQL"
   - Choose free plan
   - Copy the connection string to DATABASE_URL

## 🔧 Step 3: Environment Configuration

### Frontend Environment Variables (Vercel)

```env
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
```

### Backend Environment Variables (Render)

```env
DATABASE_URL=postgresql://username:password@host:port/database
SECRET_KEY=your-super-secret-key-here-change-in-production
DEBUG=false
ENVIRONMENT=production
CORS_ORIGINS=["https://your-frontend.vercel.app"]
GOOGLE_AI_API_KEY=your-google-ai-api-key
OPENAI_API_KEY=your-openai-api-key
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=your-twilio-phone-number
```

## 🗄️ Step 4: Database Setup

1. **Initialize Database** (after backend deployment):
   ```bash
   # The backend will automatically create tables on first run
   # Or you can run migrations manually if needed
   ```

2. **Load Demo Data** (optional):
   ```bash
   # After deployment, you can run the demo data script
   python scripts/demo_data.py
   ```

## 🔗 Step 5: Update Frontend Configuration

1. **Update API URL** in frontend:
   - Go to Vercel dashboard
   - Update `NEXT_PUBLIC_API_URL` environment variable
   - Redeploy if needed

## ✅ Step 6: Testing Deployment

1. **Test Frontend**: Visit your Vercel URL
2. **Test Backend**: Visit your Render URL + `/docs`
3. **Test API**: Try the health check endpoint
4. **Test Authentication**: Try logging in with demo credentials

## 🎯 Demo Credentials

After deployment, you can use these demo credentials:

- **Admin**: `admin@example.com` / `admin123456`
- **Surveyor**: `surveyor@example.com` / `demo123456`
- **Analyst**: `analyst@example.com` / `demo123456`

## 🔧 Troubleshooting

### Common Issues

1. **CORS Errors**:
   - Ensure CORS_ORIGINS includes your frontend URL
   - Check for trailing slashes

2. **Database Connection**:
   - Verify DATABASE_URL format
   - Check if database is accessible

3. **Build Failures**:
   - Check requirements.txt for missing dependencies
   - Verify Python version compatibility

4. **Environment Variables**:
   - Ensure all required variables are set
   - Check for typos in variable names

### Debug Commands

```bash
# Check backend logs
# In Render dashboard → Logs

# Check frontend build
# In Vercel dashboard → Functions → View Function Logs

# Test API locally
curl https://your-backend.onrender.com/health
```

## 📊 Monitoring

1. **Vercel Analytics**: Built-in performance monitoring
2. **Render Logs**: Real-time application logs
3. **Database Monitoring**: Render PostgreSQL metrics

## 🔄 Continuous Deployment

Both Vercel and Render support automatic deployments:
- Push to main branch → automatic deployment
- Preview deployments for pull requests

## 🎉 Success!

Your AI-Powered Multilingual Survey Platform is now live!

- **Frontend**: https://your-app.vercel.app
- **Backend**: https://your-backend.onrender.com
- **API Docs**: https://your-backend.onrender.com/docs

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section
2. Review Render and Vercel documentation
3. Check application logs in respective dashboards
