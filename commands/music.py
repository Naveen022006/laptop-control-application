import discord
from discord.ext import commands
import pyautogui
import asyncio
import time
import subprocess
import os

class MusicCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _find_and_focus_window(self, title_keyword):
        """Tries to find and focus a window matching the given title keyword using pygetwindow."""
        try:
            import pygetwindow as gw
            matches = [w for w in gw.getAllWindows() if title_keyword.lower() in w.title.lower()]
            if matches:
                win = matches[0]
                # Restore if minimized
                if win.isMinimized:
                    win.restore()
                win.activate()
                time.sleep(0.5)  # Give time for the window to come to focus
                return True
            return False
        except Exception as e:
            print(f"Window focus error: {e}")
            return False

    def _get_window_rect(self, title_keyword):
        """Gets the position and size of the target window."""
        try:
            import pygetwindow as gw
            matches = [w for w in gw.getAllWindows() if title_keyword.lower() in w.title.lower()]
            if matches:
                w = matches[0]
                return w.left, w.top, w.width, w.height
        except Exception:
            pass
        return None

    def _play_music_sync(self, song_name):
        """
        Searches for a specific song in Apple Music and plays it.
        Uses the user-provided logic:
          1. Open Apple Music directly via shell URI.
          2. Aggressively find, restore, and focus the window.
          3. Click center of window to ensure focus.
          4. Ctrl+F → type song → Enter to search.
          5. Tab 3 times to reach the Top Result, then Enter to play.
        """
        import pygetwindow as gw

        # Step 1: Open Apple Music (works even if already open - just brings it up)
        os.system("start shell:AppsFolder\\AppleInc.AppleMusicWin_nzyj5cx40ttqa!App")
        time.sleep(3)  # Wait for it to draw on screen

        # Step 2: Aggressive window focusing
        windows = gw.getWindowsWithTitle("Apple Music")
        am_window = None
        if windows:
            am_window = windows[0]
            try:
                if am_window.isMinimized:
                    am_window.restore()
                am_window.activate()
                time.sleep(1)  # Give Windows a second to switch focus
            except Exception as e:
                print(f"Warning: Could not force focus on Apple Music: {e}")

        # Step 3: Click near the top-center of the window to unambiguously give it focus
        if am_window:
            x = am_window.left + (am_window.width // 2)
            y = am_window.top + 50
            pyautogui.click(x, y)
            time.sleep(0.5)

        # Step 4: Open in-app search using Ctrl+F
        pyautogui.hotkey("ctrl", "f")
        time.sleep(1)

        # Step 5: Type the song name
        pyautogui.write(song_name, interval=0.05)
        time.sleep(1)

        # Step 6: Execute search — loads the "Top Results" grid
        pyautogui.press("enter")

        # Step 7: Wait for results to load from Apple servers
        time.sleep(3)

        # Step 8: Tab 3 times to highlight the Top Result (Song card), then Enter to open it
        pyautogui.press("tab", presses=3, interval=0.2)
        pyautogui.press("enter")

        # Step 9: Wait for the song/album page to fully load (shows the red ▶ Play button)
        time.sleep(2.5)

        # Step 10: Click the red ▶ Play button on the song page
        # Based on the Apple Music layout, the Play button is at ~39% width, ~56% height of the window
        if am_window:
            play_x = am_window.left + int(am_window.width  * 0.39)
            play_y = am_window.top  + int(am_window.height * 0.56)
            pyautogui.click(play_x, play_y)

        return True, f"Playing **{song_name}** in Apple Music! 🎵"

    @commands.command(name="play", help="Search and play a song in Apple Music. Usage: !play <song name>")
    async def play_music(self, ctx, *, song_name: str = None):
        """Remotely searches and plays a song in Apple Music using GUI automation."""
        if not song_name:
            await ctx.send("❌ Please provide a song name! Example: `!play Blinding Lights`")
            return

        await ctx.send(f"🎵 Looking for `{song_name}` in Apple Music...")

        try:
            loop = asyncio.get_running_loop()
            success, result_msg = await loop.run_in_executor(
                None, self._play_music_sync, song_name
            )

            if success:
                await ctx.send(f"▶️ {result_msg}")
            else:
                await ctx.send(f"❌ {result_msg}")

        except Exception as e:
            await ctx.send(f"⚠️ An error occurred while trying to play music: {e}")

    def _focus_apple_music(self):
        """Focuses Apple Music window and returns True if successful."""
        import pygetwindow as gw
        windows = gw.getWindowsWithTitle("Apple Music")
        if not windows:
            return False
        win = windows[0]
        if win.isMinimized:
            win.restore()
        win.activate()
        time.sleep(0.5)
        # Click title bar area to lock focus without triggering buttons
        pyautogui.click(win.left + win.width // 2, win.top + 30)
        time.sleep(0.3)
        return True

    @commands.command(name="pause_music", help="Pause or resume the current song in Apple Music.")
    async def pause_music(self, ctx):
        """Presses Space to toggle Pause/Play in Apple Music."""
        if not self._focus_apple_music():
            await ctx.send("❌ Apple Music is not open!")
            return
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, lambda: pyautogui.press('space'))
        await ctx.send("⏸️ Toggled Play/Pause in Apple Music.")

    @commands.command(name="stop_music", help="Stop the current song in Apple Music.")
    async def stop_music(self, ctx):
        """Pauses the music and seeks back to the beginning of the song."""
        if not self._focus_apple_music():
            await ctx.send("❌ Apple Music is not open!")
            return

        def _stop():
            # Pause playback
            pyautogui.press('space')
            time.sleep(0.3)
            # Jump to start of track using Ctrl+Left (rewind to beginning)
            pyautogui.hotkey('ctrl', 'left')

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, _stop)
        await ctx.send("⏹️ Stopped the music in Apple Music.")

    @commands.command(name="next_song", help="Skip to the next song in Apple Music.")
    async def next_song(self, ctx):
        """Presses Ctrl+Right to skip to the next track."""
        if not self._focus_apple_music():
            await ctx.send("❌ Apple Music is not open!")
            return
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, lambda: pyautogui.hotkey('ctrl', 'right'))
        await ctx.send("⏭️ Skipped to next track in Apple Music.")

    @commands.command(name="prev_song", help="Go back to the previous song in Apple Music.")
    async def prev_song(self, ctx):
        """Presses Ctrl+Left to go back to the previous track."""
        if not self._focus_apple_music():
            await ctx.send("❌ Apple Music is not open!")
            return
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, lambda: pyautogui.hotkey('ctrl', 'left'))
        await ctx.send("⏮️ Going back to previous track in Apple Music.")

async def setup(bot):
    await bot.add_cog(MusicCommand(bot))
