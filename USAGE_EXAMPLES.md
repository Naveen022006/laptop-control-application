# Usage Examples & Demo Scenarios

Complete examples of how to use the Laptop Control System.

---

## 📱 Mobile App Usage

### Scenario 1: New User Registration

```
1. User launches app
   └─→ Sees Login screen

2. User taps "Don't have an account? Register"
   └─→ Registration form appears

3. User enters:
   ├─ Username: john_doe
   ├─ Email: john@example.com
   └─ Password: SecurePassword123

4. User taps "Register"
   └─→ Account created

5. User logs back in with credentials
   └─→ Taken to Dashboard (empty, no devices yet)
```

### Scenario 2: Register Device & Send Command

```
1. User (john_doe) is on Dashboard
2. User taps "+" button to add device
3. User enters device name: "My Laptop"
4. User taps "Register"
   └─→ Device registered
   └─→ device_id: 550e8400-e29b-41d4-a716-446655440002

5. Dashboard shows device with status
   ├─ Device Name: "My Laptop"
   ├─ Status: Offline (not connected yet)
   └─ Last Seen: 2024-01-15 12:30:00

6. Agent connects on laptop
   └─→ Status changes to "Online"

7. User taps on device card
   └─→ Action menu appears with:
       ├─ Open Chrome
       ├─ Open WhatsApp Web
       ├─ Take Screenshot
       ├─ System Info
       └─ Lock Screen

8. User taps "Take Screenshot"
   └─→ Command sent to backend

9. Backend forwards command via WebSocket to agent

10. Agent executes screenshot
    └─→ Captures desktop image
    └─→ Converts to base64
    └─→ Sends result back

11. Backend updates command status in database

12. Mobile app polls for result
    └─→ Screenshot appears on screen

13. User can see:
    ├─ Execution time: 245ms
    ├─ Status: Completed
    └─ Screenshot image
```

---

## 🖥️ Backend API Usage

### Example 1: Complete Workflow with cURL

```bash
# 1. Register User
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePassword123"
  }'

Response:
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john_doe",
  "email": "john@example.com",
  "is_active": true,
  "created_at": "2024-01-15T12:30:00Z"
}

# 2. Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "SecurePassword123"
  }'

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}

# 3. Create API Token (for device)
curl -X POST http://localhost:8000/auth/token/create \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "laptop-device-token",
    "expires_in_days": 90
  }'

Response:
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "name": "laptop-device-token",
  "is_active": true,
  "last_used": null,
  "created_at": "2024-01-15T12:30:00Z"
  "token": "rO1v5s3KL3pY... " # Save this!
}

# 4. Register Device
curl -X POST http://localhost:8000/devices/register \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "laptop-001",
    "name": "My Laptop",
    "device_type": "laptop",
    "os_type": "Windows"
  }'

Response:
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "device_id": "laptop-001",
  "name": "My Laptop",
  "device_type": "laptop",
  "os_type": "Windows",
  "status": "offline",
  "last_seen": "2024-01-15T12:30:00Z",
  "is_active": true,
  "created_at": "2024-01-15T12:30:00Z"
}

# 5. Get All Devices
curl -X GET http://localhost:8000/devices/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

Response:
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440002",
    "device_id": "laptop-001",
    "name": "My Laptop",
    ...
  }
]

# 6. Send Command
curl -X POST http://localhost:8000/commands/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "laptop-001",
    "command_type": "take_screenshot"
  }'

Response:
{
  "id": "550e8400-e29b-41d4-a716-446655440003",
  "device_id": "550e8400-e29b-41d4-a716-446655440002",
  "command_type": "take_screenshot",
  "status": "pending",
  "result": null,
  "error_message": null,
  "execution_time": null,
  "sent_at": "2024-01-15T12:35:00Z",
  "created_at": "2024-01-15T12:35:00Z"
}

# 7. Check Command Status (after device executes)
curl -X GET http://localhost:8000/commands/550e8400-e29b-41d4-a716-446655440003 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

Response:
{
  "id": "550e8400-e29b-41d4-a716-446655440003",
  "device_id": "550e8400-e29b-41d4-a716-446655440002",
  "command_type": "take_screenshot",
  "status": "completed",
  "result": {
    "image": "iVBORw0KGgoAAAANSUhEUgAAAAUA...",
    "format": "png",
    "size": [1920, 1080]
  },
  "error_message": null,
  "execution_time": 245,
  "sent_at": "2024-01-15T12:35:00Z",
  "created_at": "2024-01-15T12:35:00Z"
}
```

---

## 🤖 Agent Usage

### Agent Environment Setup

