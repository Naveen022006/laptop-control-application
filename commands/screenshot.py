import discord
from discord.ext import commands
import pyautogui
import os
import asyncio

class ScreenshotCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="screenshot", help="Take a screenshot of the laptop screen.")
    async def screenshot(self, ctx):
        """Takes a screenshot, saves it temporarily, and sends it to Discord."""
        await ctx.send("📸 Taking screenshot...")
        
        # Temporary file path
        filepath = "temp_screenshot.png"
        
        try:
            # Taking screenshot might block event loop slightly, but it's very fast
            # We run it in a thread to be safe
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self._capture_screenshot, filepath)
            
            # Send file to Discord
            file = discord.File(filepath)
            await ctx.send(file=file)
            
        except Exception as e:
            await ctx.send(f"❌ Failed to take screenshot: {e}")
            
        finally:
            # Clean up the temporary file
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except Exception as e:
                    print(f"Error deleting temporary file: {e}")

    def _capture_screenshot(self, filepath):
        """Helper method to take the screenshot synchronously using pyautogui."""
        screenshot = pyautogui.screenshot()
        screenshot.save(filepath)

async def setup(bot):
    await bot.add_cog(ScreenshotCommand(bot))
