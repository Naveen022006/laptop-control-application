import discord
from discord.ext import commands
import os

class FileCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Discord's strict bot upload limit is 25MB (25 * 1024 * 1024 bytes)
        self.MAX_FILE_SIZE = 25 * 1024 * 1024 

    @commands.command(name="download", help="Download a specific file from the laptop. Usage: !download <path>")
    async def download(self, ctx, *, file_path: str = None):
        """Uploads a requested local file to the Discord channel."""
        if not file_path:
            await ctx.send("❌ Please provide the file path! Example: `!download C:\\Users\\Name\\Documents\\file.txt`")
            return
            
        # Optional: remove surrounding quotes if user copy-pasted a path with spaces
        file_path = file_path.strip('"\'')
        
        await ctx.send(f"🔍 Searching for `{file_path}`...")
        
        # Check if file exists
        if not os.path.exists(file_path):
            await ctx.send(f"❌ Error: The file `{file_path}` does not exist on the laptop.")
            return
            
        # Check if it is actually a file (not a directory)
        if not os.path.isfile(file_path):
            await ctx.send(f"❌ Error: `{file_path}` is a directory/folder, not a file. I can only download individual files.")
            return
            
        # Check file size against Discord's 25MB limit
        try:
            file_size = os.path.getsize(file_path)
            
            if file_size > self.MAX_FILE_SIZE:
                size_mb = round(file_size / (1024 * 1024), 2)
                await ctx.send(f"⛔ **File Too Large!** The file is **{size_mb} MB**.\nDiscord bots can only upload files smaller than 25 MB. Please compress it or use another method.")
                return
                
            # If everything is good, send the file!
            await ctx.send("📤 Uploading file to Discord now...")
            file = discord.File(file_path)
            await ctx.send(file=file)
            
        except PermissionError:
            await ctx.send(f"🔒 **Permission Denied:** The bot does not have permission to read `{file_path}`.")
        except Exception as e:
            await ctx.send(f"⚠️ An unexpected error occurred while processing the file: {e}")

async def setup(bot):
    await bot.add_cog(FileCommand(bot))
