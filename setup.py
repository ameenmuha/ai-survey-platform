#!/usr/bin/env python3
"""
Setup script for AI-Powered Multilingual Survey Platform

This script helps set up the development environment and initial configuration
for the AI-Powered Multilingual Survey Platform.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, cwd=None):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command '{command}': {e}")
        print(f"Error output: {e.stderr}")
        return None

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ Python 3.9 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def check_node_version():
    """Check if Node.js version is compatible"""
    result = run_command("node --version")
    if not result:
        print("❌ Node.js is not installed or not in PATH")
        return False
    
    version = result.replace('v', '')
    major_version = int(version.split('.')[0])
    if major_version < 18:
        print(f"❌ Node.js 18 or higher is required")
        print(f"Current version: {version}")
        return False
    
    print(f"✅ Node.js {version} is compatible")
    return True

def setup_backend():
    """Set up the FastAPI backend"""
    print("\n🔧 Setting up FastAPI Backend...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    # Create virtual environment
    print("Creating Python virtual environment...")
    if not run_command("python -m venv venv", cwd=backend_dir):
        return False
    
    # Activate virtual environment and install dependencies
    if os.name == 'nt':  # Windows
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix/Linux/Mac
        pip_cmd = "venv/bin/pip"
    
    print("Installing Python dependencies...")
    if not run_command(f"{pip_cmd} install -r requirements.txt", cwd=backend_dir):
        return False
    
    # Create .env file if it doesn't exist
    env_file = backend_dir / ".env"
    if not env_file.exists():
        print("Creating .env file...")
        env_example = backend_dir / "env.example"
        if env_example.exists():
            shutil.copy(env_example, env_file)
            print("✅ .env file created from template")
        else:
            print("⚠️  No env.example found, please create .env manually")
    
    print("✅ Backend setup completed")
    return True

def setup_frontend():
    """Set up the Next.js frontend"""
    print("\n🔧 Setting up Next.js Frontend...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Install Node.js dependencies
    print("Installing Node.js dependencies...")
    if not run_command("npm install", cwd=frontend_dir):
        return False
    
    # Create .env.local file if it doesn't exist
    env_local_file = frontend_dir / ".env.local"
    if not env_local_file.exists():
        print("Creating .env.local file...")
        env_content = """NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=AI Survey Platform
"""
        with open(env_local_file, 'w') as f:
            f.write(env_content)
        print("✅ .env.local file created")
    
    print("✅ Frontend setup completed")
    return True

def create_database():
    """Create PostgreSQL database"""
    print("\n🗄️  Setting up Database...")
    
    # Check if PostgreSQL is available
    result = run_command("psql --version")
    if not result:
        print("⚠️  PostgreSQL not found in PATH")
        print("Please install PostgreSQL and ensure 'psql' is in your PATH")
        return False
    
    print("Creating database...")
    db_name = "ai_survey_db"
    
    # Try to create database
    result = run_command(f"createdb {db_name}")
    if result is not None:
        print(f"✅ Database '{db_name}' created successfully")
    else:
        print(f"⚠️  Could not create database '{db_name}'")
        print("You may need to create it manually or check PostgreSQL permissions")
    
    return True

def generate_secret_key():
    """Generate a secure secret key"""
    import secrets
    return secrets.token_urlsafe(32)

def update_env_files():
    """Update environment files with generated values"""
    print("\n🔐 Updating environment files...")
    
    secret_key = generate_secret_key()
    
    # Update backend .env
    backend_env = Path("backend/.env")
    if backend_env.exists():
        content = backend_env.read_text()
        content = content.replace("your-super-secret-key-here-change-in-production", secret_key)
        backend_env.write_text(content)
        print("✅ Backend .env updated with secret key")
    
    # Update frontend .env.local
    frontend_env = Path("frontend/.env.local")
    if frontend_env.exists():
        content = frontend_env.read_text()
        if "NEXT_PUBLIC_API_URL" not in content:
            content += "\nNEXT_PUBLIC_API_URL=http://localhost:8000\n"
        frontend_env.write_text(content)
        print("✅ Frontend .env.local updated")

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "="*60)
    print("🎉 Setup completed successfully!")
    print("="*60)
    
    print("\n📋 Next Steps:")
    print("1. Configure your environment variables:")
    print("   - Edit backend/.env with your API keys and database settings")
    print("   - Add your Twilio credentials for voice calls")
    print("   - Add your Google AI or OpenAI API keys")
    
    print("\n2. Start the services:")
    print("   Backend:  cd backend && venv\\Scripts\\python -m uvicorn app.main:app --reload")
    print("   Frontend: cd frontend && npm run dev")
    
    print("\n3. Access the application:")
    print("   Frontend: http://localhost:3000")
    print("   Backend API: http://localhost:8000")
    print("   API Docs: http://localhost:8000/docs")
    
    print("\n4. Create your first user:")
    print("   - Use the registration endpoint: POST /api/v1/auth/register")
    print("   - Or create a user directly in the database")
    
    print("\n🔧 Development Tips:")
    print("- Use the demo credentials on the login page for testing")
    print("- Check the logs for any errors during startup")
    print("- Ensure PostgreSQL is running and accessible")
    print("- Configure your voice service credentials for call functionality")
    
    print("\n📚 Documentation:")
    print("- README.md contains detailed setup and usage instructions")
    print("- API documentation is available at /docs when the backend is running")
    print("- Check the code comments for implementation details")

def main():
    """Main setup function"""
    print("🚀 AI-Powered Multilingual Survey Platform Setup")
    print("=" * 60)
    
    # Check prerequisites
    print("\n🔍 Checking prerequisites...")
    if not check_python_version():
        sys.exit(1)
    
    if not check_node_version():
        sys.exit(1)
    
    # Setup backend
    if not setup_backend():
        print("❌ Backend setup failed")
        sys.exit(1)
    
    # Setup frontend
    if not setup_frontend():
        print("❌ Frontend setup failed")
        sys.exit(1)
    
    # Setup database
    create_database()
    
    # Update environment files
    update_env_files()
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main()
