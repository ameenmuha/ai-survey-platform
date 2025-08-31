# AI-Powered Multilingual Survey Platform

A comprehensive solution for intelligent, multilingual survey data collection with AI-powered clarification and real-time analytics.

## 🚀 Live Demo

- **Frontend**: [https://ai-survey-platform.vercel.app](https://ai-survey-platform.vercel.app)
- **Backend API**: [https://ai-survey-api.onrender.com](https://ai-survey-api.onrender.com)
- **API Documentation**: [https://ai-survey-api.onrender.com/docs](https://ai-survey-api.onrender.com/docs)

## 📋 Demo Credentials

- **Admin**: `admin@example.com` / `admin123456`
- **Surveyor**: `surveyor@example.com` / `demo123456`
- **Analyst**: `analyst@example.com` / `demo123456`

## ✨ Features

### 🎯 Core Functionality
- **Multilingual Support**: 10 Indian languages (English, Hindi, Bengali, Telugu, Marathi, Tamil, Gujarati, Kannada, Malayalam, Punjabi)
- **AI-Powered Clarification**: Intelligent response processing using Google Gemini/OpenAI GPT
- **Voice Call Integration**: Twilio-powered outbound calls with TTS/STT
- **Real-time Analytics**: Comprehensive dashboard with visual insights
- **CSV Upload**: Bulk contact import with validation
- **Export Options**: CSV and PDF export capabilities

### 🔧 Technical Features
- **Modern Stack**: React/Next.js frontend, FastAPI backend, PostgreSQL database
- **Authentication**: JWT-based secure authentication with role-based access
- **Responsive Design**: Mobile-first UI with TailwindCSS
- **API-First**: RESTful API with comprehensive documentation
- **Scalable Architecture**: Modular design with clear separation of concerns

## 🏗️ Architecture

```
ai-survey-platform/
├── frontend/                 # React/Next.js frontend
│   ├── components/          # Reusable UI components
│   ├── pages/              # Next.js pages
│   ├── hooks/              # Custom React hooks
│   ├── utils/              # Utility functions
│   └── styles/             # TailwindCSS styles
├── backend/                 # FastAPI backend
│   ├── app/                # Main application
│   │   ├── core/           # Core configuration
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── api/            # API routes
│   │   └── services/       # Business logic
│   └── requirements.txt    # Python dependencies
├── ai-service/             # AI integration layer
├── voice-service/          # Voice call integration
└── docs/                   # Documentation
```

## 🛠️ Technology Stack

### Frontend
- **React 18** with Next.js 14
- **TypeScript** for type safety
- **TailwindCSS** for styling
- **React Query** for data fetching
- **React Hook Form** for form handling
- **Recharts** for data visualization
- **Lucide React** for icons

### Backend
- **FastAPI** for high-performance API
- **PostgreSQL** with SQLAlchemy ORM
- **Alembic** for database migrations
- **JWT** for authentication
- **Pydantic** for data validation
- **Celery** for background tasks

### AI & Voice Services
- **Google Gemini** / **OpenAI GPT** for AI clarification
- **Twilio** for voice calls
- **Google Cloud TTS/STT** for speech processing
- **Redis** for caching and task queue

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/ai-survey-platform.git
cd ai-survey-platform
```

### 2. Automated Setup
```bash
# Run the automated setup script
python setup.py
```

### 3. Manual Setup (Alternative)

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python scripts/demo_data.py
```

#### Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env.local
# Edit .env.local with your API URL
```

### 4. Start Services
```bash
# Backend (from backend directory)
uvicorn app.main:app --reload

# Frontend (from frontend directory)
npm run dev
```

## 🌐 Deployment

### Automated Deployment

Use our deployment script for quick deployment:

```bash
# Local deployment with Docker
./deploy.sh local

# Production deployment
./deploy.sh production -f https://your-frontend.com -b https://your-backend.com

# Cloud deployment
./deploy.sh cloud -t render
```

### Manual Deployment Options

#### 1. Netlify (Frontend)
```bash
cd frontend
npm run build
# Deploy the .next folder to Netlify
```

#### 2. Vercel (Frontend)
```bash
cd frontend
vercel --prod
```

#### 3. Render (Backend)
```bash
# Connect your GitHub repository to Render
# Set environment variables in Render dashboard
# Deploy automatically on push
```

#### 4. Railway (Backend)
```bash
# Connect your GitHub repository to Railway
# Set environment variables in Railway dashboard
# Deploy automatically on push
```

#### 5. Heroku (Both)
```bash
# Backend
cd backend
heroku create your-backend-app
git push heroku main

# Frontend
cd frontend
heroku create your-frontend-app
git push heroku main
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Production deployment
docker-compose -f docker-compose.prod.yml up -d
```

## 🔧 Environment Variables

### Backend (.env)
```env
# Database
DATABASE_URL=postgresql://user:password@localhost/ai_survey_db

# Security
SECRET_KEY=your-super-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Services
GOOGLE_AI_API_KEY=your-google-ai-key
OPENAI_API_KEY=your-openai-key

# Voice Services
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=+1234567890

# Redis
REDIS_URL=redis://localhost:6379

# CORS
CORS_ORIGINS=["http://localhost:3000"]
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📊 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Token refresh

#### Surveys
- `GET /api/v1/surveys` - List surveys
- `POST /api/v1/surveys` - Create survey
- `GET /api/v1/surveys/{id}` - Get survey details
- `PUT /api/v1/surveys/{id}` - Update survey

#### Contacts
- `GET /api/v1/contacts` - List contacts
- `POST /api/v1/contacts/upload-csv/{survey_id}` - Upload contacts CSV
- `GET /api/v1/contacts/survey/{survey_id}/stats` - Contact statistics

#### Analytics
- `GET /api/v1/analytics/dashboard` - Dashboard statistics
- `GET /api/v1/analytics/survey/{id}` - Survey analytics
- `GET /api/v1/analytics/trends` - Trends analysis

## 🔄 Workflow

1. **Survey Creation**: Create surveys with multilingual questions
2. **Contact Upload**: Upload CSV files with contact information
3. **Call Scheduling**: Schedule AI-powered outbound calls
4. **Voice Interaction**: AI conducts surveys with real-time clarification
5. **Response Processing**: AI processes and validates responses
6. **Analytics**: Real-time dashboard with insights and exports

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

### End-to-End Testing
```bash
# Test the complete workflow
python scripts/test_workflow.py
```

## 📈 Performance & Scaling

### Database Optimization
- Indexed queries for fast retrieval
- Connection pooling for high concurrency
- Efficient pagination for large datasets

### Caching Strategy
- Redis caching for frequently accessed data
- Response caching for API endpoints
- Static asset caching for frontend

### Load Balancing
- Horizontal scaling with multiple instances
- Database read replicas for high traffic
- CDN for static assets

## 🔒 Security

- **JWT Authentication** with secure token handling
- **Password Hashing** using bcrypt
- **CORS Protection** for cross-origin requests
- **Input Validation** with Pydantic schemas
- **SQL Injection Prevention** with SQLAlchemy ORM
- **Rate Limiting** for API endpoints

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [https://ai-survey-platform.vercel.app/docs](https://ai-survey-platform.vercel.app/docs)
- **Issues**: [GitHub Issues](https://github.com/yourusername/ai-survey-platform/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/ai-survey-platform/discussions)

## 🙏 Acknowledgments

- **FastAPI** for the excellent web framework
- **Next.js** for the powerful React framework
- **TailwindCSS** for the utility-first CSS framework
- **Twilio** for voice communication services
- **Google AI** for intelligent processing capabilities

---

**Built with ❤️ for intelligent survey data collection**
