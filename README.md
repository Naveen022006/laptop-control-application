# Laptop Control Application - Complete System

A production-ready remote laptop control system with real-time communication between a Flutter mobile app, FastAPI backend, and Python laptop agent.

## 🎯 Features

- **Real-time Command Execution**: Send commands via WebSocket with <1 second latency
- **Device Management**: Register and manage multiple laptops
- **Secure Authentication**: Token-based authentication with JWT
- **Command Queue**: Offline device command queuing
- **Auto-reconnection**: Automatic reconnection with exponential backoff
- **System Monitoring**: Real-time CPU, memory, and disk usage tracking
- **Screenshot Capture**: Remote screenshot functionality
- **Cross-platform Support**: Windows, macOS, and Linux support

## 🗂 Project Structure

```
laptop-control-system/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py         # FastAPI application
│   │   ├── config.py       # Configuration
│   │   ├── database.py     # Database setup
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── routes/         # API routes
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utilities
│   ├── requirements.txt
│   └── run.py
├── agent/                   # Python Laptop Agent
│   ├── agent.py            # Main agent
│   ├── command_executor.py # Command execution
│   ├── config.py           # Agent config
│   ├── requirements.txt
│   └── .env.example
├── mobile_app/             # Flutter Mobile App
│   ├── lib/
│   │   ├── main.dart       # Entry point
│   │   ├── config/         # App configuration
│   │   ├── models/         # Data models
│   │   ├── services/       # API service
│   │   ├── providers/      # State management
│   │   └── screens/        # UI screens
│   └── pubspec.yaml
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Flutter SDK
- Git
- PostgreSQL or SQLite

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python -c "from app.database import init_db; init_db()"

# Run server
python run.py
```

The backend will start at `http://localhost:8000`

### Laptop Agent Setup

```bash
cd agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your device ID and API token

# Run agent
python agent.py
```

### Mobile App Setup

```bash
cd mobile_app

# Get dependencies
flutter pub get

# Run on device/emulator
flutter run
```

## 📡 API Endpoints

### Authentication

```
POST   /auth/register         - Register new user
POST   /auth/login            - Login user
POST   /auth/token/create     - Create API token
GET    /auth/tokens           - Get user tokens
DELETE /auth/token/{token_id} - Revoke token
```

### Devices

```
POST   /devices/register      - Register device
GET    /devices/              - List user devices
GET    /devices/{device_id}   - Get device details
PATCH  /devices/{device_id}/status - Update device status
GET    /devices/{device_id}/stats   - Get device statistics
DELETE /devices/{device_id}   - Delete device
```

### Commands

```
POST   /commands/             - Send command
GET    /commands/{command_id} - Get command status
GET    /commands/device/{device_id}        - Get device commands
GET    /commands/device/{device_id}/history - Get command history
```

### WebSocket

```
WS /ws/device/{device_id} - Device WebSocket connection
```

## 🔄 Communication Flow

```
Mobile App (Flutter)
    ↓
    └─→ REST API (POST /commands/)
        ↓
Backend (FastAPI)
    ├─→ Store command in database
    └─→ Send via WebSocket to connected agent
        ↓
Laptop Agent (Python)
    ├─→ Receive command
    ├─→ Execute locally
    └─→ Send result via WebSocket
        ↓
Backend (FastAPI)
    ├─→ Update command in database
    └─→ Return result to mobile app
        ↓
Mobile App (Flutter)
    └─→ Display result to user
```

## 🔐 Security Features

- **JWT Authentication**: Secure token-based auth
- **Device Registration**: Each device has unique ID
- **API Tokens**: Long-lived tokens for device access
- **Command Verification**: All commands verified before execution
- **Secure Storage**: Passwords hashed with bcrypt
- **CORS Protection**: Restricted origin access

## ⚙️ Deployment

### Deploy Backend on Render

1. Create Render account and connect GitHub
2. Create new Web Service
3. Set environment variables:
   ```
   DATABASE_URL=postgresql://user:password@host/db
   SECRET_KEY=your-secret-key
   ENVIRONMENT=production
   ```
4. Deploy!

### Deploy Laptop Agent

1. Install on target laptop
2. Configure `.env` with backend URL
3. Set as startup service/task
4. Agent auto-connects on startup

## 📊 Supported Commands

### Core Commands

- `open_chrome` - Open Chrome browser
- `open_whatsapp_web` - Open WhatsApp Web
- `take_screenshot` - Capture screenshot
- `system_info` - Get system information
- `system_metrics` - Get CPU/Memory/Disk metrics
- `open_file` - Open file with default app
- `get_processes` - List running processes
- `lock_screen` - Lock the screen
- `shutdown` - Shutdown laptop
- `restart` - Restart laptop
- `run_python_script` - Execute Python code

## 📱 Mobile App Features

- Clean Material Design UI
- Real-time device status updates
- Command execution with status tracking
- Command history view
- Device management
- Secure token storage
- Offline handling

## 🔧 Configuration

### Backend Config (app/config.py)

```python
DATABASE_URL = "sqlite:///./laptop_control.db"
SECRET_KEY = "your-secret-key"
CORS_ORIGINS = ["http://localhost:3000"]
WS_HEARTBEAT_INTERVAL = 30
COMMAND_TIMEOUT = 30
```

### Agent Config (.env)

```
DEVICE_ID=laptop-001
DEVICE_NAME=My Laptop
BACKEND_URL=ws://localhost:8000
API_TOKEN=device-api-token
RECONNECT_DELAY=5
```

## 🧪 Testing

### Test Backend

```bash
cd backend
pip install pytest
pytest
```

### Test Mobile App

```bash
cd mobile_app
flutter test
```

## 📚 API Documentation

Full interactive API documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🐛 Troubleshooting

### Agent not connecting

1. Check `BACKEND_URL` environment variable
2. Verify backend is running
3. Check API token is valid
4. Review `agent.log` file

### Commands not executing

1. Verify device is online
2. Check command parameters
3. Review device logs
4. Ensure OS-level permissions

### Database errors

1. Verify DATABASE_URL is correct
2. Check database is running
3. Verify credentials
4. Run migrations

## 📝 License

MIT License - See LICENSE file

## 🤝 Contributing

Contributions welcome! Please submit pull requests with:
- Clear description
- Tests included
- Documentation updated

## 📞 Support

For issues and questions:
1. Check troubleshooting section
2. Review logs
3. Open GitHub issue
4. Contact support

---

Built with ❤️ using Flutter, FastAPI, and Python