**File: `.env`**
```env
DEVICE_ID=laptop-001
DEVICE_NAME=My Laptop
BACKEND_URL=ws://localhost:8000
API_TOKEN=rO1v5s3KL3pY...  # From API token creation
RECONNECT_DELAY=5
MAX_RECONNECT_ATTEMPTS=10
MESSAGE_TIMEOUT=60
COMMAND_TIMEOUT=30
ENABLE_SYSTEM_COMMANDS=true
LOG_LEVEL=INFO
```

### Running the Agent

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure .env
# (copy from .env.example and update values)

# 3. Run agent
python agent.py

# Output:
# 2024-01-15 12:35:00 - __main__ - INFO - Starting Laptop Control Agent: laptop-001
# 2024-01-15 12:35:00 - __main__ - INFO - Connecting to ws://localhost:8000/ws/device/laptop-001
# 2024-01-15 12:35:01 - __main__ - INFO - Connected to backend: ws://localhost:8000/ws/device/laptop-001
# 2024-01-15 12:35:02 - __main__ - INFO - Received message type: heartbeat
```

### Agent Console Output Examples

```
# Executing command
2024-01-15 12:36:00 - __main__ - INFO - Received message type: command
2024-01-15 12:36:00 - agent - INFO - Executing command: take_screenshot (ID: 550e8400...)
2024-01-15 12:36:00 - __main__ - INFO - Command executed successfully: take_screenshot (ID: 550e8400...)

# Command with parameters
2024-01-15 12:37:00 - agent - INFO - Executing command: open_chrome (ID: 550e8401...)
2024-01-15 12:37:02 - __main__ - INFO - Command executed successfully: open_chrome

# Error handling
2024-01-15 12:38:00 - agent - ERROR - Command execution failed: shutdown - Operation not permitted
2024-01-15 12:38:00 - __main__ - ERROR - Command execution failed: shutdown (ID: 550e8402...)

# Auto-reconnection
2024-01-15 12:39:00 - __main__ - WARNING - Connection closed by server
2024-01-15 12:39:05 - __main__ - INFO - Connecting to ws://localhost:8000/ws/device/laptop-001
2024-01-15 12:39:06 - __main__ - INFO - Connected to backend
```

---

## 💾 Command Examples

### 1. Take Screenshot

**Mobile App Usage:**
1. Select device → Tap "Take Screenshot"
2. Wait for completion
3. View screenshot in app

**API Request:**
```bash
curl -X POST http://localhost:8000/commands/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "laptop-001",
    "command_type": "take_screenshot"
  }'
```

**Response:**
```json
{
  "status": "screenshot",
  "result": {
    "image": "base64_encoded_png_data...",
    "format": "png",
    "size": [1920, 1080]
  },
  "execution_time": 251
}
```

### 2. Open Chrome Browser

**Mobile App Usage:**
1. Select device → Tap "Open Chrome"
2. Chrome opens on laptop

**API Request:**
```bash
curl -X POST http://localhost:8000/commands/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "laptop-001",
    "command_type": "open_chrome",
    "parameters": {
      "url": "https://example.com"
    }
  }'
```

**Response:**
```json
{
  "status": "Chrome opened successfully"
}
```

### 3. Get System Information

**API Request:**
```bash
curl -X POST http://localhost:8000/commands/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "laptop-001",
    "command_type": "system_info"
  }'
```

**Response:**
```json
{
  "os": "Windows",
  "platform": "Windows-10-10.0.19041-SP0",
  "processor": "Intel(R) Core(TM) i7-8700K CPU @ 3.70GHz",
  "cpu_count": 12,
  "total_memory": 17179869184,
  "hostname": "LAPTOP-001",
  "python_version": "3.11.0"
}
```

### 4. Run Python Script

**API Request:**
```bash
curl -X POST http://localhost:8000/commands/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "laptop-001",
    "command_type": "run_python_script",
    "parameters": {
      "code": "import platform; print(platform.system())",
      "timeout": 10
    }
  }'
```

**Response:**
```json
{
  "return_code": 0,
  "stdout": "Windows\n",
  "stderr": ""
}
```

### 5. Lock Screen

**API Request:**
```bash
curl -X POST http://localhost:8000/commands/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "laptop-001",
    "command_type": "lock_screen"
  }'
```

---

## 🏢 Multi-Device Scenario

**Setup:**
- User has 3 devices: work_laptop, home_laptop, desktop

**Mobile Dashboard Shows:**
```
My Devices:
├── Work Laptop (Online) - Last seen: 2 min ago
├── Home Laptop (Offline) - Last seen: 1 hour ago
└── Desktop (Online) - Last seen: 1 min ago
```

**User Actions:**
```
1. Select Work Laptop
   └─→ Tap "Open Chrome" with URL
       └─→ Chrome opens on work laptop

2. Select Desktop
   └─→ Tap "Take Screenshot"
       └─→ Desktop screenshot appears

