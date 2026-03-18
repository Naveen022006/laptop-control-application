# 🚀 RUN THE COMPLETE APPLICATION

## Prerequisites
- Python 3.8+
- Flutter SDK
- Android phone with USB debugging enabled (already connected)
- Terminal/Command Prompt

---

## 📱 CURRENT STATUS

✅ **Mobile App:** Already installed on your Samsung phone!
⏳ **Backend:** Ready to run (needs Python deps)
⏳ **Agent:** Ready to run (needs Python deps)

---

## 🚀 QUICK START (5 minutes)

### Step 1: Verify IP Address

Open Command Prompt and run:
```bash
ipconfig
```

Find your **IPv4 Address** (e.g., 192.168.1.100 or 192.168.1.2)

### Step 2: Update Mobile App Configuration

Edit: `mobile_app/lib/config/app_config.dart`

Change (line 5):
```dart
static const String apiBaseUrl = 'http://localhost:8000';
```

To (use YOUR IP):
```dart
static const String apiBaseUrl = 'http://192.168.1.2:8000';
```

### Step 3: Start Backend (Terminal 1)

```bash
cd backend
python -m pip install -r requirements.txt
python run.py
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Step 4: Start Agent (Terminal 2)

```bash
cd agent
python -m pip install -r requirements.txt
```

Create/Edit `agent/.env` file:
```env
DEVICE_ID=laptop-001
DEVICE_NAME=My Laptop
BACKEND_URL=ws://192.168.1.2:8000
API_TOKEN=demo-test-token
RECONNECT_DELAY=5
LOG_LEVEL=INFO
```

Then run:
```bash
python agent.py
```

**Expected Output:**
```
Starting Laptop Control Agent: laptop-001
Connecting to ws://192.168.1.2:8000/ws/device/laptop-001
Connected to backend
```

### Step 5: Reload Mobile App (Terminal 3)

If still in Flutter run:
```bash
cd mobile_app
flutter run -d RFCW30JNA4F
```

Or if not running:
```bash
cd mobile_app
flutter run
```

Press `r` to hot-reload the app with new IP configuration.

---

## 🎯 Test the Application

### On Your Phone:

1. **Register Account**
   - Tap "Register"
   - Username: `testuser`
   - Email: `test@example.com`
   - Password: `password123`
   - Tap "Register"

2. **Login**
   - Use same credentials
   - Tap "Login"

3. **Register Device**
   - Tap "+" button
   - Name: "My Laptop"
   - Tap "Register"

4. **See Device Status**
   - Device should show "Online" ✅

5. **Send Commands**
   ```
   Tap on device
   ↓
   Choose command:
   - Take Screenshot
   - Open Chrome
   - System Info
   - Lock Screen
   - WhatsApp Web
   ```

---

## ✅ VERIFY COMPONENTS ARE RUNNING

### Backend Health Check
```bash
curl http://localhost:8000/health
```

**Expected:** 
```json
{"status":"healthy","timestamp":"...","environment":"development"}
```

### Backend API Docs
Open browser:
```
http://localhost:8000/docs
```

You'll see interactive Swagger UI

### Agent Connection
Check Terminal 2 (Agent):
- Should show: ✅ "Connected to backend"
- Should show: 📞 "Heartbeat sent" every 30 seconds

### Mobile App
- Should show: ✅ Device online (green dot)
- Can send commands ✅
- See results ✅

---

## 🔄 TROUBLESHOOTING

### Mobile App Won't Connect
```
Problem: "Connection refused" or "Failed to connect"

Solution:
1. Check IP address is correct (ipconfig)
2. Make sure backend is running: curl http://IP:8000/health
3. Phone and computer on same WiFi ⚠️
4. Firewall may be blocking port 8000
   - Windows: Allow Python through firewall
```

### Backend Won't Start
```
Problem: "ModuleNotFoundError: No module named 'fastapi'"

Solution:
cd backend
python -m pip install -r requirements.txt
python run.py
```

### Agent Won't Connect
```
Problem: "Connection failed" or "Cannot connect to WebSocket"

