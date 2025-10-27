@echo off
REM Learning Cloud Setup Script for Windows
REM This script sets up the development environment for Learning Cloud

echo 🚀 Setting up Learning Cloud Development Environment...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed. Please install Python 3.9+
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed. Please install Node.js 16+
    pause
    exit /b 1
)

REM Check if PostgreSQL is installed
psql --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] PostgreSQL is not installed. Please install PostgreSQL 13+
    pause
    exit /b 1
)

REM Check if Redis is installed
redis-server --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Redis is not installed. Please install Redis 6+
    pause
    exit /b 1
)

echo [INFO] All prerequisites found ✓

REM Create virtual environment
if not exist "venv" (
    echo [INFO] Creating Python virtual environment...
    python -m venv venv
    echo [INFO] Virtual environment created ✓
) else (
    echo [WARNING] Virtual environment already exists
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
echo [INFO] Virtual environment activated ✓

REM Install Python dependencies
echo [INFO] Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
echo [INFO] Python dependencies installed ✓

REM Install Node.js dependencies
echo [INFO] Installing Node.js dependencies...
npm install prisma @prisma/client
echo [INFO] Node.js dependencies installed ✓

REM Setup environment file
if not exist ".env" (
    echo [INFO] Setting up environment configuration...
    copy env.example .env
    echo [WARNING] Environment file created from template. Please edit .env with your configuration.
) else (
    echo [WARNING] Environment file already exists
)

REM Create necessary directories
echo [INFO] Creating necessary directories...
if not exist "logs" mkdir logs
if not exist "media" mkdir media
if not exist "static" mkdir static
echo [INFO] Directories created ✓

REM Setup database
echo [INFO] Setting up database...
echo [INFO] Please ensure PostgreSQL is running and create database 'learning_cloud' if it doesn't exist
echo [INFO] You can create it with: createdb learning_cloud

REM Run Prisma migrations
echo [INFO] Running Prisma migrations...
npx prisma migrate dev --name init
echo [INFO] Prisma migrations completed ✓

REM Generate Prisma client
echo [INFO] Generating Prisma client...
npx prisma generate
echo [INFO] Prisma client generated ✓

REM Run Django migrations
echo [INFO] Running Django migrations...
python manage.py migrate
echo [INFO] Django migrations completed ✓

REM Create superuser
echo [INFO] Creating Django superuser...
echo Please create a superuser account:
python manage.py createsuperuser
echo [INFO] Superuser created ✓

REM Collect static files
echo [INFO] Collecting static files...
python manage.py collectstatic --noinput
echo [INFO] Static files collected ✓

echo [INFO] 🎉 Setup completed successfully!
echo.
echo [INFO] Next steps:
echo [INFO] 1. Edit .env file with your configuration
echo [INFO] 2. Start the development server: python manage.py runserver
echo [INFO] 3. Start Celery worker: celery -A learning_cloud worker -l info
echo [INFO] 4. Access the admin panel at: http://localhost:8000/admin/
echo.
echo [INFO] For production deployment, see README.md

pause
