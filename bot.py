import discord
from discord.ext import commands
import config
import os

# Define bot intents (required for reading messages)
intents = discord.Intents.default()
intents.message_content = True

# Initialize bot with the prefix '!'
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')
    print('Bot is ready to receive commands.')

@bot.event
async def on_command_error(ctx, error):
    """Global error handler."""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command not found.")
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("⛔ You are not authorized to use this command.")
    else:
        print(f"Error: {error}")
        await ctx.send(f"⚠️ An error occurred: {error}")

def check_authorized(ctx):
    """A check to make sure the user is authorized."""
    return config.is_authorized(ctx.author.id)

# Apply global check to all commands
bot.add_check(check_authorized)

async def load_extensions():
    """Load all cogs from the commands directory."""
    for filename in os.listdir('./commands'):
        if filename.endswith('.py') and filename != '__init__.py':
            extension = f'commands.{filename[:-3]}'
            try:
                await bot.load_extension(extension)
                print(f"Loaded extension {extension}")
            except Exception as e:
                print(f"Failed to load extension {extension}: {e}")

async def main():
    if not config.DISCORD_TOKEN:
        print("Error: DISCORD_TOKEN is not set in the .env file.")
        return
        
    async with bot:
        await load_extensions()
        await bot.start(config.DISCORD_TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
