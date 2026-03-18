# API Documentation

Complete API reference for the Laptop Control System.

## Base URL

```
Development:  http://localhost:8000
Production:   https://your-render-url.onrender.com
```

## Authentication

All endpoints (except `/auth/register` and `/auth/login`) require an `Authorization` header with a Bearer token:

```
Authorization: Bearer <access_token>
```

**Example:**
```bash
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." http://localhost:8000/devices/
```

---

## 🔐 Authentication Endpoints

### POST /auth/register

Register a new user account.

**Request:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePassword123"
}
```

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john_doe",
  "email": "john@example.com",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Errors:**
- `400` - User already exists or invalid input
- `422` - Validation error

---

### POST /auth/login

Authenticate user and get access token.

**Request:**
```json
{
  "username": "john_doe",
  "password": "SecurePassword123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Errors:**
- `401` - Invalid credentials

---

### POST /auth/token/create

Create an API token for device authentication.

**Request:**
```json
{
  "name": "laptop-device-token",
  "expires_in_days": 90
}
```

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "name": "laptop-device-token",
  "is_active": true,
  "last_used": null,
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Note:** Save the returned token - it won't be shown again!

---

### GET /auth/tokens

Get all API tokens for current user.

**Response (200):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "name": "laptop-device-token",
    "is_active": true,
    "last_used": "2024-01-15T12:30:00Z",
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

---

### DELETE /auth/token/{token_id}

Revoke an API token.

**Response (200):**
```json
{
  "message": "Token revoked successfully"
}
```

**Errors:**
- `404` - Token not found

---

## 📱 Device Endpoints

### POST /devices/register

Register a new device.

**Request:**
```json
{
  "device_id": "laptop-001",
  "name": "My Laptop",
  "device_type": "laptop",
  "os_type": "Windows"
}
```

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "device_id": "laptop-001",
  "name": "My Laptop",
  "device_type": "laptop",
  "os_type": "Windows",
  "status": "offline",
  "last_seen": "2024-01-15T10:30:00Z",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Parameters:**
- `device_id` - Unique device identifier
- `name` - Human-readable device name
- `device_type` - Type of device (laptop, desktop, etc.)
- `os_type` - Operating system (Windows, Linux, macOS)

---

### GET /devices/

List all devices for current user.

**Response (200):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440002",
    "device_id": "laptop-001",
    "name": "My Laptop",
    "device_type": "laptop",
    "os_type": "Windows",
    "status": "online",
    "last_seen": "2024-01-15T12:30:00Z",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

**Status Values:**
- `online` - Device connected and active
- `offline` - Device not connected
- `idle` - Device idle/waiting

---

### GET /devices/{device_id}

Get device details.

**Path Parameters:**
- `device_id` - Device ID

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "device_id": "laptop-001",
  "name": "My Laptop",
  "device_type": "laptop",
  "os_type": "Windows",
  "status": "online",
  "last_seen": "2024-01-15T12:30:00Z",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Errors:**
- `404` - Device not found
- `403` - Access denied (not your device)

---

### PATCH /devices/{device_id}/status

Update device status.

**Request:**
```json
{
  "status": "online",
  "os_type": "Windows"
}
```

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "device_id": "laptop-001",
  "name": "My Laptop",
  "device_type": "laptop",
  "os_type": "Windows",
  "status": "online",
  "last_seen": "2024-01-15T12:35:00Z",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### GET /devices/{device_id}/stats

Get device statistics.

**Response (200):**
```json
{
  "device_id": "laptop-001",
  "device_name": "My Laptop",
  "status": "online",
  "total_commands": 15,
  "completed_commands": 13,
  "failed_commands": 2,
  "last_seen": "2024-01-15T12:30:00Z",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### DELETE /devices/{device_id}

Delete a device.

**Response (200):**
```json
{
  "message": "Device deleted successfully"
}
```

**Errors:**
- `404` - Device not found
- `403` - Access denied

---

## ⚙️ Command Endpoints

### POST /commands/

Send a command to a device.

**Request:**
```json
{
  "device_id": "laptop-001",
  "command_type": "open_chrome",
  "parameters": {
    "url": "https://example.com"
  }
}
```

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440003",
  "device_id": "550e8400-e29b-41d4-a716-446655440002",
  "command_type": "open_chrome",
  "status": "pending",
  "result": null,
  "error_message": null,
  "execution_time": null,
  "sent_at": "2024-01-15T12:40:00Z",
  "created_at": "2024-01-15T12:40:00Z"
}
```

**Supported Commands:**

| Command | Parameters | Description |
|---------|-----------|-------------|
| `open_chrome` | `url` (optional) | Open Chrome browser |
| `open_whatsapp_web` | - | Open WhatsApp Web |
| `take_screenshot` | - | Capture screenshot |
| `system_info` | - | Get system information |
| `system_metrics` | - | Get CPU/Memory/Disk usage |
| `lock_screen` | - | Lock the screen |
| `shutdown` | `delay` (optional) | Shutdown device |
| `restart` | `delay` (optional) | Restart device |
| `open_file` | `path` (required) | Open file |
| `run_python_script` | `code` (required), `timeout` (optional) | Execute Python code |
| `get_processes` | - | List running processes |

**Status Values:**
- `pending` - Command created, waiting to send
- `sent` - Command sent to device
- `executing` - Device executing command
- `completed` - Command completed successfully
- `failed` - Command execution failed
- `timeout` - Command timed out

---

### GET /commands/{command_id}

Get command status.

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440003",
  "device_id": "550e8400-e29b-41d4-a716-446655440002",
  "command_type": "open_chrome",
  "status": "completed",
  "result": {
    "status": "Chrome opened successfully"
  },
  "error_message": null,
  "execution_time": 245,
  "sent_at": "2024-01-15T12:40:00Z",
  "created_at": "2024-01-15T12:40:00Z"
}
```

---

### GET /commands/device/{device_id}

Get commands for a device.

**Query Parameters:**
- `limit` - Number of commands to return (default: 50)
- `status` - Filter by status (pending, completed, failed, etc.)

**Example:**
```
GET /commands/device/laptop-001?limit=20&status=completed
```

**Response (200):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440003",
    "device_id": "550e8400-e29b-41d4-a716-446655440002",
    "command_type": "open_chrome",
    "status": "completed",
    "result": {"status": "Chrome opened successfully"},
    "error_message": null,
    "execution_time": 245,
    "sent_at": "2024-01-15T12:40:00Z",
    "created_at": "2024-01-15T12:40:00Z"
  }
]
```

