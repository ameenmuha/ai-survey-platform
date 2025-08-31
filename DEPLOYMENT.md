# Deployment Guide

This guide provides detailed instructions for deploying the AI-Powered Multilingual Survey Platform to various cloud platforms.

## 🚀 Quick Deployment

### Automated Deployment Script

Use our deployment script for the fastest setup:

```bash
# Make the script executable
chmod +x deploy.sh

# Local deployment with Docker
./deploy.sh local

# Production deployment
./deploy.sh production -f https://your-frontend.com -b https://your-backend.com

# Cloud deployment
./deploy.sh cloud -t render
```

## 🌐 Cloud Platform Deployment

### 1. Vercel (Frontend) + Render (Backend)

#### Frontend Deployment on Vercel

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Deploy Frontend**
   ```bash
   cd frontend
   vercel --prod
   ```

3. **Configure Environment Variables**
   - Go to Vercel Dashboard → Your Project → Settings → Environment Variables
   - Add: `NEXT_PUBLIC_API_URL=https://your-backend.onrender.com`

#### Backend Deployment on Render

1. **Connect GitHub Repository**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New" → "Web Service"
   - Connect your GitHub repository

2. **Configure Service**
   - **Name**: `ai-survey-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Set Environment Variables**
   ```env
   DATABASE_URL=postgresql://user:password@host:port/database
   SECRET_KEY=your-super-secret-key
   GOOGLE_AI_API_KEY=your-google-ai-key
   OPENAI_API_KEY=your-openai-key
   TWILIO_ACCOUNT_SID=your-twilio-sid
   TWILIO_AUTH_TOKEN=your-twilio-token
   TWILIO_PHONE_NUMBER=+1234567890
   REDIS_URL=redis://your-redis-url
   CORS_ORIGINS=["https://your-frontend.vercel.app"]
   ```

4. **Add PostgreSQL Database**
   - Create a new PostgreSQL service in Render
   - Copy the connection string to `DATABASE_URL`

### 2. Railway (Full Stack)

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Deploy to Railway**
   ```bash
   # Login to Railway
   railway login

   # Initialize project
   railway init

   # Deploy
   railway up
   ```

3. **Configure Services**
   - Add PostgreSQL plugin
   - Add Redis plugin
   - Set environment variables in Railway dashboard

### 3. Heroku (Full Stack)

#### Backend Deployment

1. **Install Heroku CLI**
   ```bash
   # macOS
   brew install heroku/brew/heroku

   # Windows
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Create Heroku App**
   ```bash
   cd backend
   heroku create your-backend-app
   ```

3. **Add PostgreSQL**
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

4. **Set Environment Variables**
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set GOOGLE_AI_API_KEY=your-google-ai-key
   heroku config:set OPENAI_API_KEY=your-openai-key
   heroku config:set TWILIO_ACCOUNT_SID=your-twilio-sid
   heroku config:set TWILIO_AUTH_TOKEN=your-twilio-token
   heroku config:set TWILIO_PHONE_NUMBER=+1234567890
   heroku config:set CORS_ORIGINS=["https://your-frontend.herokuapp.com"]
   ```

5. **Deploy**
   ```bash
   git add .
   git commit -m "Deploy backend to Heroku"
   git push heroku main
   ```

#### Frontend Deployment

1. **Create Frontend App**
   ```bash
   cd frontend
   heroku create your-frontend-app
   ```

2. **Set Environment Variables**
   ```bash
   heroku config:set NEXT_PUBLIC_API_URL=https://your-backend-app.herokuapp.com
   ```

3. **Deploy**
   ```bash
   git add .
   git commit -m "Deploy frontend to Heroku"
   git push heroku main
   ```

### 4. Netlify (Frontend) + DigitalOcean (Backend)

#### Frontend on Netlify

1. **Build the Project**
   ```bash
   cd frontend
   npm run build
   ```

2. **Deploy to Netlify**
   - Go to [Netlify](https://netlify.com)
   - Drag and drop the `.next` folder
   - Or connect your GitHub repository

3. **Configure Environment Variables**
   - Go to Site Settings → Environment Variables
   - Add: `NEXT_PUBLIC_API_URL=https://your-backend-ip:8000`

#### Backend on DigitalOcean

1. **Create Droplet**
   - Choose Ubuntu 22.04
   - Select plan based on your needs
   - Add SSH key

2. **Connect and Setup**
   ```bash
   ssh root@your-droplet-ip

   # Update system
   apt update && apt upgrade -y

   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh

   # Install Docker Compose
   curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   chmod +x /usr/local/bin/docker-compose
   ```

3. **Deploy Application**
   ```bash
   # Clone repository
   git clone https://github.com/yourusername/ai-survey-platform.git
   cd ai-survey-platform

   # Create production environment file
   cp backend/.env.example backend/.env
   # Edit backend/.env with your configuration

   # Deploy with Docker Compose
   docker-compose -f docker-compose.prod.yml up -d
   ```

## 🐳 Docker Deployment

### Local Docker Deployment

