# Project File Structure and Descriptions

## Root Directory Files

```
laptop_control/
├── README.md                          # Main project documentation
├── QUICKSTART.md                      # 5-minute quick start guide
├── SETUP_GUIDE.md                     # Detailed setup instructions
├── API_DOCUMENTATION.md               # Complete API reference
├── postman_collection.json            # Postman API collection
├── setup.sh                           # Linux/macOS automatic setup
├── setup.bat                          # Windows automatic setup
├── docker-compose.production.yml      # Production Docker compose
└── THIS_FILE                          # File structure index
```

---

## Backend Directory (`/backend`)

### Main Files
```
backend/
├── requirements.txt                   # Python dependencies
├── config.py                          # Configuration management
├── .env.example                       # Environment variables template
├── Dockerfile                         # Docker image for backend
├── docker-compose.yml                 # Docker compose for backend
├── deploy.py                          # Deployment helper script
└── app/                               # Main application package
```

### Application Code
```
app/
├── __init__.py                        # Package initialization
├── main.py                            # FastAPI application setup
│                                       # - App instance creation
│                                       # - Middleware setup
│                                       # - Router inclusion
│                                       # - Exception handlers
│                                       # - Health check endpoints
│
├── models/
│   ├── __init__.py                    # Package initialization
│   ├── database.py                    # Database configuration
│   │                                   # - SQLAlchemy setup
│   │                                   # - Session management
│   │                                   # - Table creation
│   └── models.py                      # SQLAlchemy ORM models
│                                       # - Device model
│                                       # - Command model
│                                       # - SystemMetrics model
│                                       # - CommandStatus enum
│
├── schemas/
│   ├── __init__.py                    # Package initialization
│   └── schemas.py                     # Pydantic validation schemas
│                                       # - DeviceRegister
│                                       # - DeviceResponse
│                                       # - CommandRequest
│                                       # - CommandResponse
│                                       # - SystemMetricsRequest/Response
│                                       # - AuthToken
│                                       # - ErrorResponse
│
├── routes/
│   ├── __init__.py                    # Package initialization
│   ├── devices.py                     # Device management endpoints
│   │                                   # - POST /devices/register
│   │                                   # - GET /devices/{id}
│   │                                   # - PUT /devices/{id}/activate
│   │                                   # - PUT /devices/{id}/deactivate
│   │                                   # - DELETE /devices/{id}
│   │
│   ├── commands.py                    # Command execution endpoints
│   │                                   # - POST /commands/execute
│   │                                   # - GET /commands/history
│   │                                   # - GET /commands/{id}
│   │
│   └── metrics.py                     # System metrics endpoints
│                                       # - POST /metrics/
│                                       # - GET /metrics/{id}/latest
│                                       # - GET /metrics/{id}/history
│
├── websockets/
│   ├── __init__.py                    # Package initialization
│   ├── manager.py                     # WebSocket connection manager
│   │                                   # - Connection tracking
│   │                                   # - Message routing
│   │                                   # - Device status management
│   │
│   └── routes.py                      # WebSocket endpoints
│                                       # - WS /ws/{api_token}
│                                       # - Message handlers
│
└── utils/
    ├── __init__.py                    # Package initialization
    ├── security.py                    # Authentication & security
    │                                   # - Token generation
    │                                   # - Token validation
    │
    ├── logger.py                      # Logging configuration
    │                                   # - File handlers
    │                                   # - Console handlers
    │                                   # - Formatting
    │
    └── helpers.py                     # Helper utilities
                                        # - JSON conversion
                                        # - Timestamp handling
                                        # - Time calculations
```

---

## Laptop Agent Directory (`/laptop_agent`)

### Main Files
```
laptop_agent/
├── requirements.txt                   # Python dependencies
├── agent.py                           # Main agent application
├── .env.example                       # Environment variables template
├── monitor.py                         # System monitoring
├── websocket_client.py                # WebSocket client
├── Dockerfile                         # Docker image for agent
├── docker-compose.yml                 # Docker compose for agent
└── commands/                          # Command execution modules
```

