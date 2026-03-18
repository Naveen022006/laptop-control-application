# Setup & Deployment Guide

Complete step-by-step guide for setting up and deploying the Laptop Control Application.

## Table of Contents

1. [Local Development Setup](#local-development-setup)
2. [Production Deployment](#production-deployment)
3. [Troubleshooting](#troubleshooting)
4. [Best Practices](#best-practices)

---

## Local Development Setup

### 1. Backend Setup

#### Step 1: Clone and Navigate

```bash
cd laptop-control-system/backend
```

#### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

#### Step 4: Setup Environment

```bash
# Copy example env
cp .env.example .env

# Edit .env with your values
# nano .env  (or use your editor)
```

**Default .env for Development:**
```env
DATABASE_URL=sqlite:///./laptop_control.db
SECRET_KEY=dev-secret-key-change-in-production
ENVIRONMENT=development
LOG_LEVEL=INFO
CORS_ORIGINS=["http://localhost:3000","http://localhost:8100"]
```

#### Step 5: Initialize Database

```bash
python -c "from app.database import init_db; init_db()"
```

This creates `laptop_control.db` with all required tables.

#### Step 6: Run Backend

```bash
python run.py
```

Backend runs at: `http://localhost:8000`

**Health Check:**
```bash
curl http://localhost:8000/health
```

**API Documentation:**
- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

### 2. Laptop Agent Setup

#### Step 1: Navigate to Agent Directory

```bash
cd laptop-control-system/agent
```

#### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

#### Step 4: Create API Token (from Backend)

1. Start backend first
2. Register user and login:

```bash
# Register user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user1",
    "email": "user@example.com",
    "password": "password123"
  }'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user1",
    "password": "password123"
  }'
```

Get the `access_token` from response.

3. Create API token:

```bash
curl -X POST http://localhost:8000/auth/token/create \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "laptop-device",
    "expires_in_days": 30
  }'
```

#### Step 5: Setup Environment

```bash
cp .env.example .env
```

**Edit .env:**
```env
DEVICE_ID=laptop-001
DEVICE_NAME=My Laptop
BACKEND_URL=ws://localhost:8000
API_TOKEN=your-api-token-from-step-4
RECONNECT_DELAY=5
MAX_RECONNECT_ATTEMPTS=10
MESSAGE_TIMEOUT=60
COMMAND_TIMEOUT=30
ENABLE_SYSTEM_COMMANDS=true
LOG_LEVEL=INFO
```

#### Step 6: Run Agent

```bash
python agent.py
```

You should see:
```
2024-01-15 10:30:45 - __main__ - INFO - Starting Laptop Control Agent: laptop-001
2024-01-15 10:30:45 - __main__ - INFO - Connecting to ws://localhost:8000/ws/device/laptop-001
2024-01-15 10:30:46 - __main__ - INFO - Connected to backend: ws://localhost:8000/ws/device/laptop-001
```

---

### 3. Mobile App Setup

#### Step 1: Navigate to Mobile App

```bash
cd laptop-control-system/mobile_app
```

#### Step 2: Install Flutter Dependencies

```bash
flutter pub get
```

#### Step 3: Update API Configuration

Edit `lib/config/app_config.dart`:

```dart
class AppConfig {
  static const String apiBaseUrl = 'http://localhost:8000';
  static const String wsBaseUrl = 'ws://localhost:8000';
  // ...
}
```

For physical device on same network, use your machine's IP:
```dart
static const String apiBaseUrl = 'http://192.168.x.x:8000';
```

#### Step 4: Run App

**On Emulator:**
```bash
flutter run
```

**On Physical Device:**
```bash
flutter run -d <device_id>
```

**Platform-specific:**
```bash
# iOS
flutter run -d ios

# Android
flutter run -d android

# Web
flutter run -d chrome
```

#### Step 5: Login

1. Register new account or use existing credentials
2. Login with username and password
3. Dashboard shows available devices

---

## Production Deployment

### 1. Deploy Backend on Render

#### Prerequisites

- Render account (https://render.com)
- GitHub repository
- PostgreSQL database (Render provides)

#### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git push -u origin main
```

#### Step 2: Create Render Web Service

1. Login to Render dashboard
2. Click "New +"
3. Select "Web Service"
4. Connect GitHub repository
5. Configure:

**Build Command:**
```bash
pip install -r backend/requirements.txt
```

**Start Command:**
```bash
cd backend && python run.py
```

#### Step 3: Set Environment Variables

In Render dashboard, add environment variables:

```
DATABASE_URL=postgresql://user:pass@host:5432/dbname
SECRET_KEY=your-production-secret-key-min-32-chars
ENVIRONMENT=production
LOG_LEVEL=INFO
CORS_ORIGINS=["https://yourdomain.com","https://app.yourdomain.com"]
```

#### Step 4: Configure PostgreSQL

1. Create PostgreSQL database on Render
2. Get connection string
3. Set as DATABASE_URL

#### Step 5: Deploy

Click "Create Web Service" - Render automatically deploys on push to main branch.

---

### 2. Deploy Laptop Agent

#### As Background Service (Windows)

**Create batch file `C:\LaptopAgent\start.bat`:**
```batch
@echo off
cd C:\LaptopAgent
pip install -r requirements.txt
python agent.py
```

**Create Task Scheduler entry:**
1. Open Task Scheduler
2. Create Task
3. General: Name "Laptop Control Agent"
4. Triggers: At startup
5. Actions: Run `start.bat`
6. Settings: Run with highest privileges, Run whether logged in or not

#### As Service (Linux/macOS)

**Create systemd service `/etc/systemd/system/laptop-agent.service`:**
```ini
[Unit]
Description=Laptop Control Agent
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/laptop-agent
ExecStart=/home/ubuntu/laptop-agent/venv/bin/python agent.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl enable laptop-agent
sudo systemctl start laptop-agent
sudo systemctl status laptop-agent
```

---

### 3. Deploy Mobile App

#### Android APK

```bash
cd mobile_app
flutter build apk --release
```

APK location: `build/app/outputs/flutter-apk/app-release.apk`

#### iOS Build

```bash
flutter build ios --release
```

#### Web Deployment

```bash
flutter build web
# Upload files from build/web to hosting service
```

---

## Troubleshooting

### Backend Issues

#### Port 8000 already in use

```bash
# Find process using port
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # Mac/Linux
taskkill /PID <PID> /F  # Windows
```

#### Database connection error

```bash
# Check if SQLite file exists
ls laptop_control.db

# Reinitialize database
rm laptop_control.db
python -c "from app.database import init_db; init_db()"
```

#### WebSocket connection refused

1. Verify backend is running
2. Check firewall settings
3. Verify WEBSOCKET_PORT in config

### Agent Issues

#### Connection timeout

1. Check `BACKEND_URL` in `.env`
2. Verify backend is accessible
3. Check network connectivity
4. Review `agent.log` file

#### Command execution failed

1. Check command permissions
2. Verify OS compatibility
3. Review error in logs
4. Test command manually

### Mobile App Issues

#### Cannot connect to backend

1. Check API_BASE_URL configuration
2. On physical device: use correct IP address
3. Check firewall/network settings
4. Verify backend is running

#### Blank device list

1. Register device from agent
2. Verify device token is valid
3. Check if device is online
4. Review app logs

---

## Best Practices

### Security

1. **Change default secrets:**
   ```
   SECRET_KEY - use cryptographically strong random string
   DB passwords - use strong passwords
   API tokens - rotate regularly
   ```

2. **Use HTTPS/WSS in production**
   ```
   Update URLs to use https:// and wss://
   ```

3. **Restrict CORS origins**
   ```
   Only allow trusted domains in CORS_ORIGINS
   ```

4. **Enable rate limiting** (add to FastAPI)
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   ```

### Performance

1. **Enable Redis caching** (optional)
   ```python
   # Cache frequently accessed data
   # Cache command results temporarily
   ```

2. **Database optimization**
   ```python
   # Add indexes to frequently queried columns
   # Regular cleanup of old commands
   ```

3. **WebSocket optimization**
   ```python
   # Compress large messages
   # Batch multiple commands
   ```

### Monitoring

1. **Setup logging**
   ```python
   # Use ELK stack or CloudWatch
   # Monitor critical errors
   ```

2. **Database backups**
   ```bash
   # Daily PostgreSQL backups
   # Store in S3 or cloud storage
   ```

3. **Uptime monitoring**
   ```
   # Use services like UptimeRobot
   # Alert on downtime
   ```

### Maintenance

1. **Regular updates**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. **Database cleanup**
   ```python
   CommandService.cleanup_old_commands(db, days=30)
   ```

3. **Token rotation**
   ```bash
   Revoke old tokens periodically
   ```

---

## Support

For issues:
1. Check logs: `backend/app.log`, `agent/agent.log`
2. Review error messages carefully
3. Test individual components
4. Check network connectivity
5. Verify environment configuration

For more help, review the main README.md and API documentation.
