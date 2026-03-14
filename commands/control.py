import discord
from discord.ext import commands
import os
import platform
import subprocess
import asyncio
from urllib.parse import quote_plus


class ControlCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _get_chrome_command(self, target=None):
        """Return a Chrome launch command, optionally with a URL."""
        os_name = platform.system()

        if os_name == "Windows":
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Google\Chrome\Application\chrome.exe"),
            ]
            for chrome_path in chrome_paths:
                if chrome_path and os.path.exists(chrome_path):
                    command = [chrome_path]
                    if target:
                        command.append(target)
                    return command
            return None

        if os_name == "Darwin":
            command = ["open", "-a", "Google Chrome"]
            if target:
                command.append(target)
            return command

        command = ["google-chrome"]
        if target:
            command.append(target)
        return command

    @commands.command(name="open_chrome", help="Open Google Chrome on the laptop.")
    async def open_chrome(self, ctx):
        """Opens Google Chrome depending on the OS."""
        await ctx.send("Opening Google Chrome...")

        try:
            chrome_command = self._get_chrome_command()
            if chrome_command:
                subprocess.Popen(chrome_command)
            elif platform.system() == "Windows":
                os.system("start chrome")
            else:
                raise FileNotFoundError("Google Chrome executable was not found.")

            await ctx.send("Chrome should be opening now.")
        except Exception as e:
            await ctx.send(f"Failed to open Chrome: {e}")

    @commands.command(
        name="chrome_search",
        help="Open Chrome and search Google. Usage: !chrome_search <search terms>",
    )
    async def chrome_search(self, ctx, *, query: str = None):
        """Launches Chrome directly into a Google search for the requested query."""
        if not query:
            await ctx.send("Please provide a search query! Example: `!chrome_search weather in chennai`")
            return

        search_url = f"https://www.google.com/search?q={quote_plus(query)}"
        await ctx.send(f"Searching Chrome for `{query}`...")

        try:
            chrome_command = self._get_chrome_command(search_url)
            if chrome_command:
                subprocess.Popen(chrome_command)
            elif platform.system() == "Windows":
                os.system(f'start chrome "{search_url}"')
            else:
                raise FileNotFoundError("Google Chrome executable was not found.")

            await ctx.send(f"Opened Chrome search for `{query}`.")
        except Exception as e:
            await ctx.send(f"Failed to search in Chrome: {e}")

    def _find_app_shortcut(self, app_name):
        """Search Windows Start Menu directories for a matching .lnk shortcut."""
        app_name_lower = app_name.lower()
        search_paths = [
            os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs"),
            os.path.join(os.environ.get("PROGRAMDATA", ""), r"Microsoft\Windows\Start Menu\Programs"),
        ]

        for root_path in search_paths:
            if not os.path.exists(root_path):
                continue

            for root, dirs, files in os.walk(root_path):
                for file in files:
                    if file.endswith(".lnk") and app_name_lower in file.lower():
                        return os.path.join(root, file)

        return None

    async def _find_uwp_app(self, app_name):
        """Search for UWP apps using PowerShell and return their AppUserModelId."""
        ps_cmd = f"Get-StartApps | Where-Object {{ $_.Name -match '{app_name}' }} | Select-Object -First 1 -ExpandProperty AppID"
        try:
            process = await asyncio.create_subprocess_shell(
                f'powershell -Command "{ps_cmd}"',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await process.communicate()
            app_id = stdout.decode().strip()
            return app_id if app_id else None
        except Exception:
            return None

    @commands.command(name="open", help="Open an application by name (e.g., !open notepad, !open discord).")
    async def open_app(self, ctx, *, app_name: str = None):
        """Attempt to open an application by shortcut, UWP AppID, or generic execution."""
        if not app_name:
            await ctx.send("Please provide an application name! Example: `!open discord` or `!open calc`")
            return

        await ctx.send(f"Attempting to open `{app_name}`...")

        try:
            os_name = platform.system()
            if os_name == "Windows":
                shortcut_path = self._find_app_shortcut(app_name)
                if shortcut_path:
                    os.startfile(shortcut_path)
                    await ctx.send(f"Found and launched shortcut for `{app_name}`.")
                    return

                uwp_app_id = await self._find_uwp_app(app_name)
                if uwp_app_id:
                    os.system(f"explorer.exe shell:appsFolder\\{uwp_app_id}")
                    await ctx.send(f"Found and launched Windows App for `{app_name}`.")
                    return

                os.system(f'start "" "{app_name}"')
                await ctx.send(f"Executed generic command to open `{app_name}`.")
            elif os_name == "Darwin":
                subprocess.Popen(["open", "-a", app_name])
                await ctx.send(f"Executed command to open `{app_name}`.")
            else:
                subprocess.Popen([app_name], start_new_session=True)
                await ctx.send(f"Executed command to open `{app_name}`.")
        except Exception as e:
            await ctx.send(f"Failed to open `{app_name}`: {e}")

    @commands.command(name="lock", help="Lock the computer.")
    async def lock(self, ctx):
        """Lock the workstation."""
        await ctx.send("Locking the computer...")

        try:
            os_name = platform.system()
            if os_name == "Windows":
                os.system("rundll32.exe user32.dll,LockWorkStation")
            elif os_name == "Darwin":
                os.system("pmset displaysleepnow")
            else:
                os.system("xdg-screensaver lock")

            await ctx.send("Computer locked.")
        except Exception as e:
            await ctx.send(f"Failed to lock computer: {e}")

    @commands.command(name="shutdown", help="Shutdown the laptop.")
    async def shutdown(self, ctx):
        """Initiate a system shutdown."""
        await ctx.send("Shutting down the computer in 10 seconds. Use `shutdown /a` in CMD to abort on Windows.")

        try:
            os_name = platform.system()
            if os_name == "Windows":
                os.system("shutdown /s /t 10")
            elif os_name in {"Darwin", "Linux"}:
                os.system("shutdown +1")

            await ctx.send("Shutdown initiated.")
        except Exception as e:
            await ctx.send(f"Failed to initiate shutdown: {e}")

    @commands.command(name="vol_up", help="Increase system volume. Usage: !vol_up [amount 1-50, default 10]")
    async def vol_up(self, ctx, amount: int = 10):
        """Press the Volume Up media key multiple times."""
        amount = max(1, min(amount, 50))
        try:
            import pyautogui

            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, lambda: pyautogui.press("volumeup", presses=amount, interval=0.02))
            await ctx.send(f"Volume increased by {amount} steps.")
        except Exception as e:
            await ctx.send(f"Failed to increase volume: {e}")

    @commands.command(name="vol_down", help="Decrease system volume. Usage: !vol_down [amount 1-50, default 10]")
    async def vol_down(self, ctx, amount: int = 10):
        """Press the Volume Down media key multiple times."""
        amount = max(1, min(amount, 50))
        try:
            import pyautogui

            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, lambda: pyautogui.press("volumedown", presses=amount, interval=0.02))
            await ctx.send(f"Volume decreased by {amount} steps.")
        except Exception as e:
            await ctx.send(f"Failed to decrease volume: {e}")

    @commands.command(name="mute", help="Mute or unmute the system audio.")
    async def mute(self, ctx):
        """Toggle system mute using the media key."""
        try:
            import pyautogui

            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, lambda: pyautogui.press("volumemute"))
            await ctx.send("Toggled system mute.")
        except Exception as e:
            await ctx.send(f"Failed to toggle mute: {e}")

    @commands.command(name="vol_set", help="Set system volume to an exact level (0-100). Usage: !vol_set 50")
    async def vol_set(self, ctx, level: int = None):
        """Set the system master volume to an approximate percentage using PowerShell."""
        if level is None:
            await ctx.send("Please provide a volume level (0-100). Example: `!vol_set 50`")
            return

        level = max(0, min(level, 100))

        try:
            simple_ps = (
                f"$vol={level}; "
                "$wsh = New-Object -ComObject WScript.Shell; "
                "1..50 | ForEach-Object { $wsh.SendKeys([char]174) }; "
                "1..([Math]::Round($vol/2)) | ForEach-Object { $wsh.SendKeys([char]175) }"
            )
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                None,
                lambda: subprocess.run(["powershell", "-Command", simple_ps], capture_output=True),
            )
            await ctx.send(f"System volume set to approximately **{level}%**.")
        except Exception as e:
            await ctx.send(f"Failed to set volume: {e}")


async def setup(bot):
    await bot.add_cog(ControlCommand(bot))
