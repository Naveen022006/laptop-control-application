import discord
from discord.ext import commands
import psutil
import platform
import asyncio

class SystemInfoCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="sysinfo", help="Show system information (CPU, RAM, Disk, OS).")
    async def sysinfo(self, ctx):
        """Retrieves system utilization metrics and OS details."""
        await ctx.send("📊 Gathering system information...")
        
        try:
            # Get OS info
            os_info = f"{platform.system()} {platform.release()} ({platform.version()})"
            
            # Get CPU usage
            cpu_usage = psutil.cpu_percent(interval=1)
            cpu_cores = psutil.cpu_count(logical=False)
            cpu_threads = psutil.cpu_count(logical=True)
            
            # Get RAM usage
            ram = psutil.virtual_memory()
            ram_total = round(ram.total / (1024**3), 2)
            ram_used = round(ram.used / (1024**3), 2)
            ram_percent = ram.percent
            
            # Get Disk usage (Root/C: drive)
            # Find the primary partition based on OS
            disk_path = "C:\\" if platform.system() == "Windows" else "/"
            disk = psutil.disk_usage(disk_path)
            disk_total = round(disk.total / (1024**3), 2)
            disk_used = round(disk.used / (1024**3), 2)
            disk_percent = disk.percent
            
            # Create an Embed for better formatting in Discord
            embed = discord.Embed(
                title="💻 Laptop System Information", 
                color=discord.Color.blue()
            )
            
            embed.add_field(name="Operating System", value=os_info, inline=False)
            embed.add_field(name="CPU Usage", value=f"{cpu_usage}% ({cpu_cores} Cores / {cpu_threads} Threads)", inline=False)
            embed.add_field(name="Memory (RAM)", value=f"{ram_used} GB / {ram_total} GB ({ram_percent}%)", inline=False)
            embed.add_field(name=f"Disk Usage ({disk_path})", value=f"{disk_used} GB / {disk_total} GB ({disk_percent}%)", inline=False)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Failed to gather system information: {e}")

async def setup(bot):
    await bot.add_cog(SystemInfoCommand(bot))