```bash
# Build and run all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Production Docker Deployment

```bash
# Create production environment file
cp .env.example .env.prod
# Edit .env.prod with production values

# Deploy with production compose file
docker-compose -f docker-compose.prod.yml up -d
```

### Docker Swarm Deployment

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.prod.yml ai-survey
```

## 🔧 Environment Configuration

### Required Environment Variables

#### Backend (.env)
```env
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# Security
SECRET_KEY=your-super-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# AI Services
GOOGLE_AI_API_KEY=your-google-ai-api-key
OPENAI_API_KEY=your-openai-api-key

# Voice Services
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=+1234567890

# Google Cloud Services
GOOGLE_CLOUD_PROJECT_ID=your-google-cloud-project-id
GOOGLE_CLOUD_CREDENTIALS=path/to/your/credentials.json

# Redis
REDIS_URL=redis://localhost:6379

# Application Settings
DEBUG=False
ENVIRONMENT=production
CORS_ORIGINS=["https://your-frontend-domain.com"]

# File Upload
MAX_FILE_SIZE=10485760
UPLOAD_DIR=./uploads
```

#### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=https://your-backend-domain.com
NEXT_PUBLIC_APP_NAME=AI Survey Platform
```

## 📊 Database Setup

### PostgreSQL Setup

1. **Create Database**
   ```sql
   CREATE DATABASE ai_survey_db;
   CREATE USER ai_survey_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE ai_survey_db TO ai_survey_user;
   ```

2. **Run Migrations**
   ```bash
   cd backend
   alembic upgrade head
   ```

3. **Seed Demo Data**
   ```bash
   python scripts/demo_data.py
   ```

### Redis Setup

1. **Install Redis**
   ```bash
   # Ubuntu/Debian
   sudo apt install redis-server

   # macOS
   brew install redis
   ```

2. **Start Redis**
   ```bash
   sudo systemctl start redis-server
   ```

## 🔒 Security Configuration

### SSL/TLS Setup

1. **Let's Encrypt (Recommended)**
   ```bash
   # Install Certbot
   sudo apt install certbot

   # Get certificate
   sudo certbot certonly --standalone -d your-domain.com

   # Configure Nginx
   sudo nano /etc/nginx/sites-available/your-domain.com
   ```

2. **Nginx Configuration**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       return 301 https://$server_name$request_uri;
   }

   server {
       listen 443 ssl;
       server_name your-domain.com;

       ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### Firewall Configuration

```bash
# Allow SSH
sudo ufw allow ssh

# Allow HTTP/HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Allow application ports
sudo ufw allow 8000
sudo ufw allow 3000

# Enable firewall
sudo ufw enable
```

## 📈 Monitoring and Logging

### Application Monitoring

1. **Health Checks**
   ```bash
   # Backend health check
   curl https://your-backend.com/health

   # Frontend health check
   curl https://your-frontend.com/api/health
   ```

2. **Log Monitoring**
   ```bash
   # View application logs
   docker-compose logs -f backend
   docker-compose logs -f frontend

   # View system logs
   sudo journalctl -u docker.service -f
   ```

### Performance Monitoring

1. **Database Monitoring**
   ```sql
   -- Check active connections
   SELECT count(*) FROM pg_stat_activity;

   -- Check slow queries
   SELECT query, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;
   ```

2. **Application Metrics**
   ```bash
   # Check resource usage
   docker stats

   # Monitor API performance
   curl -w "@curl-format.txt" -o /dev/null -s "https://your-backend.com/api/v1/health"
   ```

## 🔄 CI/CD Pipeline

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Render
        uses: johnbeynon/render-deploy-action@v1.0.0
        with:
          service-id: ${{ secrets.RENDER_SERVICE_ID }}
          api-key: ${{ secrets.RENDER_API_KEY }}

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
          vercel-args: '--prod'
```

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Issues**
   ```bash
   # Check database connectivity
   psql $DATABASE_URL -c "SELECT 1;"

   # Check database logs
   docker-compose logs postgres
   ```

2. **CORS Issues**
   ```bash
   # Verify CORS configuration
   curl -H "Origin: https://your-frontend.com" \
        -H "Access-Control-Request-Method: POST" \
        -H "Access-Control-Request-Headers: Content-Type" \
        -X OPTIONS https://your-backend.com/api/v1/auth/login
   ```

3. **Memory Issues**
   ```bash
   # Check memory usage
   free -h
   docker system df

   # Clean up Docker
   docker system prune -a
   ```

### Performance Optimization

1. **Database Optimization**
   ```sql
   -- Create indexes for better performance
   CREATE INDEX idx_surveys_created_by ON surveys(created_by);
   CREATE INDEX idx_responses_survey_id ON responses(survey_id);
   CREATE INDEX idx_contacts_survey_id ON contacts(survey_id);
   ```

2. **Application Optimization**
   ```bash
   # Enable gzip compression
   # Add to nginx configuration
   gzip on;
   gzip_types text/plain text/css application/json application/javascript;
   ```

## 📞 Support

For deployment issues:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review application logs
3. Open an issue on GitHub
4. Contact support with deployment details

---

**Happy Deploying! 🚀**
