# Laptop Control Application - Architecture & API Documentation

## System Architecture

### High-Level Architecture

```
┌─────────────────┐
│  Mobile Phone   │
│   (Flutter)     │
└────────┬────────┘
         │
    REST API HTTP
         │
    ┌────▼─────────────────────────┐
    │   FastAPI Backend Server      │
    │   ├─ Device Management        │
    │   ├─ Command Queue            │
    │   ├─ Metrics Storage          │
    │   └─ WebSocket Manager        │
    │                               │
    │   ┌─ SQLite/PostgreSQL        │
    │   └─ Logs                     │
    └────┬──────────────────────────┘
         │
   WebSocket (bidirectional)
         │
    ┌────▼──────────────────┐
    │  Laptop Agent          │
    │  ├─ Command Executor   │
    │  ├─ System Monitor     │
    │  └─ Screenshot Capture │
    │                        │
    │  Supported Commands:   │
    │  ├─ open_chrome        │
    │  ├─ open_whatsapp      │
    │  ├─ take_screenshot    │
    │  ├─ system_info        │
    │  ├─ shutdown           │
    │  ├─ restart            │
    │  └─ run_script         │
    └────────────────────────┘
```

### Data Flow

**Command Execution:**
```
Mobile App
  ↓
[POST /commands/execute]
  ↓
Backend Database (stores command as PENDING)
  ↓
[WebSocket] Sends to Agent
  ↓
Agent executes command
  ↓
[WebSocket] Sends response back
  ↓
Backend updates command status (COMPLETED/FAILED)
  ↓
Mobile App polls for status and receives result
```

**Metrics Collection:**
```
Agent (every 30 seconds)
  ↓
[Collects CPU, Memory, Disk, Battery]
  ↓
[POST /metrics/] sends to Backend
  ↓
Backend stores in database
  ↓
Mobile App can query latest or historical metrics
```

---

## Database Schema

### Devices Table
```sql
CREATE TABLE devices (
  device_id VARCHAR(255) PRIMARY KEY,
  device_name VARCHAR(255) NOT NULL,
  device_type VARCHAR(50) NOT NULL,  -- 'laptop' or 'mobile'
  api_token VARCHAR(500) UNIQUE NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  last_online DATETIME,
  created_at DATETIME DEFAULT NOW(),
  updated_at DATETIME DEFAULT NOW()
);
```

### Commands Table
```sql
CREATE TABLE commands (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  device_id VARCHAR(255) NOT NULL,
  command_name VARCHAR(100) NOT NULL,
  command_params TEXT,  -- JSON
  status ENUM('pending', 'executing', 'completed', 'failed'),
  result TEXT,  -- JSON response
  error_message TEXT,
  execution_time INTEGER,  -- milliseconds
  created_at DATETIME DEFAULT NOW(),
  executed_at DATETIME,
  updated_at DATETIME DEFAULT NOW()
);
```

### System Metrics Table
```sql
CREATE TABLE system_metrics (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  device_id VARCHAR(255) NOT NULL,
  cpu_percent INTEGER NOT NULL,
  memory_percent INTEGER NOT NULL,
  disk_percent INTEGER NOT NULL,
  temperature INTEGER,
  battery_percent INTEGER,
  is_charging BOOLEAN,
  created_at DATETIME DEFAULT NOW()
);
```

---

## API Endpoints Documentation

### Base URL: `/`

#### Health Check
```
GET /health
Response: 200 OK
{
  "status": "healthy",
  "message": "Laptop Control Backend is running"
}
```

#### Root Info
```
GET /
Response: 200 OK
{
  "name": "Laptop Control API",
  "version": "1.0.0",
  "endpoints": {
    "health": "/health",
    "docs": "/docs",
    "device_management": "/devices",
    "command_execution": "/commands",
    "system_metrics": "/metrics",
    "websocket": "/ws/{api_token}"
  }
}
```

---

### Device Management: `/devices`

#### Register Device
```
POST /devices/register
Content-Type: application/json

Request:
{
  "device_id": "laptop-001",
  "device_name": "My Laptop",
  "device_type": "laptop"
}

Response: 201 Created
{
  "device_id": "laptop-001",
  "device_name": "My Laptop",
  "device_type": "laptop",
  "api_token": "5QpR_w8x2LkN9mP0jV5tY3hU6bZ-qX1vC4dF7gI2jL",
  "is_active": true,
  "last_online": "2024-01-15T10:30:00"
}
```

#### Get Device
```
GET /devices/{device_id}

Response: 200 OK
{
  "device_id": "laptop-001",
  "device_name": "My Laptop",
  "device_type": "laptop",
  "api_token": "5QpR_w8x2LkN9mP0jV5tY3hU6bZ-qX1vC4dF7gI2jL",
  "is_active": true,
  "last_online": "2024-01-15T10:30:00"
}
```

