import discord
from discord.ext import commands
import asyncio

# Token'ın doğrudan koda yazılmış hali.
TOKEN = ""

# Intent'ler (members intent'i otomatik rol için gerekli)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} giriş yaptı ve aktif!")

async def main():
    async with bot:
        # Cog’ları yükle
        await bot.load_extension("cogs.komut")
        await bot.load_extension("cogs.oyunlar")
        await bot.load_extension("cogs.cekilis")
        await bot.load_extension("cogs.member")
        await bot.load_extension("cogs.ai")
        await bot.load_extension("cogs.dmmesega") # <-- en son satır

        await bot.start(TOKEN)

# Async bot başlat
asyncio.run(main())