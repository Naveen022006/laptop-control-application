import os
import sys

def setup_startup():
    # Get the Windows Startup folder for the current user
    startup_folder = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
    
    # Get the directory where this script and bot.py are located
    bot_dir = os.path.abspath(os.path.dirname(__file__))
    
    # Path to the pythonw executable in the virtual environment
    # We use pythonw.exe instead of python.exe to run without a visible command prompt window
    python_exe = os.path.join(bot_dir, 'venv', 'Scripts', 'pythonw.exe')
    
    # If the venv Python doesn't exist, fallback to system Python (though venv should be there based on project structure)
    if not os.path.exists(python_exe):
        python_exe = 'pythonw.exe'
        
    bot_script = os.path.join(bot_dir, 'bot.py')
    
    # Create a VBScript file in the startup folder
    # VBScript is used here because it can reliably launch the process completely hidden
    vbs_path = os.path.join(startup_folder, 'DiscordRemoteBot.vbs')
    
    vbs_content = f"""Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "{bot_dir}"
WshShell.Run chr(34) & "{python_exe}" & chr(34) & " " & chr(34) & "{bot_script}" & chr(34), 0
Set WshShell = Nothing
"""
    
    try:
        with open(vbs_path, 'w') as f:
            f.write(vbs_content)
        print(f"✅ Startup script created successfully at:\n{vbs_path}")
        print("\nThe bot will now start automatically in the background every time you log into your laptop.")
    except Exception as e:
        print(f"❌ Failed to create startup script: {e}")

if __name__ == "__main__":
    setup_startup()