---

### GET /commands/device/{device_id}/history

Get command history (full details).

**Query Parameters:**
- `limit` - Number of commands to return (default: 100)

**Response (200):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440003",
    "device_id": "550e8400-e29b-41d4-a716-446655440002",
    "command_type": "open_chrome",
    "status": "completed",
    "result": {"status": "Chrome opened successfully"},
    "error_message": null,
    "execution_time": 245,
    "sent_at": "2024-01-15T12:40:00Z",
    "created_at": "2024-01-15T12:40:00Z"
  }
]
```

---

## 🔌 WebSocket Endpoint

### WS /ws/device/{device_id}

Real-time WebSocket connection for devices.

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/device/laptop-001');

// Message format
ws.send(JSON.stringify({
  type: 'heartbeat',
  timestamp: new Date().toISOString()
}));
```

**Message Types:**

#### Command
```json
{
  "type": "command",
  "command_id": "550e8400-e29b-41d4-a716-446655440003",
  "command_type": "take_screenshot",
  "parameters": {},
  "timestamp": "2024-01-15T12:40:00Z"
}
```

#### Command Result
```json
{
  "type": "command_result",
  "command_id": "550e8400-e29b-41d4-a716-446655440003",
  "status": "success",
  "result": {"image": "base64..."},
  "error_message": null,
  "execution_time": 450,
  "timestamp": "2024-01-15T12:40:00Z"
}
```

#### Heartbeat
```json
{
  "type": "heartbeat",
  "timestamp": "2024-01-15T12:40:00Z"
}
```

#### Status Update
```json
{
  "type": "status_update",
  "device_id": "laptop-001",
  "status": "online",
  "system_info": {
    "os": "Windows",
    "cpu_usage": 25.5,
    "memory_usage": 60.2
  },
  "timestamp": "2024-01-15T12:40:00Z"
}
```

---

## 🏥 Health Check Endpoint

### GET /health

System health check.

**Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T12:40:00Z",
  "environment": "development"
}
```

---

## 🔍 Utility Endpoints

### GET /

Root endpoint - API information.

**Response (200):**
```json
{
  "message": "Laptop Control API",
  "version": "1.0.0",
  "status": "running"
}
```

---

## Error Responses

All errors follow this format:

**400 Bad Request:**
```json
{
  "detail": "Invalid input: device_id is required"
}
```

**401 Unauthorized:**
```json
{
  "detail": "Invalid credentials"
}
```

**403 Forbidden:**
```json
{
  "detail": "Access denied"
}
```

**404 Not Found:**
```json
{
  "detail": "Device not found"
}
```

**422 Validation Error:**
```json
{
  "detail": [
    {
      "loc": ["body", "username"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

Currently no rate limiting is enabled. Consider implementing for production:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/devices/", dependencies=[Depends(limiter.limit("100/minute"))])
```

---

## Examples

### Complete Workflow Example

```bash
# 1. Register user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "password": "password123"
  }'

# 2. Login
TOKEN=$(curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "password": "password123"
  }' | jq -r '.access_token')

# 3. Create API token
curl -X POST http://localhost:8000/auth/token/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "device-token"
  }'

# 4. Register device
curl -X POST http://localhost:8000/devices/register \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "laptop-001",
    "name": "My Laptop",
    "device_type": "laptop",
    "os_type": "Windows"
  }'

# 5. Send command
curl -X POST http://localhost:8000/commands/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "laptop-001",
    "command_type": "open_chrome"
  }'
```

---

## API Interactive Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

Visit these endpoints in your browser for interactive API exploration and testing.