### Commands Module
```
commands/
├── __init__.py                        # Package initialization & registry
├── base.py                            # Base command class
│                                       # - Abstract execute method
│                                       # - Result handling
│
└── executor.py                        # Command implementations
                                        # - OpenChromeCommand
                                        # - OpenWhatsAppCommand
                                        # - ShutdownCommand
                                        # - RestartCommand
                                        # - TakeScreenshotCommand
                                        # - SystemInfoCommand
                                        # - RunScriptCommand
                                        # - Command registry
```

### Key Files Details

**agent.py**
- Main event loop
- WebSocket connection management
- Command handling and dispatch
- Metrics collection and reporting
- Signal handling for graceful shutdown

**websocket_client.py**
- WebSocket protocol implementation
- Reconnection logic with exponential backoff
- Message serialization/deserialization
- Connection lifecycle management

**monitor.py**
- System resource monitoring
- CPU/Memory/Disk/Battery metrics
- Process counting
- Cross-platform compatibility

---

## Mobile App Directory (`/mobile_app`)

### Main Files
```
mobile_app/
├── pubspec.yaml                       # Flutter dependencies & config
├── lib/
│   ├── main.dart                      # App entry point
│   │                                   # - Material theme
│   │                                   # - Provider setup
│   │                                   # - Splash screen
│   │
│   ├── models/
│   │   └── models.dart                # Data models
│   │                                   # - ApiResponse
│   │                                   # - Device
│   │                                   # - Command
│   │                                   # - SystemMetrics
│   │
│   ├── services/
│   │   └── api_service.dart           # API client
│   │                                   # - Device registration
│   │                                   # - Command execution
│   │                                   # - Metrics querying
│   │                                   # - HTTP/REST methods
│   │
│   └── screens/
│       ├── login_screen.dart          # Registration/Login
│       │                                # - Device name input
│       │                                # - Registration flow
│       │
│       └── dashboard_screen.dart      # Main dashboard
                                        # - Command buttons
                                        # - Device selection
                                        # - Metrics display
```

### pubspec.yaml Contents
- Flutter SDK version constraint
- Dependencies:
  - http (REST client)
  - provider (state management)
  - shared_preferences (local storage)
  - uuid (unique ID generation)
  - cupertino_icons (iOS icons)

---

## Configuration Files

### Environment Templates

**backend/.env.example**
```
ENV=development
DEBUG=true
DATABASE_URL=sqlite:///./laptop_control.db
SECRET_KEY=your-secret-key
LOG_LEVEL=INFO
CORS_ORIGINS=*
```

**laptop_agent/.env.example**
```
BACKEND_URL=ws://localhost:8000
API_TOKEN=your-api-token
DEVICE_ID=laptop-001
METRICS_INTERVAL=30
LOG_LEVEL=INFO
```

### Docker Files

**backend/Dockerfile**
- Python 3.11 slim base image
- Dependency installation
- Application setup
- Port exposure (8000)
- Health check endpoint

**laptop_agent/Dockerfile**
- Python 3.11 slim base image
- System dependencies for GUI/display
- Python dependencies
- Directory structure creation
- Agent startup

---

## Documentation Files

### README.md
- Project overview
- Feature list
- Technology stack
- Project structure overview
- Getting started links
- Support information

### QUICKSTART.md
- 5-minute setup
- Step-by-step instructions
- Terminal commands
- Testing with curl
- Troubleshooting basics

### SETUP_GUIDE.md
- Detailed prerequisites
- Backend installation & configuration
- Laptop agent setup & auto-start
- Mobile app setup & building
- Docker deployment options
- API endpoint reference
- Command reference
- Troubleshooting guide
- Security best practices
- Performance optimization

### API_DOCUMENTATION.md
- System architecture diagrams
- Data flow diagrams
- Database schema
- Complete endpoint documentation
- Request/response examples
- Authentication details
- Error responses
- WebSocket message formats
- Code examples
- Deployment checklist

### postman_collection.json
- Pre-configured API requests
- Environment variables
- All endpoints included
- Example payloads
- Ready to import into Postman

