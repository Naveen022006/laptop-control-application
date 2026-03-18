# System Architecture & Design

Complete technical architecture of the Laptop Control Application.

## 🏗 System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                       User/Mobile Device                     │
│                    (Flutter Application)                     │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                   Presentation Layer                   │ │
│  │  • Login Screen                                        │ │
│  │  • Dashboard Screen                                    │ │
│  │  • Device Management UI                                │ │
│  │  • Command Execution UI                                │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                          ↓
                 REST API (HTTP/HTTPS)
                 (Stateless, Request/Response)
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                   Cloud Server (Render)                      │
│              (FastAPI Backend Application)                   │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                   Route Layer                          │ │
│  │  • /auth/* (Authentication)                            │ │
│  │  • /devices/* (Device Management)                      │ │
│  │  • /commands/* (Command Management)                    │ │
│  │  • /ws/* (WebSocket)                                   │ │
│  └────────────────────────────────────────────────────────┘ │
│                          ↓                                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                  Services Layer                        │ │
│  │  • AuthService                                         │ │
│  │  • DeviceService                                       │ │
│  │  • CommandService                                      │ │
│  │  • ConnectionManager (WebSocket)                       │ │
│  └────────────────────────────────────────────────────────┘ │
│                          ↓                                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                Database Layer                          │ │
│  │  • SQLAlchemy ORM                                      │ │
│  │  • PostgreSQL/SQLite                                   │ │
│  │  • Models: User, Device, Command, APIToken             │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                          ↓ ↑
         WebSocket (Persistent Connection)
         (Real-time, Bidirectional)
                          ↓ ↑
┌─────────────────────────────────────────────────────────────┐
│                   User's Laptop Device                       │
│             (Python Laptop Control Agent)                    │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              WebSocket Client Connection              │ │
│  │  • Connected to Backend                                │ │
│  │  • Listens for incoming commands                       │ │
│  │  • Auto-reconnect logic                                │ │
│  └────────────────────────────────────────────────────────┘ │
│                          ↓                                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │            Command Execution Engine                    │ │
│  │  • Command Router                                      │ │
│  │  • Process Management                                  │ │
│  │  • System Interaction (OS Commands)                    │ │
│  │  • Error Handling                                      │ │
│  └────────────────────────────────────────────────────────┘ │
│                          ↓                                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Local System Resources                    │ │
│  │  • Chrome/Applications                                 │ │
│  │  • File System                                         │ │
│  │  • System Information                                  │ │
│  │  • Screenshot Engine                                   │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Communication Flow

### Scenario 1: Send Command (Mobile → Backend → Agent)

```
┌──────────────┐
│  Mobile App  │
│ (Flutter)    │
└──────────────┘
       │
       │ 1. User taps "Take Screenshot"
       │
       ↓
┌──────────────┐
│ send_command()
└──────────────┘
       │
       │ 2. REST API POST /commands/
       │    - device_id: "laptop-001"
       │    - command_type: "take_screenshot"
       │
       ↓
┌──────────────────────────────┐
│     FastAPI Backend          │
│ POST /commands/              │
└──────────────────────────────┘
       │
       │ 3. CommandService.create_command()
       │    - Create DB record
       │    - Status: PENDING
       │
       ↓
┌──────────────────────────────┐
│   ConnectionManager check    │
│  Is device online?           │
└──────────────────────────────┘
       │
       ├─→ YES: Send via WebSocket
       │
       └─→ NO: Queue command
       │
       │ 4. WebSocket message sent
       │    {
       │      "type": "command",
       │      "command_id": "...",
       │      "command_type": "take_screenshot"
       │    }
       │
       ↓
┌──────────────────────────────┐
│   Laptop Agent (Python)      │
│ Receives on WebSocket        │
└──────────────────────────────┘
       │
       │ 5. handle_command()
       │
       ↓
┌──────────────────────────────┐
│  CommandExecutor.execute()   │
│  Runs: ImageGrab.grab()      │
└──────────────────────────────┘
       │
       │ 6. Convert to base64
       │    execution_time: 450ms
       │
       ↓
┌──────────────────────────────┐
│  Send result via WebSocket   │
│  {                           │
│    "type": "command_result", │
│    "status": "success",      │
│    "result": {...},          │
│    "execution_time": 450     │
│  }                           │
└──────────────────────────────┘
       │
       ↓
┌──────────────────────────────┐
│   FastAPI Backend            │
│ Receives command result      │
│ Updates DB                   │
│ Status: COMPLETED            │
└──────────────────────────────┘
       │
       │ 7. Backend stores result
       │    May notify mobile app
       │    (if polling)
       │
       ↓
┌──────────────────────────────┐
│   Mobile App polls status    │
│   GET /commands/{command_id} │
│                              │
│   Displays screenshot        │
└──────────────────────────────┘
```

### Scenario 2: Device Goes Offline

```
Connected Device (Online)
       │
       │ Connection drops
       ↓
Disconnected Device (Offline)
       │
       ├─→ Command queue stores pending commands
       │   (queued in memory)
       │
       └─→ Next command received
           └─→ Added to queue
               (not sent)

When device reconnects:
       │
       ├─→ WebSocket connection re-established
       │
       └─→ Backend sends queued commands
           └─→ Device executes
               └─→ All commands processed
```

---

## 📊 Data Models (ERD)

```
User
├── id (PK)
├── username (UNIQUE)
├── email (UNIQUE)
├── password_hash
├── is_active
├── created_at
└── updated_at
    │
    ├── 1: N → Device
    │          └── Device.user_id (FK)
    │
    └── 1: N → APIToken
               └── APIToken.user_id (FK)

Device
├── id (PK)
├── device_id (UNIQUE)
├── user_id (FK → User)
├── name
├── device_type
├── os_type
├── status (online/offline/idle)
├── last_seen
├── is_active
├── created_at
└── updated_at
    │
    └── 1: N → Command
               └── Command.device_id (FK)

Command
├── id (PK)
├── device_id (FK → Device)
├── command_type
├── parameters (JSON)
├── status (pending/sent/executing/completed/failed/timeout)
├── result (JSON)
├── error_message
├── execution_time (ms)
├── sent_at
├── executed_at
├── created_at
└── updated_at

APIToken
├── id (PK)
├── user_id (FK → User)
├── token (UNIQUE)
├── name
├── is_active
├── last_used
├── created_at
└── expires_at (nullable)
```

---

## 🔐 Security Architecture

### Authentication Flow

```
┌──────────────────┐
│   User Input     │
│ username/password│
└──────────────────┘
         │
         ↓
┌──────────────────┐
│  POST /login     │
└──────────────────┘
         │
         ↓
┌──────────────────────────┐
│ AuthService.authenticate_user()
│ • Lookup user by username
│ • Hash provided password
│ • Compare with stored hash
└──────────────────────────┘
         │
         ├─→ Match? YES
         │       │
         │       ↓
         │   ┌──────────────┐
         │   │ Create JWT   │
         │   │ Token        │
         │   └──────────────┘
         │       │
         │       ↓
         │   ┌──────────────┐
         │   │ Return token │
         │   │ to client    │
         │   └──────────────┘
         │
         └─→ Match? NO
                 │
                 ↓
             ┌──────────────┐
             │ Return 401   │
             │ Unauthorized │
             └──────────────┘

Subsequent Requests:
┌──────────────────────────┐
│ Authorization: Bearer JWT│
└──────────────────────────┘
         │
         ↓
┌──────────────────────────┐
│ decode_access_token()    │
│ • Verify signature       │
│ • Check expiration       │
│ • Extract user_id        │
└──────────────────────────┘
         │
         ├─→ Valid? YES → Allow request
         │
         └─→ Valid? NO → Return 401
```

### API Token (Device Authentication)

```
Create API Token:
  Device User → Mobile App → POST /auth/token/create
                                    ↓
                            APIToken created in DB
                            Token = random 32-char string
                                    ↓
                            Returned to user
                            (shown once)

Device Registration:
  User provides token
  Stores in agent .env
  Backend verifies token before accepting device connections

Device Connection:
  Agent connects via WebSocket
  Sends API token
  Backend verifies token validity
  Accept/Reject connection
```

### Data Protection

```
Passwords:
  ├─→ Hashed with bcrypt
  │   ├─ Salt rounds: 12
  │   └─ Stored as hash only (not reversible)
  │
  └─→ Never sent in responses

API Tokens:
  ├─→ Random generation (secrets.token_urlsafe)
  ├─→ Stored in secure database
  ├─→ Can be revoked anytime
  └─→ Optional expiration

JWT Tokens:
  ├─→ Signed with SHA-256
  ├─→ 30 minute expiration
  ├─→ Contains user_id claim
  └─→ Cannot be modified without signature

CORS:
  ├─→ Whitelist allowed origins
  ├─→ Prevent unauthorized domain access
  └─→ Credentials validated per-request

Database:
  ├─→ SQL Injection protected (ORM)
  ├─→ Parameterized queries
  └─→ Input validation
```

---

## ⚙️ Command Execution Architecture

### Command Processing Pipeline

```
WebSocket Message Received
       │
       ↓
┌──────────────────────────┐
│ Parse JSON message       │
│ Extract: command_id,     │
│          command_type,   │
│          parameters      │
└──────────────────────────┘
       │
       ↓
┌──────────────────────────┐
│ Route to handler         │
│ Based on command_type    │
└──────────────────────────┘
       │
       ↓
┌──────────────────────────┐
│ CommandExecutor dispatch │
│ Validate parameters      │
│ Check OS compatibility   │
└──────────────────────────┘
       │
       ↓
┌──────────────────────────┐
│ Execute command          │
│ • Subprocess/OS call     │
│ • Timeout protection     │
│ • Error handling         │
└──────────────────────────┘
       │
       ├─→ Success
       │       │
       │       ↓
       │   ┌──────────────────┐
       │   │ Format result    │
       │   │ capture output   │
       │   └──────────────────┘
       │       │
       │       ↓
       │   ┌──────────────────┐
       │   │ Send result      │
       │   │ via WebSocket    │
       │   │ Status: success  │
       │   └──────────────────┘
       │
       └─→ Failure
               │
               ↓
           ┌──────────────────┐
           │ Capture error    │
           │ message          │
           └──────────────────┘
               │
               ↓
           ┌──────────────────┐
           │ Send error       │
           │ via WebSocket    │
           │ Status: failed   │
           └──────────────────┘
```

### Supported Commands Registry

```python
{
    "open_chrome": {
        "handler": open_chrome,
        "parameters": ["url"],
        "timeout": 5000,
        "os": ["Windows", "Linux", "Darwin"]
    },
    "take_screenshot": {
        "handler": take_screenshot,
        "parameters": [],
        "timeout": 3000,
        "os": ["Windows", "Linux", "Darwin"]
    },
    "system_info": {
        "handler": system_info,
        "parameters": [],
        "timeout": 2000,
        "os": ["Windows", "Linux", "Darwin"]
    },
    # ... more commands
}
```

---

## 🌐 Deployment Architecture

### Development Setup

```
Developer Machine
├── Backend
│   ├── Python venv
│   ├── SQLite database
│   ├── Running on :8000
│   └── Logs: console + file
│
├── Laptop Agent
│   ├── Python venv
│   ├── Connects to localhost:8000
│   ├── Command execution
│   └── Logs: agent.log
│
└── Mobile App (Emulator/Device)
    ├── Flutter running
    ├── Connects to localhost:8000
    └── UI/UX testing
```

### Production Setup

```
Internet
    │
    ↓
┌─────────────────────────────┐
│   CDN (Optional)            │
│   • Static assets           │
│   • App distribution        │
└─────────────────────────────┘
    │
    ↓
┌─────────────────────────────┐
│   Render Platform           │
│                             │
│  ┌──────────────────────┐  │
│  │  FastAPI Backend     │  │
│  │  • 2+ dynos          │  │
│  │  • Load balanced     │  │
│  │  • Auto-scaling      │  │
│  └──────────────────────┘  │
│           │                 │
│           ↓                 │
│  ┌──────────────────────┐  │
│  │  PostgreSQL DB       │  │
│  │  • Automated backups │  │
│  │  • Replication       │  │
│  │  • SSL encrypted     │  │
│  └──────────────────────┘  │
│           │                 │
│           ├─→ Metrics       │
│           └─→ Logs          │
└─────────────────────────────┘
    │
    ↓
┌─────────────────────────────┐
│  User Laptops (Agents)      │
│  • Installed as service     │
│  • Auto-reconnect           │
│  • Command execution        │
│  • Local logging            │
└─────────────────────────────┘
    │
    ↓
┌─────────────────────────────┐
│  Mobile Users               │
│  • iOS/Android              │
│  • Downloaded from store    │
│  • Connects to backend      │
└─────────────────────────────┘
```

---

## 📈 Scalability Considerations

### Horizontal Scaling

```
Multiple Backend Servers
(Behind Load Balancer)

┌──────────────┐
│ Load Balancer│
└──────────────┘
      │
      ├→ ┌──────────────┐
      │  │ Backend 1    │
      │  │ Port: 8000   │
      │  └──────────────┘
      │
      ├→ ┌──────────────┐
      │  │ Backend 2    │
      │  │ Port: 8000   │
      │  └──────────────┘
      │
      └→ ┌──────────────┐
         │ Backend N    │
         │ Port: 8000   │
         └──────────────┘

Shared Database: PostgreSQL

Shared Cache (Optional):
  ├─→ Redis
  ├─→ Connection state
  └─→ Command queue
```

### Database Optimization

```
Indexes on:
  • users.username (unique)
  • devices.device_id (unique)
  • commands.device_id (for queries)
  • commands.status (for filtering)
  • api_tokens.token (unique)

Partitioning:
  • Commands table by created_at (monthly)
  • Archive old commands

Connection Pooling:
  • SQLAlchemy pool (default: 5)
  • Adjust based on load
```

---

## 🔍 Monitoring & Observability

### Logging Strategy

```
Backend Logs:
  • INFO: API requests, device connections
  • WARNING: Command failures, timeouts
  • ERROR: System errors, database issues
  • DEBUG: Detailed execution flow

Agent Logs:
  • INFO: WebSocket connection, command execution
  • ERROR: Connection failures, execution errors

Mobile App Logs:
  • User actions
  • API errors
  • Network issues
```

### Health Checks

```
Backend:
  GET /health
  • Database connectivity
  • WebSocket availability
  • Memory/CPU usage

Agent:
  • Periodic heartbeat to backend
  • Command execution status
  • System resource monitoring

Mobile:
  • Backend connectivity
  • Token validity
  • Device status cache
```

---

## 🚀 Performance Targets

```
Latency Targets:
  • Command send: <200ms
  • Device execution: <1s
  • Result return: <500ms
  • Total round-trip: <2s

Throughput:
  • 100+ concurrent devices
  • 1000+ commands/minute
  • 50+ simultaneous connections

Resource Usage:
  • Backend: 512MB memory, 1 CPU
  • Agent: 50MB memory, <1% CPU
  • Mobile: <100MB storage
```

---

This architecture provides:
- ✅ Scalability
- ✅ Security
- ✅ Reliability
- ✅ Performance
- ✅ Maintainability
