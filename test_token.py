import discord
import config
import asyncio
import sys

async def test_token():
    print(f"Token length: {len(config.DISCORD_TOKEN) if config.DISCORD_TOKEN else 0}")
    if config.DISCORD_TOKEN:
        print(f"Token stars with: {config.DISCORD_TOKEN[:5]}")
        
    client = discord.Client(intents=discord.Intents.default())
    try:
        await client.login(config.DISCORD_TOKEN)
        print("✅ Token is VALID!")
        await client.close()
        sys.exit(0)
    except discord.errors.LoginFailure as e:
        print(f"❌ Token is INVALID: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"⚠️ Other Error: {e}")
        sys.exit(2)

if __name__ == "__main__":
    if not config.DISCORD_TOKEN:
        print("❌ DISCORD_TOKEN is empty!")
        sys.exit(1)
        
    asyncio.run(test_token())