3. Try Home Laptop
   └─→ Status shows "Offline"
   └─→ "Open Chrome" button disabled
   └─→ Command queued automatically
       └─→ Will execute when device comes online

4. Home Laptop connects 30 mins later
   └─→ Backend sends queued command
   └─→ Chrome opens on home laptop
```

---

## 🔍 Real-Time Monitoring

**Agent Console Logs (Real-Time Updates):**

```
12:40:00 - Device connected
12:40:15 - Heartbeat received
12:40:30 - Heartbeat received
12:41:00 - Command received: system_info
12:41:00 - Executing: system_info
12:41:01 - Command completed: system_info (91ms)
12:41:15 - Heartbeat received
12:41:30 - Heartbeat received
12:42:00 - Heartbeat received
12:42:15 - Heartbeat received
12:42:30 - Heartbeat received
12:43:00 - Command received: take_screenshot
12:43:00 - Executing: take_screenshot
12:43:01 - Command completed: take_screenshot (251ms)
12:43:15 - Heartbeat received
```

**Mobile App Real-Time Updates:**

```
Dashboard shows:
├── Work Laptop (Online) ✓
│   Last Command: Take Screenshot - Completed (251ms)
│   Commands Sent Today: 5
│
├── Home Laptop (Offline) ✗
│   Commands Pending: 1 (queued)
│   Last Seen: 1 hour ago
│
└── Desktop (Online) ✓
    Last Command: System Info - Completed (91ms)
    Uptime: 2 days
```

---

## 🚨 Error Handling Examples

### Device Offline When Sending Command

```
User: Taps "Lock Screen" on offline device

Backend:
1. Creates command (status: PENDING)
2. Tries to send via WebSocket
3. Device not connected
4. Queues command in memory
5. Returns response to mobile

Mobile: Shows "Command queued - will execute when device comes online"

Later: Device comes Online
Backend: Sends queued command
Agent: Executes command
Mobile: Shows "Command completed"
```

### Command Execution Timeout

```
User: Sends "run_python_script" with 5s timeout
Agent: Receives command
Agent: Starts execution
20 seconds pass...
Agent: Execution timeout reached
Agent: Sends error result

Response:
{
  "status": "failed",
  "error_message": "Script execution timed out",
  "execution_time": 5000
}

Mobile: Shows "Command failed: Script execution timed out"
```

### Invalid Command

```
User: Somehow sends invalid command_type

Backend: Validation rejects it
Mobile: Shows alert "Invalid command type"

Response:
{
  "error": "Unknown command type: invalid_command"
}
```

---

## 📊 Usage Statistics

**After One Week:**

```
User Dashboard Analytics:
├── Total Devices: 3
├── Total Commands Sent: 47
│   ├─ Successful: 45 (95.7%)
│   ├─ Failed: 2 (4.3%)
│   └─ Pending: 0
├── Most Used Command: take_screenshot (18 times)
├── Average Execution Time: 340ms
├── Commands by Type:
│   ├─ take_screenshot: 18
│   ├─ open_chrome: 12
│   ├─ system_info: 10
│   ├─ lock_screen: 5
│   └─ other: 2
└── Device Status:
    ├─ Work Laptop: Online, 98.2% uptime
    ├─ Home Laptop: Online, 87.5% uptime
    └─ Desktop: Offline (offline for 2 days)
```

---

## 🎓 Training Scenario

**New Administrator Learning the System:**

```
Day 1: Setup
├── Install backend locally
├── Install agent on test laptop
└── Download mobile app

Day 2: Basic Operations
├── Register user account
├── Register device
├── Send basic command (screenshot)
└── Check command history

Day 3: Advanced Features
├── Test all command types
├── Test offline queue
├── Test reconnection
└── Check monitoring metrics

Day 4: Production Deployment
├── Deploy backend to Render
├── Configure production database
├── Install agent on production device
└── Deploy mobile app to app store

Day 5: Maintenance
├── Monitor system health
├── Review logs
├── Test backup procedures
└── Set up alerts
```

---

## 💡 Pro Tips

### Tip 1: Command History
Always check command history when debugging issues
```bash
GET /commands/device/{device_id}/history?limit=100
```

### Tip 2: Device Status
Monitor device status to ensure availability
```bash
GET /devices/{device_id}/stats
```

### Tip 3: Offline Queue
Commands are automatically queued for offline devices
No need to retry manually

### Tip 4: Heartbeat Monitoring
Agent sends heartbeat every 30s
No heartbeat for 60s = device considered offline

### Tip 5: Token Management
- Create tokens with appropriate expiration
- Revoke old tokens regularly
- Use descriptive token names

---

This comprehensive guide shows how to use every feature of the Laptop Control System!

**Start with the quick examples and progress to advanced scenarios.**
