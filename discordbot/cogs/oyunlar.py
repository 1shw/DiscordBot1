import discord
from discord.ext import commands

TICKET_KANAL_ID = 1421955678481813604 # Ticket kanal ID

# YARDIMCI FONKSİYON GÜNCELLENDİ
async def send_game_embed(ctx, title, desc_tr, desc_en):
    # Ticket bilgisini kanal etiketi formatında düz metin olarak oluştur
    ticket_info = f"\n\n🎫 Ticket için: <#{TICKET_KANAL_ID}>"
    
    # Türkçe açıklamaya Ticket bilgisini ekle
    full_desc_tr = desc_tr + ticket_info
    
    embed = discord.Embed(
        title=title,
        description=full_desc_tr, # Burası güncellendi (Kanal etiketi düzgün çalışacak)
        color=0xFF4500
    )
    
    embed.add_field(name="English:", value=desc_en, inline=False)
    
    # Not: Footer kaldırıldı veya boş bırakıldı. 
    # (Çünkü asıl sorun kanal etiketinin burada çalışmamasıydı.)
    # Eğer isterseniz, düz metin bir footer ekleyebilirsiniz:
    # embed.set_footer(text="GameGold UYG")
    
    await ctx.send(embed=embed)
    try:
        await ctx.message.delete()
    except:
        pass

class Oyunlar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def poe2(self, ctx):
        await send_game_embed(ctx,
            "🔥 PATH OF EXILE 2 – YENİ SEZON ORB 🔥",
            "⚔️ Yeni Sezon Orb Satışı Başladı!\n💎 Şimdi sipariş ver ve macerana başla!",
            "⚔️ New Season Orb Sale Started!\n💎 Order now and start your adventure!"
        )

    @commands.command()
    async def poe1(self, ctx):
        await send_game_embed(ctx,
            "🔥 PATH OF EXILE 1 – YENİ SEZON 🔥",
            "⚔️ POE 1 Satışı Başladı!",
            "⚔️ POE 1 Sale Started!"
        )

    @commands.command()
    async def alb_silver(self, ctx):
        await send_game_embed(ctx,
            "💰 ALBION ONLINE – SILVER SATIŞI 💰",
            "⚔️ Albion Silver Satışı Başladı!\n💎 Hemen sipariş ver, karakterini güçlendir!",
            "⚔️ Albion Silver Sale Started!\n💎 Order now and strengthen your character!"
        )

    @commands.command()
    async def alb_account(self, ctx):
        await send_game_embed(ctx,
            "🎮 ALBION ONLINE – HESAP SATIŞI 🎮",
            "⚔️ Albion Online Hesap Satışı Başladı!\n💎 Hemen sipariş ver ve güçlü bir başlangıç yap!",
            "⚔️ Albion Online Account Sale Started!\n💎 Order now and start strong!"
        )

    @commands.command()
    async def alb_boost(self, ctx):
        await send_game_embed(ctx,
            "⚡ ALBION ONLINE – FAME BOOST ⚡",
            """💪 Fame boost hizmetimizle karakterini kısa sürede güçlendir, oyunun keyfini çıkar!

✅ 8 Silah - 8 Zırh - 8 Kafalık - 8 Ayakkabı = Toplam 32 iteminizi full spec yapıyoruz
✅ Hızlı teslimat – Profesyonel kadro
✅ %100 güvenli, el ile yapılır. Bot yok, RMT yok, ban riski sıfır
📅 İstediğin zaman başlayabiliriz – Esnek saatler
🎮 Tecrübeli boost ekibi – Maksimum verim, minimum bekleme
💬 Detaylı bilgi için Ticket açabilirsiniz!""",
            """💪 Boost your character fast and enjoy the game!

✅ 8 Weapons - 8 Armor - 8 Helmets - 8 Boots = Total 32 items fully spec’d
✅ Fast delivery – Professional team
✅ 100% safe, hand-made, no bots, no RMT, zero ban risk
📅 Flexible schedule – Start anytime
🎮 Experienced boost team – Maximum efficiency, minimum wait
💬 Open a ticket for detailed info!"""
        )

    @commands.command()
    async def tl_lucent(self, ctx):
        await send_game_embed(ctx,
            "⚡ THRONE & LIBERTY LUCENT – SATIŞ ⚡",
            "✅ Lucent satışları başladı!",
            "✅ Lucent Sale Started!"
        )

    @commands.command()
    async def tl_boost(self, ctx):
        await send_game_embed(ctx,
            "⚡ THRONE & LIBERTY LUCENT – BOOST & FARM ⚡",
            """✅ 80k abyssal contract token farm
✅ 12600 dimensional contract token 2 farm
✅ 6300 dimensional contract token 1 farm
✅ Battle pass daily, weekly görevlerinin tamamı ve birçok always görev yapılacak
✅ Allied resistance forces Contract scroll 2 (24 adet yapılacak)

⭐️ HIZLI TESLİM – PROFESYONEL KADRO – MAXİMUM VERİM""",
            """✅ 80k abyssal contract token farm
✅ 12600 dimensional contract token 2 farm (Done in 3-star or 4-star dungeon)
✅ 6300 dimensional contract token 1 farm
✅ Complete all Battle Pass daily & weekly tasks and many always tasks
✅ Allied resistance forces Contract scroll 2 (24 pieces)

⭐️ FAST DELIVERY – PROFESSIONAL TEAM – MAXIMUM EFFICIENCY"""
        )

    @commands.command()
    async def d4(self, ctx):
        await send_game_embed(ctx,
            "🔥 DIABLO 4 – INFERNAL CHAOS 🔥",
            """⚔️ Infernal Chaos satışı başladı!
🎯 Hemen sipariş ver ve oyuna güçlenerek başla!""",
            """⚔️ Infernal Chaos sale started!
🎯 Order now and start the game strong!"""
        )

async def setup(bot):
    await bot.add_cog(Oyunlar(bot))