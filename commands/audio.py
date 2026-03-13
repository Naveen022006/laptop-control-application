import discord
from discord.ext import commands
import pyttsx3
import asyncio

class AudioCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Initialize the TTS engine once to save time on subsequent calls
        self.engine = pyttsx3.init()
        # Optional: You can change voice speed and volume here if desired
        # self.engine.setProperty('rate', 150)
        # self.engine.setProperty('volume', 0.9)

    @commands.command(name="speak", help='Make the laptop speak a message aloud. Usage: !speak "Hello there!"')
    async def speak(self, ctx, *, message: str = None):
        """Uses Windows native TTS to speak a message loudly from the host machine."""
        if not message:
            await ctx.send('❌ Please provide a message! Example: `!speak "Warning, host system is restarting."`')
            return
            
        # Clean up quotes if the user wrapped the text in them
        message = message.strip('"\'')
        
        status_msg = await ctx.send(f"🔊 Speaking: `{message}`...")
        
        try:
            # We must run the speech engine in a separate executor thread.
            # Otherwise, the `runAndWait()` method will completely freeze the Discord bot
            # causing it to miss other commands or disconnect entirely.
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self._speak_sync, message)
            
            await status_msg.edit(content=f"✅ Finished speaking: `{message}`")
        except Exception as e:
            await status_msg.edit(content=f"❌ Error while trying to speak: {e}")

    def _speak_sync(self, text):
        """Synchronous blocking function that handles the actual speech generation."""
        # Using a new engine instance per-thread is sometimes safer for SAPI5 stability 
        # in long-running Python processes
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        
        # Stop the engine to ensure clean up between calls
        engine.stop()

async def setup(bot):
    await bot.add_cog(AudioCommand(bot))
