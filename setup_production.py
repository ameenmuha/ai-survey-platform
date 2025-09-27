#!/usr/bin/env python3
"""
Production Setup Script for AI-Powered Multilingual Survey Platform

This script helps set up the environment for production deployment.
"""

import os
import secrets
import subprocess
import sys
from pathlib import Path

def generate_secret_key():
    """Generate a secure secret key"""
    return secrets.token_urlsafe(32)

def create_backend_env():
    """Create backend .env file with production defaults"""
    backend_dir = Path("backend")
    env_file = backend_dir / ".env"
    
    if env_file.exists():
        print(f"⚠️  {env_file} already exists. Backing up to {env_file}.backup")
        subprocess.run(["cp", str(env_file), f"{env_file}.backup"])
    
    secret_key = generate_secret_key()
    
    env_content = f"""# Database Configuration
DATABASE_URL=postgresql://user:password@localhost/ai_survey_db

# Security
SECRET_KEY={secret_key}
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# AI Services (Add your actual API keys)
GOOGLE_AI_API_KEY=your-google-ai-api-key
OPENAI_API_KEY=your-openai-api-key

# Voice Services (Add your actual Twilio credentials)
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
ALLOWED_HOSTS=["your-backend-domain.com", "localhost", "127.0.0.1"]

# File Upload
MAX_FILE_SIZE=10485760
UPLOAD_DIR=./uploads
"""
    
    with open(env_file, "w") as f:
        f.write(env_content)
    
    print(f"✅ Created {env_file}")
    return env_file

def create_frontend_env():
    """Create frontend .env.local file"""
    frontend_dir = Path("frontend")
    env_file = frontend_dir / ".env.local"
    
    if env_file.exists():
        print(f"⚠️  {env_file} already exists. Backing up to {env_file}.backup")
        subprocess.run(["cp", str(env_file), f"{env_file}.backup"])
    
    env_content = """# Frontend Environment Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=AI Survey Platform

# For production, update NEXT_PUBLIC_API_URL to your backend URL
"""
    
    with open(env_file, "w") as f:
        f.write(env_content)
    
    print(f"✅ Created {env_file}")
    return env_file

def check_dependencies():
    """Check if required dependencies are installed"""
    dependencies = ["docker", "docker-compose", "node", "npm"]
    missing = []
    
    for dep in dependencies:
        try:
            subprocess.run([dep, "--version"], capture_output=True, check=True)
            print(f"✅ {dep} is installed")
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing.append(dep)
            print(f"❌ {dep} is not installed")
    
    return missing

def install_backend_dependencies():
    """Install backend Python dependencies"""
    backend_dir = Path("backend")
    requirements_file = backend_dir / "requirements.txt"
    
    if not requirements_file.exists():
        print(f"❌ {requirements_file} not found")
        return False
    
    try:
        print("📦 Installing backend dependencies...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], check=True)
        print("✅ Backend dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install backend dependencies: {e}")
        return False

def install_frontend_dependencies():
    """Install frontend Node.js dependencies"""
    frontend_dir = Path("frontend")
    package_file = frontend_dir / "package.json"
    
    if not package_file.exists():
        print(f"❌ {package_file} not found")
        return False
    
    try:
        print("📦 Installing frontend dependencies...")
        subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
        print("✅ Frontend dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install frontend dependencies: {e}")
        return False

def build_docker_images():
    """Build Docker images"""
    try:
        print("🐳 Building Docker images...")
        
        # Build backend image
        print("Building backend image...")
        subprocess.run([
            "docker", "build", "-t", "ai-survey-backend", "./backend"
        ], check=True)
        
        # Build frontend image
        print("Building frontend image...")
        subprocess.run([
            "docker", "build", "-t", "ai-survey-frontend", "./frontend"
        ], check=True)
        
        print("✅ Docker images built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to build Docker images: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 AI-Powered Multilingual Survey Platform - Production Setup")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("backend").exists() or not Path("frontend").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Check dependencies
    print("\n📋 Checking dependencies...")
    missing_deps = check_dependencies()
    
    if missing_deps:
        print(f"\n❌ Missing dependencies: {', '.join(missing_deps)}")
        print("Please install them before proceeding.")
        print("\nInstallation commands:")
        if "docker" in missing_deps:
            print("  Docker: https://docs.docker.com/get-docker/")
        if "node" in missing_deps:
            print("  Node.js: https://nodejs.org/")
        sys.exit(1)
    
    # Create environment files
    print("\n📄 Creating environment files...")
    backend_env = create_backend_env()
    frontend_env = create_frontend_env()
    
    # Install dependencies (optional)
    choice = input("\n❓ Install project dependencies? (y/N): ").lower()
    if choice == 'y':
        install_backend_dependencies()
        install_frontend_dependencies()
    
    # Build Docker images (optional)
    choice = input("\n❓ Build Docker images? (y/N): ").lower()
    if choice == 'y':
        build_docker_images()
    
    print("\n" + "=" * 60)
    print("🎉 Production setup completed!")
    print("=" * 60)
    
    print(f"\n📝 Next steps:")
    print(f"1. Edit {backend_env} with your actual configuration:")
    print("   - Database URL")
    print("   - API keys (Google AI, OpenAI)")
    print("   - Twilio credentials")
    print("   - Production domain URLs")
    
    print(f"\n2. Edit {frontend_env} with your backend URL")
    
    print("\n3. Choose a deployment method:")
    print("   - Local: ./deploy.sh local")
    print("   - Cloud: ./deploy.sh cloud -t render")
    print("   - Production: ./deploy.sh production -f <frontend-url> -b <backend-url>")
    
    print("\n4. Initialize demo data (after database is running):")
    print("   python3 scripts/demo_data.py")
    
    print("\n📖 For detailed deployment instructions, see:")
    print("   - README.md")
    print("   - DEPLOYMENT.md")
    print("   - DEPLOYMENT_GUIDE.md")

if __name__ == "__main__":
    main()