#### Activate Device
```
PUT /devices/{device_id}/activate

Response: 200 OK
{
  "message": "Device activated",
  "device_id": "laptop-001"
}
```

#### Deactivate Device
```
PUT /devices/{device_id}/deactivate

Response: 200 OK
{
  "message": "Device deactivated",
  "device_id": "laptop-001"
}
```

#### Delete Device
```
DELETE /devices/{device_id}

Response: 204 No Content
```

---

### Command Execution: `/commands`

#### Execute Command
```
POST /commands/execute/{target_device_id}
Authorization: Bearer {api_token}
Content-Type: application/json

Request:
{
  "command_name": "open_chrome",
  "command_params": {
    "url": "https://google.com"
  }
}

Response: 200 OK
{
  "id": 1,
  "device_id": "laptop-001",
  "command_name": "open_chrome",
  "status": "pending",
  "result": null,
  "error_message": null,
  "created_at": "2024-01-15T10:35:20",
  "executed_at": null
}
```

#### Get Command History
```
GET /commands/history/{device_id}?limit=50&offset=0
Authorization: Bearer {api_token}

Response: 200 OK
[
  {
    "id": 1,
    "device_id": "laptop-001",
    "command_name": "open_chrome",
    "status": "completed",
    "result": "{\"success\": true}",
    "error_message": null,
    "created_at": "2024-01-15T10:35:20",
    "executed_at": "2024-01-15T10:35:22"
  },
  {
    "id": 2,
    "device_id": "laptop-001",
    "command_name": "shutdown",
    "status": "pending",
    "result": null,
    "error_message": null,
    "created_at": "2024-01-15T10:36:00",
    "executed_at": null
  }
]
```

#### Get Command Details
```
GET /commands/{command_id}
Authorization: Bearer {api_token}

Response: 200 OK
{
  "id": 1,
  "device_id": "laptop-001",
  "command_name": "open_chrome",
  "status": "completed",
  "result": "{\"success\": true, \"message\": \"Chrome opened with URL: https://google.com\"}",
  "error_message": null,
  "created_at": "2024-01-15T10:35:20",
  "executed_at": "2024-01-15T10:35:22"
}
```

---

### System Metrics: `/metrics`

#### Record Metrics
```
POST /metrics/
Authorization: Bearer {api_token}
X-Device-ID: {device_id}

Request:
{
  "cpu_percent": 45,
  "memory_percent": 60,
  "disk_percent": 70,
  "temperature": 65,
  "battery_percent": 85,
  "is_charging": true
}

Response: 201 Created
{
  "id": 1,
  "device_id": "laptop-001",
  "cpu_percent": 45,
  "memory_percent": 60,
  "disk_percent": 70,
  "temperature": 65,
  "battery_percent": 85,
  "is_charging": true,
  "created_at": "2024-01-15T10:40:00"
}
```

#### Get Latest Metrics
```
GET /metrics/{device_id}/latest
Authorization: Bearer {api_token}

Response: 200 OK
{
  "id": 100,
  "device_id": "laptop-001",
  "cpu_percent": 42,
  "memory_percent": 58,
  "disk_percent": 70,
  "temperature": 64,
  "battery_percent": 82,
  "is_charging": true,
  "created_at": "2024-01-15T10:50:00"
}
```

#### Get Metrics History
```
GET /metrics/{device_id}/history?limit=100
Authorization: Bearer {api_token}

Response: 200 OK
[
  {
    "id": 100,
    "device_id": "laptop-001",
    "cpu_percent": 42,
    "memory_percent": 58,
    "disk_percent": 70,
    "temperature": 64,
    "battery_percent": 82,
    "is_charging": true,
    "created_at": "2024-01-15T10:50:00"
  },
  {
    "id": 99,
    "device_id": "laptop-001",
    "cpu_percent": 45,
    "memory_percent": 60,
    "disk_percent": 70,
    "temperature": 65,
    "battery_percent": 85,
    "is_charging": true,
    "created_at": "2024-01-15T10:40:00"
  }
]
```

---

### WebSocket: `/ws/{api_token}`

#### Connection
```
WebSocket wss://backend.example.com/ws/{api_token}

Laptop Agent connects and maintains persistent connection
```

#### Message Types

**Ping (keep-alive)**
```json
{
  "type": "ping"
}
```

**Pong (keep-alive response)**
```json
{
  "type": "pong",
  "timestamp": "2024-01-15T10:50:00"
}
```

**Command (from Server to Agent)**
```json
{
  "type": "command",
  "id": 1,
  "command_name": "open_chrome",
  "command_params": {
    "url": "https://google.com"
  }
}
```

