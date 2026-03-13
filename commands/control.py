import discord
from discord.ext import commands
import os
import platform
import subprocess
import asyncio

class ControlCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="open_chrome", help="Open Google Chrome on the laptop.")
    async def open_chrome(self, ctx):
        """Opens Google Chrome depending on the OS."""
        await ctx.send("🌐 Opening Google Chrome...")
        
        try:
            os_name = platform.system()
            if os_name == "Windows":
                # Typical Windows Chrome path
                chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
                if os.path.exists(chrome_path):
                    subprocess.Popen([chrome_path])
                else:
                    # Try fallback path or just using 'start chrome'
                    os.system("start chrome")
            elif os_name == "Darwin": # macOS
                subprocess.Popen(["open", "-a", "Google Chrome"])
            else: # Linux
                subprocess.Popen(["google-chrome"])
                
            await ctx.send("✅ Chrome should be opening now.")
        except Exception as e:
            await ctx.send(f"❌ Failed to open Chrome: {e}")

    def _find_app_shortcut(self, app_name):
        """Searches Windows Start Menu directories for a matching .lnk shortcut."""
        app_name_lower = app_name.lower()
        
        # Define paths to search (User Start Menu, System Start Menu)
        search_paths = [
            os.path.join(os.environ.get('APPDATA', ''), r'Microsoft\Windows\Start Menu\Programs'),
            os.path.join(os.environ.get('PROGRAMDATA', ''), r'Microsoft\Windows\Start Menu\Programs')
        ]
        
        for root_path in search_paths:
            if not os.path.exists(root_path):
                continue
                
            for root, dirs, files in os.walk(root_path):
                for file in files:
                    if file.endswith('.lnk'):
                        # Check if the requested app name is part of the shortcut name
                        if app_name_lower in file.lower():
                            return os.path.join(root, file)
        
        return None

    async def _find_uwp_app(self, app_name):
        """Searches for UWP (Windows Store) apps using PowerShell and returns their AppUserModelId."""
        # This PowerShell command gets all installed app packages and filters by Name
        ps_cmd = f"Get-StartApps | Where-Object {{ $_.Name -match '{app_name}' }} | Select-Object -First 1 -ExpandProperty AppID"
        try:
            process = await asyncio.create_subprocess_shell(
                f"powershell -Command \"{ps_cmd}\"",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await process.communicate()
            app_id = stdout.decode().strip()
            return app_id if app_id else None
        except Exception:
            return None

    @commands.command(name="open", help="Open an application by name (e.g., !open notepad, !open discord).")
    async def open_app(self, ctx, *, app_name: str = None):
        """Attempts to open an application by shortcut, then UWP AppID, then generic execution."""
        if not app_name:
            await ctx.send("❌ Please provide an application name! Example: `!open discord` or `!open calc`")
            return
            
        await ctx.send(f"🔄 Attempting to open `{app_name}`...")
        
        try:
            os_name = platform.system()
            if os_name == "Windows":
                # 1. Try to find a legitimate Start Menu shortcut (.lnk)
                shortcut_path = self._find_app_shortcut(app_name)
                
                if shortcut_path:
                    os.startfile(shortcut_path)
                    await ctx.send(f"✅ Found and launched shortcut for `{app_name}`.")
                    return
                
                # 2. Try to find a UWP (Windows Store) App (e.g. Apple Music, Netflix)
                uwp_app_id = await self._find_uwp_app(app_name)
                
                if uwp_app_id:
                    # UWP apps are launched via explorer with the shell:AppsFolder URI
                    os.system(f'explorer.exe shell:appsFolder\\{uwp_app_id}')
                    await ctx.send(f"✅ Found and launched Windows App for `{app_name}`.")
                    return

                # 3. Fallback to standard command (works for native PATH tools like calc)
                os.system(f'start "" "{app_name}"')
                await ctx.send(f"✅ Executed generic command to open `{app_name}`.")
                    
            elif os_name == "Darwin": # macOS
                subprocess.Popen(["open", "-a", app_name])
                await ctx.send(f"✅ Executed command to open `{app_name}`.")
            else: # Linux
                subprocess.Popen([app_name], start_new_session=True)
                await ctx.send(f"✅ Executed command to open `{app_name}`.")
                
        except Exception as e:
            await ctx.send(f"❌ Failed to open `{app_name}`: {e}")

    @commands.command(name="lock", help="Lock the computer.")
    async def lock(self, ctx):
        """Locks the workstation."""
        await ctx.send("🔒 Locking the computer...")
        
        try:
            os_name = platform.system()
            if os_name == "Windows":
                # Uses user32.dll LockWorkStation via rundll32
                os.system("rundll32.exe user32.dll,LockWorkStation")
            elif os_name == "Darwin": # macOS
                os.system("pmset displaysleepnow")
            else: # Linux (depends on desktop environment, assuming GNOME for example)
                os.system("xdg-screensaver lock")
                
            await ctx.send("✅ Computer locked.")
        except Exception as e:
            await ctx.send(f"❌ Failed to lock computer: {e}")

    @commands.command(name="shutdown", help="Shutdown the laptop.")
    async def shutdown(self, ctx):
        """Initiates a system shutdown."""
        await ctx.send("⚠️ Shutting down the computer in 10 seconds. Use `shutdown /a` in CMD to abort on Windows.")
        
        try:
            os_name = platform.system()
            if os_name == "Windows":
                # Shutdown with 10s delay to allow sending the message
                os.system("shutdown /s /t 10")
            elif os_name == "Darwin" or os_name == "Linux":
                # Requires sudo, might not work depending on user permissions
                os.system("shutdown +1")
                
            await ctx.send("✅ Shutdown initiated.")
        except Exception as e:
            await ctx.send(f"❌ Failed to initiate shutdown: {e}")

    # ── Volume Control Commands ──────────────────────────────────────────────────

    @commands.command(name="vol_up", help="Increase system volume. Usage: !vol_up [amount 1-50, default 10]")
    async def vol_up(self, ctx, amount: int = 10):
        """Presses the Volume Up media key multiple times to raise system volume."""
        amount = max(1, min(amount, 50))  # Clamp between 1 and 50
        try:
            import pyautogui
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                None, lambda: pyautogui.press('volumeup', presses=amount, interval=0.02)
            )
            await ctx.send(f"🔊 Volume increased by {amount} steps.")
        except Exception as e:
            await ctx.send(f"❌ Failed to increase volume: {e}")

    @commands.command(name="vol_down", help="Decrease system volume. Usage: !vol_down [amount 1-50, default 10]")
    async def vol_down(self, ctx, amount: int = 10):
        """Presses the Volume Down media key multiple times to lower system volume."""
        amount = max(1, min(amount, 50))
        try:
            import pyautogui
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                None, lambda: pyautogui.press('volumedown', presses=amount, interval=0.02)
            )
            await ctx.send(f"🔉 Volume decreased by {amount} steps.")
        except Exception as e:
            await ctx.send(f"❌ Failed to decrease volume: {e}")

    @commands.command(name="mute", help="Mute or unmute the system audio.")
    async def mute(self, ctx):
        """Toggles the system mute using the Volume Mute media key."""
        try:
            import pyautogui
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, lambda: pyautogui.press('volumemute'))
            await ctx.send("🔇 Toggled system mute.")
        except Exception as e:
            await ctx.send(f"❌ Failed to toggle mute: {e}")

    @commands.command(name="vol_set", help="Set system volume to an exact level (0-100). Usage: !vol_set 50")
    async def vol_set(self, ctx, level: int = None):
        """Sets the system master volume to an exact percentage using PowerShell."""
        if level is None:
            await ctx.send("❌ Please provide a volume level (0–100). Example: `!vol_set 50`")
            return

        level = max(0, min(level, 100))  # Clamp 0–100

        try:
            # Use PowerShell to set the exact system volume via Windows Audio Component
            # $wsh.SendKeys uses the media keys a calculated number of times, but
            # PowerShell's SoundSettings API is more precise
            ps_script = (
                f"$vol = {level / 100.0}; "
                "$obj = New-Object -ComObject WScript.Shell; "
                # First mute then unmute to reset to known state, then set precisely
                "Add-Type -TypeDefinition '"
                "using System.Runtime.InteropServices; "
                "[Guid(\"5CDF2C82-841E-4546-9722-0CF74078229A\"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)] "
                "public interface IAudioEndpointVolume { int f(); int ff(); int fff(); int ffff(); int SetMasterVolumeLevelScalar(float fLevel, System.Guid pguidEventContext); }; "
                "[Guid(\"D666063F-1587-4E43-81F1-B948E807363F\"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)] "
                "public interface IMMDevice { int Activate(ref System.Guid id, int clsCtx, int activationParams, out IAudioEndpointVolume aev); }; "
                "[Guid(\"A95664D2-9614-4F35-A746-DE8DB63617E6\"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)] "
                "public interface IMMDeviceEnumerator { int f(); int GetDefaultAudioEndpoint(int dataFlow, int role, out IMMDevice endpoint); }; "
                "[ComImport, Guid(\"BCDE0395-E52F-467C-8E3D-C4579291692E\")] public class MMDeviceEnumeratorC {}; "
                "' -PassThru | Out-Null; "
                "$enumerator = [Activator]::CreateInstance([MMDeviceEnumeratorC]) -as [IMMDeviceEnumerator]; "
                "$aev = $null; $guid = [System.Guid]::Empty; $enumerator.GetDefaultAudioEndpoint(0, 1, [ref]$device) | Out-Null; "
                # simpler fallback below
                f"(New-Object -ComObject 'Shell.Application').Windows() | Out-Null; "  
            )

            # Simpler, reliable PowerShell approach using nircmd-like method via the audio API
            simple_ps = (
                f"$vol={level}; "
                "$wsh = New-Object -ComObject WScript.Shell; "
                # Reset volume to 0 first by pressing VolumeDown 50 times, then press VolumeUp $vol/2 times
                # This is approximate — use pycaw for precise if installed
                "1..50 | ForEach-Object { $wsh.SendKeys([char]174) }; "  # 174 = VolumeDown
                f"1..([Math]::Round($vol/2)) | ForEach-Object {{ $wsh.SendKeys([char]175) }}"  # 175 = VolumeUp
            )
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                None,
                lambda: subprocess.run(
                    ["powershell", "-Command", simple_ps],
                    capture_output=True
                )
            )
            await ctx.send(f"🔊 System volume set to approximately **{level}%**.")
        except Exception as e:
            await ctx.send(f"❌ Failed to set volume: {e}")

async def setup(bot):
    await bot.add_cog(ControlCommand(bot))
