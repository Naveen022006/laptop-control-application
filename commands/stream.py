import discord
from discord.ext import commands, tasks
import pyautogui
import io
import asyncio
import time
from PIL import Image

class StreamCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stream_message = None
        self.stream_ctx = None
        # We need to tightly control how often we update Discord to avoid Rate Limits.
        # Discord allows 5 edits per 5 seconds per message, so 1 frame per second is safe.
        self.update_interval = 1.0  
        self.last_update = 0
        self.max_width = 960
        self.jpeg_quality = 45

    @commands.command(name="stream_start", help="Starts a simulated live stream (updates 1 fps).")
    async def stream_start(self, ctx):
        """Starts a live stream by rapidly editing a message with screenshots."""
        if self.stream_task.is_running():
            await ctx.send("🎥 A stream is already running! Use `!stream_stop` to stop it.")
            return

        self.stream_ctx = ctx
        await ctx.send("🎥 Simulating live stream... Please wait for the first frame.")
        
        # Take the initial screenshot to start
        img_bytes = await self._get_screenshot_bytes()
        
        # Send an initial message to hold the stream
        file = discord.File(img_bytes, filename="stream.png")
        self.stream_message = await ctx.send(content="🟢 **LIVE STREAM ACTIVE**", file=file)
        
        # Start the background loop
        self.stream_task.start()

    @commands.command(name="stream_stop", help="Stops the live stream.")
    async def stream_stop(self, ctx):
        """Stops the ongoing background screenshot loop."""
        if not self.stream_task.is_running():
            await ctx.send("❌ No stream is currently running.")
            return

        self.stream_task.cancel()
        
        if self.stream_message:
            try:
                await self.stream_message.edit(content="🔴 **STREAM ENDED**")
            except Exception:
                pass
                
        self.stream_message = None
        self.stream_ctx = None
        await ctx.send("🔴 Stream stopped successfully.")

    @tasks.loop(seconds=1.5)
    async def stream_task(self):
        """The background task that updates the message periodically."""
        if not self.stream_message:
            return

        # Ensure we don't hit Discord's hard rate limit (429 Too Many Requests)
        now = time.time()
        if now - self.last_update < self.update_interval:
            return
            
        try:
            # Capture screenshot from memory
            img_bytes = await self._get_screenshot_bytes()
            
            # Prepare new file attachment
            file = discord.File(img_bytes, filename="stream.png")
            
            # Edit the existing message with the new attachment image
            # Discord replaces old attachments with new ones automatically during edit
            await self.stream_message.edit(content="🟢 **LIVE STREAM ACTIVE**", attachments=[file])
            self.last_update = time.time()
            
        except discord.errors.RateLimited as e:
            # If hit by rate limits, back off slightly
            await asyncio.sleep(e.retry_after)
        except Exception as e:
            print(f"Stream error: {e}")
            # If the original message was deleted by a user, stop the loop
            self.stream_task.cancel()
            if self.stream_ctx:
                await self.stream_ctx.send("⚠️ Stream stopped unexpectedly (message deleted or error occurred).")

    async def _get_screenshot_bytes(self):
        """Captures a screenshot in memory to limit disk I/O."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._sync_screenshot)

    def _sync_screenshot(self):
        """Synchronous part: take screenshot, save to bytesio buffer."""
        screenshot = pyautogui.screenshot()
        screenshot = self._optimize_frame(screenshot)
        buffer = io.BytesIO()
        # Use a smaller JPEG to keep Discord uploads responsive.
        screenshot.save(buffer, format='JPEG', quality=self.jpeg_quality, optimize=True)
        buffer.seek(0)
        return buffer

    def _optimize_frame(self, screenshot):
        """Resize the screenshot to reduce upload time while keeping aspect ratio."""
        if screenshot.width <= self.max_width:
            return screenshot

        new_height = int((self.max_width / screenshot.width) * screenshot.height)
        return screenshot.resize((self.max_width, new_height), Image.Resampling.LANCZOS)

    @stream_task.before_loop
    async def before_stream_task(self):
        """Wait until the bot is ready before starting loop."""
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(StreamCommand(bot))