**Command Response (from Agent to Server)**
```json
{
  "type": "command_response",
  "command_id": 1,
  "status": "completed",
  "result": {
    "success": true,
    "message": "Chrome opened with URL: https://google.com"
  },
  "error": null,
  "timestamp": "2024-01-15T10:35:22"
}
```

**System Metrics (from Agent to Server)**
```json
{
  "type": "system_metrics",
  "metrics": {
    "cpu_percent": 45,
    "memory_percent": 60,
    "disk_percent": 70,
    "battery": {
      "percent": 85,
      "is_charging": true,
      "time_left_sec": 7200
    },
    "process_count": 150
  },
  "timestamp": "2024-01-15T10:40:00"
}
```

---

## Authentication

### Token-Based Authorization

All endpoints except registration use token-based authorization.

```
Authorization: Bearer {api_token}
```

Where `api_token` is returned during device registration.

### CORS Headers

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
```

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error description",
  "error_code": "ERROR_CODE" // Optional
}
```

### Common Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 201 | Created - Resource created |
| 204 | No Content - Resource deleted |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Invalid/missing token |
| 403 | Forbidden - Permission denied |
| 404 | Not Found - Resource doesn't exist |
| 409 | Conflict - Resource already exists |
| 500 | Server Error - Internal error |

---

## Rate Limiting

Rate limits are applied per IP:
- **100 requests per minute** for general endpoints
- **10 requests per minute** for command execution

When limit exceeded:
```
429 Too Many Requests
Retry-After: 60
```

---

## WebSocket Connection Management

### Connection Lifecycle

1. **Connect**: Agent connects with API token
2. **Authenticate**: Server validates token and device
3. **Online**: Agent is marked as online, can receive commands
4. **Heartbeat**: Server sends ping every 30 seconds
5. **Disconnect**: Connection closes gracefully

### Reconnection Strategy

- **Initial Delay**: 5 seconds
- **Max Delay**: 30 seconds
- **Backoff**: Exponential (double each attempt)
- **Retry**: Indefinite until successful

---

## Performance Metrics

- **Command Execution**: 2-5 seconds
- **Screenshot Capture**: 1-3 seconds
- **Metrics Collection**: <100ms
- **API Response**: <200ms
- **WebSocket Latency**: <50ms (LAN), <500ms (Internet)

---

## Security Considerations

1. **HTTPS Only**: All production connections use HTTPS
2. **Token Security**: Tokens are 32+ character random strings
3. **Input Validation**: All inputs validated server-side
4. **SQL Injection**: Protected via SQLAlchemy ORM
5. **XSS Protection**: No user input rendered in templates
6. **CORS Security**: Configurable origins in production
7. **Command Validation**: Only whitelisted commands allowed
8. **Execution Timeout**: Commands timeout after 5 minutes
9. **Logging**: All actions logged for audit trail
10. **Encryption**: Optional TLS encryption for WebSocket

---

## Deployment Checklist

- [ ] Update `SECRET_KEY` to strong random value
- [ ] Set `ENVIRONMENT=production`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Configure CORS origins
- [ ] Set up HTTPS/SSL certificates
- [ ] Configure firewalls and security groups
- [ ] Enable logging and monitoring
- [ ] Set up backups for database
- [ ] Test all endpoints with curl/Postman
- [ ] Load test with expected traffic
- [ ] Setup alerting for errors and downtime
- [ ] Configure rate limiting
- [ ] Document API keys and tokens securely
- [ ] Setup database replication
- [ ] Configure log aggregation

---

## Code Examples

### Python - Execute Command
```python
import requests

api_token = "your-token"
headers = {"Authorization": f"Bearer {api_token}"}

response = requests.post(
    "http://localhost:8000/commands/execute/laptop-001",
    json={
        "command_name": "open_chrome",
        "command_params": {"url": "https://google.com"}
    },
    headers=headers
)
command = response.json()
print(f"Command ID: {command['id']}, Status: {command['status']}")
```

### JavaScript - Get Metrics
```javascript
const apiToken = "your-token";
const deviceId = "laptop-001";

fetch(`http://localhost:8000/metrics/${deviceId}/latest`, {
    headers: {
        "Authorization": `Bearer ${apiToken}`
    }
})
.then(r => r.json())
.then(metrics => {
    console.log(`CPU: ${metrics.cpu_percent}%`);
    console.log(`Memory: ${metrics.memory_percent}%`);
});
```

### cURL - Register Device
```bash
curl -X POST http://localhost:8000/devices/register \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "laptop-001",
    "device_name": "My Laptop",
    "device_type": "laptop"
  }'
```

---

**Last Updated**: January 2024
**Version**: 1.0.0
