import discord
from discord.ext import commands

class Komut(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # !f komutu
    @commands.command()
    async def f(self, ctx, *, message: str = None):
        if not message:
            await ctx.send("❌ Lütfen bir mesaj ve kullanıcı etiketleyin. Örnek: `!f Albion Silver 1m = 9 TL @kullanıcı`")
            return
        if ctx.message.mentions:
            mentioned_user = ctx.message.mentions[0]
            content = message.replace(f"<@{mentioned_user.id}>", "").strip()
            embed = discord.Embed(
                title="💰 Fiyat / Price 💰",
                description=f"{content}\n\n👤 : {mentioned_user.mention}",
                color=0xFFD700
            )
            embed.set_author(
                name=f"{mentioned_user.display_name}",
                icon_url=mentioned_user.avatar.url if mentioned_user.avatar else None
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Lütfen bir kullanıcı etiketleyin.")
        try:
            await ctx.message.delete()
        except:
            pass

    # !k komutu (GÜNCELLENDİ)
    @commands.command()
    async def k(self, ctx):
        komutlar = """**Komut Listesi**
!poe1 - Path of Exile 1 Satışı
!poe2 - Path of Exile 2 Satışı
!alb_silver - Albion Silver Satışı
!alb_account - Albion Hesap Satışı
!alb_boost - Albion Fame Boost
!tl_lucent - Throne & Liberty Lucent Satışı
!tl_boost - Throne & Liberty Lucent Boost & Farm
!d4 - Diablo 4 Satışı
!f <mesaj> @kullanıcı - Fiyat / Price mesajı

**🎉 Çekiliş Komutları 🎉**
!cekilis <süre_dakika> <kazanan_sayısı> <ödül> - Yeni bir çekiliş başlatır.
!sonlandır <mesaj_id> - Devam eden çekilişi hemen bitirir ve kazananları çeker.
!iptal <mesaj_id> - Çekilişi siler ve sonlandırmadan iptal eder.
!t <mesaj_id> - Bitmiş bir çekilişi **tekrar çeker** (yeni kazanan belirler)."""
        await ctx.send(komutlar)
        try:
            await ctx.message.delete()
        except:
            pass

async def setup(bot):
    await bot.add_cog(Komut(bot))