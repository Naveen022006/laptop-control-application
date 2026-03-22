# Laptop Control Application (Discord Bot)

This is a Python-based Discord bot designed to execute commands on your laptop remotely via Discord.

## How to Run

1. **Open PowerShell or Command Prompt** and navigate to this directory:
   ```powershell
   cd "C:\Users\Naveen K\Desktop\admin branh of laptop\laptop-control-application"
   ```

2. **Activate the Virtual Environment**:
   ```powershell
   .\venv\Scripts\activate
   ```
   *(Note: You should see `(venv)` appear at the beginning of your command prompt)*

3. **Run the Bot**:
   ```powershell
   python bot.py
   ```

## Configuration

Make sure your Discord bot token and other credentials are properly set in the `.env` file within this directory:

```env
DISCORD_TOKEN=your_bot_token_here
AUTHORIZED_USERS=your_user_id_here
```

## Available Commands

For a complete list of all available commands, see [commands.md](commands.md).

**Quick Examples:**
- `!speak "Hello"` - Make the laptop speak
- `!screenshot` - Take a screenshot
- `!sysinfo` - Get system information
- **And 25+ more commands!**
