import discord
from discord.ext import commands
import cv2
import io
import asyncio
import os

class WebcamCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="webcam", help="Take a snapshot from the laptop's webcam.")
    async def webcam(self, ctx):
        """Captures an image using the default webcam and sends it to Discord."""
        msg = await ctx.send("📷 Accessing webcam... Please wait.")
        
        try:
            # Run webcam capture in an executor so we don't block the bot
            loop = asyncio.get_running_loop()
            img_bytes = await loop.run_in_executor(None, self._capture_webcam)
            
            if img_bytes is None:
                await msg.edit(content="❌ Failed to access the webcam. It might be in use or physically disabled.")
                return
                
            # Send file to Discord
            file = discord.File(img_bytes, filename="webcam.jpg")
            await msg.delete()
            await ctx.send(content="📸 **Webcam Capture:**", file=file)
            
        except Exception as e:
            await msg.edit(content=f"❌ An error occurred while capturing webcam: {e}")

    def _capture_webcam(self):
        """Synchronously captures a frame from the default webcam."""
        # 0 is usually the default built-in webcam
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            return None
            
        try:
            # Let the camera warm up to adjust lighting/exposure
            # Reading a few frames helps get a clear picture instead of a black/dark one
            for _ in range(5):
                cap.read()
                
            ret, frame = cap.read()
            
            if not ret:
                return None
                
            # OpenCV captures in BGR, Discord needs standard RGB/JPEG bytes
            # cv2.imencode directly encodes to a memory buffer
            success, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
            
            if not success:
                return None
                
            return io.BytesIO(buffer.tobytes())
            
        finally:
            # ALWAYS release the camera so it doesn't stay lit up or blocked
            cap.release()

async def setup(bot):
    await bot.add_cog(WebcamCommand(bot))
