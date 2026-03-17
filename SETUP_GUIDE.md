# Laptop Control Application - Complete Setup Guide

## Project Overview

This is a production-grade remote laptop control system with three main components:

- **Frontend**: Flutter Mobile App
- **Backend**: FastAPI Server
- **Agent**: Python WebSocket Client (runs on laptop)

### Architecture Flow
```
Mobile App → REST API → Backend Server ← WebSocket ← Laptop Agent
                ↑
            Database
```

## Prerequisites

### For Backend
- Python 3.11+
- pip or conda
- PostgreSQL (optional, SQLite by default)

### For Laptop Agent
- Python 3.11+
- pip or conda
- OS: Windows, macOS, or Linux

### For Mobile App
- Flutter SDK 3.0+
- Android Studio or Xcode
- iOS or Android device/emulator

---

## Backend Setup

### Step 1: Install Dependencies

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### Step 2: Configure Environment

Create `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` and set your configuration:

```env
ENV=development
DEBUG=true
DATABASE_URL=sqlite:///./laptop_control.db
SECRET_KEY=your-super-secret-key-12345
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=*
LOG_LEVEL=INFO
```

### Step 3: Initialize Database

```bash
python -c "from app.models.database import create_tables; create_tables()"
```

### Step 4: Run Backend

```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```

Backend will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

---

## Laptop Agent Setup

### Step 1: Install Dependencies

```bash
cd laptop_agent
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### Step 2: Register Laptop Device

First, use the backend API to register your laptop:

```bash
# Register device via REST API (or use Mobile App)
curl -X POST http://localhost:8000/devices/register \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "laptop-001",
    "device_name": "My Laptop",
    "device_type": "laptop"
  }'
```

You'll receive a response with `api_token`. Save this!

### Step 3: Configure Environment

Create `.env` file:

```bash
cp .env.example .env
```

Edit `.env`:

```env
BACKEND_URL=ws://localhost:8000
API_TOKEN=your-token-from-registration
DEVICE_ID=laptop-001
DEVICE_NAME=My Laptop
METRICS_INTERVAL=30
LOG_LEVEL=INFO
```

### Step 4: Run Agent

```bash
python agent.py
```

You should see:
```
Starting Laptop Control Agent
Device ID: laptop-001
Backend URL: ws://localhost:8000
Connected to WebSocket server
```

### Step 5: Setup Auto-Start (Optional)

#### Windows
Create a batch file `start_agent.bat`:
```batch
@echo off
cd C:\path\to\project\laptop_agent
python agent.py
pause
```

Add to Windows Task Scheduler to run on startup.

#### macOS
Create `~/.local/launchd/com.laptopcontrol.agent.plist` or use:
```bash
brew install python
mkdir -p ~/Library/LaunchAgents
# Create plist file for auto-start
```

#### Linux
Create systemd service:
```bash
sudo nano /etc/systemd/system/laptop-agent.service
```

```ini
[Unit]
Description=Laptop Control Agent
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/laptop_agent
ExecStart=/usr/bin/python3 agent.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable laptop-agent
sudo systemctl start laptop-agent
```

---

## Mobile App Setup

### Step 1: Install Flutter

```bash
# Download Flutter SDK
# Follow instructions at: https://flutter.dev/docs/get-started/install
flutter doctor
```

### Step 2: Configure API Endpoint

Edit `lib/main.dart`:

```dart
Provider<ApiService>(
  create: (_) => ApiService(
    baseUrl: 'http://your-backend-url:8000',
  ),
),
```

### Step 3: Get Dependencies

```bash
cd mobile_app
flutter pub get
```

### Step 4: Run App

```bash
# Android
flutter run -d android

# iOS
flutter run -d ios

# Web (for testing)
flutter run -d chrome
```

### Step 5: Build for Release

```bash
# Android APK
flutter build apk --release

# iOS
flutter build ios --release

# Web
flutter build web --release
```

Built files will be in `build/` directory.

---

## Docker Deployment

### Option 1: Local Docker Compose

#### Backend Only

```bash
cd backend
docker-compose up -d
```

#### Laptop Agent

```bash
cd laptop_agent
docker-compose up -d
```

#### Full Stack (Development)

```bash
docker-compose -f docker-compose.yml up -d
```

### Option 2: Production Deployment (Render.com)

#### Backend Deployment

1. Push your code to GitHub
2. Create new Web Service on Render
3. Connect GitHub repository
4. Set environment variables:
   - `DATABASE_URL`: Your PostgreSQL URL
   - `SECRET_KEY`: Strong random key
   - `ENVIRONMENT`: production
   - `CORS_ORIGINS`: Your frontend domain

5. Build command: `pip install -r requirements.txt && python deploy.py`
6. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Option 3: Vercel / Netlify (Mobile App)

```bash
# Build for web deployment
flutter build web

# Deploy to Vercel
vercel --prod
```

---

## API Endpoints Reference

### Device Management

#### Register Device
```
POST /devices/register
Content-Type: application/json

{
  "device_id": "laptop-001",
  "device_name": "My Laptop",
  "device_type": "laptop"
}

Response:
{
  "device_id": "laptop-001",
  "device_name": "My Laptop",
  "device_type": "laptop",
  "api_token": "token_here",
  "is_active": true,
  "last_online": "2024-01-01T12:00:00"
}
```

#### Get Device
```
GET /devices/{device_id}
Authorization: Bearer {api_token}
```

#### Activate/Deactivate Device
```
PUT /devices/{device_id}/activate
PUT /devices/{device_id}/deactivate
```

### Command Execution

#### Execute Command
```
POST /commands/execute/{target_device_id}
Authorization: Bearer {api_token}
Content-Type: application/json

