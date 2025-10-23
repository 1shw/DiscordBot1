# cogs/ai.py

import discord
from discord.ext import commands
import google.generativeai as genai

# LÜTFEN DİKKAT:
# Google AI Studio'dan, YENİ BİR PROJEDE oluşturduğun API anahtarını buraya yapıştır.
GEMINI_API_KEY = "AIzaSyD9Vl0boZQCW4Ow5l5cMfxxTxupNCHy_LQ"

class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Aktif sohbet oturumlarını saklamak için bir sözlük
        self.conversations = {} 
        
        # API anahtarının girilip girilmediğini kontrol et
        if not GEMINI_API_KEY or GEMINI_API_KEY == "BURAYA_YENİ_GOOGLE_AI_API_ANAHTARINI_YAPIŞTIR":
            print("HATA: GEMINI_API_KEY girilmemiş. Lütfen cogs/ai.py dosyasını düzenleyin.")
            return
        
        # Google AI API'ını yapılandır
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Stabil çalışan 'gemini-pro' modelini seçiyoruz.
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not isinstance(message.channel, discord.DMChannel):
            return

        if message.content.startswith(await self.bot.get_prefix(message)):
            return

        if message.author.id in self.conversations:
            async with message.channel.typing():
                try:
                    chat = self.conversations[message.author.id]
                    response = await chat.send_message_async(message.content)
                    await message.channel.send(response.text)
                except Exception as e:
                    print(f"Gemini API Hatası: {e}")
                    await message.channel.send("Üzgünüm, bir hata oluştu ve isteğimi işleyemedim. Lütfen daha sonra tekrar deneyin.")
                    del self.conversations[message.author.id]

    @commands.dm_only()
    @commands.group(name="ai", invoke_without_command=True)
    async def ai_group(self, ctx):
        await ctx.send("AI modülünü başlatmak için `!ai on`, kapatmak için `!ai off` yazın.")

    @ai_group.command(name="on")
    async def ai_on(self, ctx):
        if ctx.author.id in self.conversations:
            await ctx.send("Yapay zeka zaten aktif. Konuşmaya başlayabilirsiniz.")
        else:
            chat = self.model.start_chat(history=[])
            self.conversations[ctx.author.id] = chat
            await ctx.send("🤖 **Yapay zeka modu AKTİF!**\nArtık benimle sohbet edebilirsiniz. Bitirmek için `!ai off` yazmanız yeterli.")

    @ai_group.command(name="off")
    async def ai_off(self, ctx):
        if ctx.author.id in self.conversations:
            del self.conversations[ctx.author.id]
            await ctx.send("🤖 **Yapay zeka modu KAPALI!**\nSohbet geçmişiniz temizlendi.")
        else:
            await ctx.send("Yapay zeka zaten kapalı.")

async def setup(bot):
    if not GEMINI_API_KEY or GEMINI_API_KEY == "BURAYA_YENİ_GOOGLE_AI_API_ANAHTARINI_YAPIŞTIR":
        print("AI Cog yüklenemedi: Lütfen cogs/ai.py dosyasına GEMINI_API_KEY'inizi girin.")
    else:
        await bot.add_cog(AI(bot))