Solutions:
1. Check BACKEND_URL is correct in .env
2. Make sure backend is running
3. Check API_TOKEN exists (any value works for demo)
4. Verify WebSocket path: ws://IP:8000/ws/device/device-id
```

### Can't Find IP Address
```
Windows: Run ipconfig → Look for IPv4 Address
Mac: Run ifconfig → Look for inet (not inet6)
Linux: Run hostname -I
```

### Port 8000 Already in Use
```
# Find what's using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F
```

---

## 📊 MONITORING THE APPLICATION

### Backend Logs
```
INFO: Device connected: laptop-001
INFO: Command created: take_screenshot
INFO: Command completed: take_screenshot
```

### Agent Logs  
```
Connected to backend: ws://192.168.1.2:8000
Received message type: command
Executing command: take_screenshot
Command completed: take_screenshot (245ms)
```

### Mobile App
- Tap on device → See status updates
- Command buttons enable/disable based on device status
- Bottom sheet shows command options

---

## 🎓 UNDERSTANDING THE DATA FLOW

### Command Execution Flow

```
Your Phone (Flutter Mobile App)
    ↓
    └─→ REST API: POST /commands/
        ↓
        Backend (FastAPI)
        ├─→ Create command in database
        └─→ Send via WebSocket
            ↓
            Laptop Agent (Python)
            ├─→ Receive command
            ├─→ Execute locally
            └─→ Send result back via WebSocket
                ↓
                Backend
                ├─→ Update command in database
                └─→ Ready to return to mobile
                    ↓
                    Mobile App
                    └─→ Poll for result
                    └─→ Display to user
```

---

## 📝 IMPORTANT NOTES FOR CURRENT BUILD

⚠️ **SECURITY WARNING:**
This is a development build with demo features:
- Authentication is hardcoded (currently bypassed)
- Any commands accepted without validation  
- DO NOT use in production
- See COMPREHENSIVE_CODE_ANALYSIS.md for security issues

---

## 🛑 STOP THE APPLICATION

### Cleanly Stop All Components

**Terminal 1 (Backend):**
```
Press Ctrl+C
```

**Terminal 2 (Agent):**
```
Press Ctrl+C
```

**Terminal 3 (Mobile)**:
```
Press Ctrl+C
Or
Press q (in Flutter terminal)
```

---

## 🔧 DEVELOPMENT TIPS

### Hot Reload Mobile App
- In Flutter terminal, press `r` to hot reload
- Changes to Dart code appear instantly
- Don't need to restart whole app

### View Backend Logs
- Terminal 1 shows all API requests
- Check for errors in command execution
- Shows WebSocket connection/disconnection

### View Agent Logs
- Terminal 2 shows all commands executed
- Shows connection status
- Shows any command failures

### Quick Test Commands

**Test API:**
```bash
# Get health
curl http://192.168.1.2:8000/health

# Register user
curl -X POST http://192.168.1.2:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","email":"user@test.com","password":"pass123"}'

# Login
curl -X POST http://192.168.1.2:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","password":"pass123"}'
```

---

## 📱 PHONE DISCONNECTION

If phone disconnects:
1. Reconnect phone via USB
2. Authorize USB debugging if prompted
3. In Flutter terminal: press `R` (capital R) for hot restart
4. Or: Close app and `flutter run` again

---

## 🎉 SUCCESS INDICATORS

You'll know it's working when:

✅ Backend shows: "INFO: Uvicorn running on http://0.0.0.0:8000"
✅ Agent shows: "INFO - Connected to backend"  
✅ Mobile shows: Device with "Online" status
✅ Phone can send command and see result
✅ Screenshots appear on phone instantly
✅ Chrome opens on your laptop from phone
✅ System info shown on phone

---

## 📖 NEXT STEPS

1. Explore all command types
2. Test with multiple registrations
3. Review code in `COMPREHENSIVE_CODE_ANALYSIS.md`
4. Test offline behavior (disconnect agent, send command)
5. Check logs for any errors
6. Try API directly with curl

---

**Estimated time to fully running:** 10-15 minutes
**First command execution:** 2-3 seconds end-to-end
**All features tested:** 10-15 minutes

**Enjoy your Laptop Control App! 🚀**