{
  "command_name": "open_chrome",
  "command_params": {
    "url": "https://google.com"
  }
}
```

#### Get Command History
```
GET /commands/history/{device_id}?limit=50
Authorization: Bearer {api_token}
```

#### Get Command Status
```
GET /commands/{command_id}
Authorization: Bearer {api_token}
```

### System Metrics

#### Record Metrics
```
POST /metrics/
Authorization: Bearer {api_token}
Content-Type: application/json

{
  "cpu_percent": 45,
  "memory_percent": 60,
  "disk_percent": 70,
  "temperature": 65,
  "battery_percent": 85,
  "is_charging": true
}
```

#### Get Latest Metrics
```
GET /metrics/{device_id}/latest
Authorization: Bearer {api_token}
```

#### Get Metrics History
```
GET /metrics/{device_id}/history?limit=100
Authorization: Bearer {api_token}
```

---

## Supported Commands

### System Commands

| Command | Parameters | Description |
|---------|------------|-------------|
| `open_chrome` | `url` (optional) | Open Google Chrome |
| `open_whatsapp` | - | Open WhatsApp |
| `take_screenshot` | - | Capture screenshot |
| `system_info` | - | Get system information |
| `shutdown` | `delay` (optional, seconds) | Shutdown system |
| `restart` | `delay` (optional, seconds) | Restart system |
| `run_script` | `script_path` (required) | Execute Python script |

### Example Command Executions

```bash
# Open Chrome
curl -X POST http://localhost:8000/commands/execute/laptop-001 \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "command_name": "open_chrome",
    "command_params": {"url": "https://google.com"}
  }'

# Take Screenshot
curl -X POST http://localhost:8000/commands/execute/laptop-001 \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{"command_name": "take_screenshot"}'

# System Shutdown (60 seconds delay)
curl -X POST http://localhost:8000/commands/execute/laptop-001 \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{"command_name": "shutdown", "command_params": {"delay": 60}}'
```

---

## Troubleshooting

### Backend Issues

**Port already in use:**
```bash
# Windows
netstat -ano | findstr :8000

# macOS/Linux
lsof -i :8000
```

**Database errors:**
```bash
# Reset database
rm laptop_control.db
python -c "from app.models.database import create_tables; create_tables()"
```

### Agent Issues

**WebSocket connection refused:**
- Check backend is running at correct URL
- Verify API_TOKEN is correct
- Check firewall settings

**Commands not executing:**
- Check agent logs in `logs/` directory
- Verify command is supported on your OS
- Check required dependencies are installed

### Mobile App Issues

**API connection failed:**
- Check backend URL is correct
- Ensure CORS_ORIGINS includes mobile domain
- Check network connectivity

**Registration fails:**
- Let sure backend is running
- Check for typos in device name
- Verify no duplicate device IDs

---

## Security Best Practices

1. **Change Secret Key**: Update `SECRET_KEY` in production
2. **Use HTTPS**: Always use HTTPS in production
3. **Database**: Use PostgreSQL in production, not SQLite
4. **API Token**: Keep API tokens secret and rotate periodically
5. **CORS**: Set specific origins in production, not `*`
6. **Firewall**: Restrict WebSocket access to trusted networks
7. **SSL Certificates**: Use Let's Encrypt for free SSL
8. **Rate Limiting**: Implement rate limiting for API endpoints
9. **Input Validation**: All inputs are validated and sanitized
10. **Logging**: Monitor logs for suspicious activity

---

## Performance Optimization

### Backend
- Use PostgreSQL for production
- Enable connection pooling
- Cache frequently accessed data
- Implement rate limiting
- Use Uvicorn with multiple workers

### Agent
- Batch metric collection
- Compress screenshot transfers
- Implement command queuing
- Use async/await for I/O operations

### Mobile App
- Implement local caching
- Use image compression
- Lazy load data
- Implement pagination for lists

---

## Monitoring and Logging

### Backend Logs
Logs are stored in `backend/logs/` directory:
- `laptop_control.log`: General application logs
- `websocket_routes.log`: WebSocket connection events
- `websocket_manager.log`: WebSocket message events

### Agent Logs
Logs are stored in `laptop_agent/logs/` directory:
- `agent.log`: Main agent logs
- Command execution logs

### Run Diagnostics

```bash
# Check backend health
curl http://localhost:8000/health

# Check connected devices
curl http://localhost:8000/devices/

# Monitor metrics
curl http://localhost:8000/metrics/laptop-001/latest
```

---

## Advanced Configuration

### Custom Database
Edit `.env`:
```env
DATABASE_URL=postgresql://user:password@localhost/laptop_control
```

### Environment Modes
```env
ENV=development    # Development with debug info
ENV=production     # Production optimized
ENV=testing        # Testing with in-memory database
```

### Custom Logging
Edit `app/utils/logger.py`:
```python
LOG_LEVEL = "DEBUG"  # Debug, Info, Warning, Error, Critical
```

---

## Support and Contribution

For issues, questions, or contributions, please follow the project guidelines.

---

## License

This project is provided as-is for educational and commercial use.

---

## Version History

### v1.0.0 (Current)
- Initial release
- Basic device management
- Command execution
- System metrics monitoring
- WebSocket communication
- Flutter mobile app
- Production-ready backend

---

**Last Updated**: January 2024