---

## Setup Scripts

**setup.sh** (Linux/macOS)
- Automated backend setup
- Automated agent setup
- Virtual environment creation
- Dependency installation
- Database initialization
- Status reporting

**setup.bat** (Windows)
- Automated backend setup
- Automated agent setup
- Virtual environment creation
- Dependency installation
- Database initialization
- Status reporting

---

## Key Technologies in Each File

### Backend
- **FastAPI** (main.py): Web framework
- **SQLAlchemy** (models.py): ORM
- **Pydantic** (schemas.py): Data validation
- **WebSockets** (websockets/): Real-time communication
- **asyncio** (main.py): Async operations

### Agent
- **asyncio** (agent.py): Async event loop
- **websockets** (websocket_client.py): WebSocket protocol
- **psutil** (monitor.py): System monitoring
- **subprocess** (commands/executor.py): Command execution
- **PIL** (commands/executor.py): Screenshot capture

### Mobile App
- **Flutter** (lib/main.dart): UI framework
- **Provider** (main.dart): State management
- **http** (services/api_service.dart): HTTP client
- **shared_preferences** (screens/login_screen.dart): Local storage
- **Material Design** (screens/): UI design system

---

## File Dependencies & Imports

```
main.dart
  ├── services/api_service.dart
  ├── screens/login_screen.dart
  └── screens/dashboard_screen.dart
         └── models/models.dart

api_service.dart
  └── models/models.dart

app/main.py
  ├── routes/devices.py
  ├── routes/commands.py
  ├── routes/metrics.py
  └── websockets/routes.py
       └── websockets/manager.py
            └── models/models.py

agent.py
  ├── commands/__init__.py
  │   └── executor.py
  │        └── base.py
  ├── monitor.py
  └── websocket_client.py
```

---

## Configuration Hierarchy

```
Environment Variables (.env)
         ↓
config.py (Configuration Classes)
         ↓
app/main.py (Application Instance)
         ↓
routes/ (Endpoint Handlers)
│   ├── devices.py
│   ├── commands.py
│   └── metrics.py
│
websockets/ (Real-time Communication)
│   ├── manager.py
│   └── routes.py
│
utils/ (Supporting Functions)
    ├── security.py
    ├── logger.py
    └── helpers.py
```

---

## Total File Count

- **Backend**: 15 files (code) + 4 files (config/docker)
- **Agent**: 6 files (code) + 3 files (config/docker)
- **Mobile App**: 5 files (code) + 1 file (config)
- **Documentation**: 6 files
- **Configuration**: 2 files (setup scripts) + 1 file (postman)
- **Total**: ~43 files

---

## Deployment File Organization

```
Production Deployment
├── docker-compose.production.yml
│   ├── FastAPI backend service
│   ├── PostgreSQL database
│   └── Volume management
│
Remote (Render.com)
├── README.md
├── requirements.txt
├── app/
└── Procfile (auto-generated)

Mobile Deployment
├── flutter build apk --release
├── flutter build ios --release
└── flutter build web --release
```

---

## Backup & Version Control

Recommended `.gitignore` entries:
```
venv/
__pycache__/
*.db
.env
.DS_Store
*.pyc
build/
dist/
node_modules/
logs/
screenshots/
.flutter-plugins
```

---

## Quick File Reference

| Task | File |
|------|------|
| Start backend | `backend/app/main.py` |
| API endpoints | `backend/app/routes/` |
| Database setup | `backend/app/models/database.py` |
| Run agent | `laptop_agent/agent.py` |
| Add command | `laptop_agent/commands/executor.py` |
| Mobile UI | `mobile_app/lib/screens/` |
| API client | `mobile_app/lib/services/api_service.dart` |
| Setup | `setup.sh` or `setup.bat` |
| Quick help | `QUICKSTART.md` |
| Full docs | `SETUP_GUIDE.md` |
| API ref | `API_DOCUMENTATION.md` |

---

**Last Updated**: January 2024
**Version**: 1.0.0
