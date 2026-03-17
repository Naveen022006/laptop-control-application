# Quick Start Guide - Laptop Control

Get up and running in 5 minutes!

## Step 1: Start Backend (Terminal 1)

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# or macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
python -c "from app.models.database import create_tables; create_tables()"
uvicorn app.main:app --reload
```

The backend will start at: **http://localhost:8000**

## Step 2: Register Your Laptop (Terminal 2)

```bash
# Register laptop device - copy the api_token from response
curl -X POST http://localhost:8000/devices/register \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "laptop-001",
    "device_name": "My Laptop",
    "device_type": "laptop"
  }'
```

**Expected Response:**
```json
{
  "device_id": "laptop-001",
  "device_name": "My Laptop",
  "device_type": "laptop",
  "api_token": "YOUR_TOKEN_HERE",
  "is_active": true,
  "last_online": "2024-01-15T10:00:00"
}
```

**Save the `api_token`!** You'll need it for the agent.

## Step 3: Start Laptop Agent (Terminal 3)

```bash
cd laptop_agent

# Create .env file
echo "BACKEND_URL=ws://localhost:8000" > .env
echo "API_TOKEN=YOUR_TOKEN_HERE" >> .env
echo "DEVICE_ID=laptop-001" >> .env
echo "DEVICE_NAME=My Laptop" >> .env

# Install and run
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python agent.py
```

You should see:
```
Starting Laptop Control Agent
Device ID: laptop-001
Backend URL: ws://localhost:8000
Connected to WebSocket server
```

## Step 4: Run Mobile App (Terminal 4)

```bash
cd mobile_app

# Edit lib/main.dart and change:
# baseUrl: 'http://localhost:8000'

flutter pub get
flutter run
```

## Step 5: Test Commands

### Via cURL:

```bash
# Replace {api_token} with your mobile app token
API_TOKEN="your-mobile-app-token"

# Open Chrome
curl -X POST http://localhost:8000/commands/execute/laptop-001 \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command_name": "open_chrome"}'

# Take Screenshot
curl -X POST http://localhost:8000/commands/execute/laptop-001 \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command_name": "take_screenshot"}'

# Get System Info
curl -X POST http://localhost:8000/commands/execute/laptop-001 \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command_name": "system_info"}'

# Check Command Status
curl http://localhost:8000/commands/1 \
  -H "Authorization: Bearer $API_TOKEN"
```

### Via Mobile App:

1. Launch the Flutter app
2. Enter device name (e.g., "My Phone")
3. Click "Get Started"
4. Select "laptop-001" from device dropdown
5. Click any command button (Open Chrome, etc.)
6. Watch command execute on your laptop!

## API Documentation URL

Access full interactive docs at:
```
http://localhost:8000/docs
```

## Troubleshooting

**Issue: Agent can't connect to backend**
- Check backend is running: `curl http://localhost:8000/health`
- Verify API_TOKEN is correct
- Check BACKEND_URL is correct

**Issue: Commands not executing**
- Check agent logs output
- Verify device is connected: `curl http://localhost:8000/devices/laptop-001`
- Try simple commands first (open_chrome before shutdown)

**Issue: Port 8000 already in use**
```bash
# Find what's using it
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process
kill -9 <PID>  # macOS/Linux
```

## Next Steps

1. Read [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed setup
2. Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for all endpoints
3. Deploy to production using Docker/Render
4. Configure auto-start for agent
5. Setup mobile app notifications (optional)

## Key URLs

- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **WebSocket**: ws://localhost:8000/ws/{api_token}

## Command Reference

| Command | Usage | Parameters |
|---------|-------|-----------|
| `open_chrome` | Open browser | `url` (optional) |
| `open_whatsapp` | Open WhatsApp | - |
| `take_screenshot` | Capture screen | - |
| `system_info` | System stats | - |
| `shutdown` | Power off | `delay` (optional) |
| `restart` | Reboot | `delay` (optional) |
| `run_script` | Run Python | `script_path` (required) |

## Support

- API docs: `/docs` on backend
- Logs: Check `backend/logs/` and `laptop_agent/logs/`
- Issues: Check troubleshooting above

---

**Ready to go!** 🚀
