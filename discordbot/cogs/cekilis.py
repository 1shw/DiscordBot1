import discord
from discord.ext import commands, tasks
import random
import asyncio
import sqlite3
from datetime import datetime, timedelta

TICKET_KANAL_ID = 1421955678481813604 # Ticket kanal ID'niz

# Yardımcı Fonksiyon: Kalan saniyeyi okunabilir süre formatına çevirir.
def format_sure(saniye):
    if saniye <= 0:
        return "Çekiliş sona erdi!"
    
    delta = timedelta(seconds=saniye)
    gün = delta.days
    saat, kalan = divmod(delta.seconds, 3600)
    dakika, _ = divmod(kalan, 60)

    if gün > 0:
        return f"{gün} gün {saat} saat {dakika} dakika"
    elif saat > 0:
        return f"{saat} saat {dakika} dakika"
    else:
        return f"{dakika} dakika"

class Cekilis(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Veritabanı bağlantısı ve tablo oluşturma
        self.con = sqlite3.connect("cekilisler.db")
        self.cur = self.con.cursor()
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS giveaways (
                message_id INTEGER PRIMARY KEY,
                channel_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL,
                end_timestamp INTEGER NOT NULL,
                winner_count INTEGER NOT NULL,
                prize TEXT NOT NULL,
                starter_id INTEGER NOT NULL,
                is_active INTEGER DEFAULT 1
            )
        """)
        self.con.commit()
        # Aktif çekilişleri takip etmek için asyncio.Task'ları tutan bir sözlük
        self.active_tasks = {}

    # Cog yüklendiğinde veya bot hazır olduğunda çalışacak fonksiyon
    @commands.Cog.listener()
    async def on_ready(self):
        print("Çekiliş Cog'u hazır. Aktif çekilişler kontrol ediliyor...")
        await self.resume_all_giveaways()

    async def resume_all_giveaways(self):
        self.cur.execute("SELECT * FROM giveaways WHERE is_active = 1")
        active_giveaways = self.cur.fetchall()
        
        for gw in active_giveaways:
            message_id, channel_id, _, end_timestamp, _, _, _, _ = gw
            
            now = datetime.now().timestamp()
            
            # Eğer çekiliş bot kapalıyken bitmişse, hemen sonlandır
            if now >= end_timestamp:
                print(f"{message_id} ID'li çekiliş bot kapalıyken sona ermiş. Sonlandırılıyor...")
                await self.end_giveaway(message_id, was_offline=True)
            else:
                # Çekiliş hala devam ediyorsa, geri sayım görevini başlat
                print(f"{message_id} ID'li çekiliş devam ediyor. Geri sayım başlatılıyor...")
                task = self.bot.loop.create_task(self.countdown(message_id))
                self.active_tasks[message_id] = task

    async def countdown(self, message_id):
        # Veritabanından çekiliş bilgilerini al
        self.cur.execute("SELECT channel_id, end_timestamp FROM giveaways WHERE message_id = ?", (message_id,))
        result = self.cur.fetchone()
        if not result:
            return

        channel_id, end_timestamp = result
        channel = self.bot.get_channel(channel_id)
        if not channel:
            return
        
        try:
            mesaj = await channel.fetch_message(message_id)
        except discord.NotFound:
            # Mesaj silinmişse veritabanından da kaldır
            self.cur.execute("DELETE FROM giveaways WHERE message_id = ?", (message_id,))
            self.con.commit()
            return
        
        while datetime.now().timestamp() < end_timestamp:
            kalan_saniye = end_timestamp - datetime.now().timestamp()
            
            # Embed'i her 10 dakikada bir güncelle
            try:
                embed = mesaj.embeds[0]
                embed.set_footer(text=f"Kalan Süre: {format_sure(kalan_saniye)}")
                await mesaj.edit(embed=embed)
            except (discord.NotFound, IndexError):
                break # Mesaj silinmiş veya embed yok, döngüyü kır
                
            bekleme_süresi = min(600, kalan_saniye) # 10 dakika veya kalandan azı kadar bekle
            if bekleme_süresi <= 0: break
            await asyncio.sleep(bekleme_süresi)

        # Süre doldu, çekilişi sonlandır
        await self.end_giveaway(message_id)

    @commands.command()
    async def cekilis(self, ctx, süre: int, kazanan_sayısı: int, *, ödül: str):
        """!cekilis <süre_dakika> <kazanan_sayısı> <ödül>"""
        await ctx.message.delete()

        bitis_zamanı = datetime.now() + timedelta(minutes=süre)
        bitis_timestamp = int(bitis_zamanı.timestamp())

        await ctx.send("@everyone")

        kalan_süre_ilk = format_sure(süre * 60)
        
        embed = discord.Embed(
            title="🎉 ÇEKİLİŞ 🎉",
            description=f"Çekilişe katılmak için 🎟️ emojiye basın!\n**Bitiş Zamanı:** <t:{bitis_timestamp}:F>\nKazanan sayısı: {kazanan_sayısı}\n\n**ÖDÜL :** __**{ödül}**__",
            color=0x3498db
        )
        embed.set_footer(text=f"Kalan Süre: {kalan_süre_ilk}")
        if ctx.author.avatar:
            embed.set_author(name=f"Başlatan: {ctx.author.display_name}", icon_url=ctx.author.avatar.url)
        else:
            embed.set_author(name=f"Başlatan: {ctx.author.display_name}")

        mesaj = await ctx.send(embed=embed)
        await mesaj.add_reaction("🎟️")

        # Çekilişi veritabanına kaydet
        self.cur.execute("""
            INSERT INTO giveaways (message_id, channel_id, guild_id, end_timestamp, winner_count, prize, starter_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (mesaj.id, ctx.channel.id, ctx.guild.id, bitis_timestamp, kazanan_sayısı, ödül, ctx.author.id))
        self.con.commit()

        # Geri sayım görevini başlat ve sakla
        task = self.bot.loop.create_task(self.countdown(mesaj.id))
        self.active_tasks[mesaj.id] = task

    # YENİ VE GÜVENLİ HALE GETİRİLMİŞ end_giveaway FONKSİYONU
    async def end_giveaway(self, message_id, was_offline=False):
        # Görev tamamlandı, listeden kaldır
        if message_id in self.active_tasks:
            del self.active_tasks[message_id]

        # --- YARIŞ DURUMU (RACE CONDITION) İÇİN KONTROL BLOGU ---
        # 1. Önce çekilişin hala aktif olup olmadığını kontrol et
        self.cur.execute("SELECT is_active FROM giveaways WHERE message_id = ?", (message_id,))
        result = self.cur.fetchone()

        # 2. Eğer çekiliş bulunamadıysa veya zaten pasif (0) ise, işlemi hemen durdur.
        if not result or result[0] == 0:
            print(f"Çekiliş {message_id} zaten sonlandırılmış, tekrar işlem yapılması engellendi.")
            return

        # 3. YARIŞ DURUMUNU ENGELLEMEK İÇİN İLK İŞ OLARAK VERİTABANINI GÜNCELLE
        # Bu sayede bu fonksiyon aynı anda iki kez çağrılsa bile, biri diğerinden önce
        # burayı pasif hale getireceği için, diğeri üstteki if kontrolüne takılır.
        self.cur.execute("UPDATE giveaways SET is_active = 0 WHERE message_id = ?", (message_id,))
        self.con.commit()
        # --- KONTROL BLOGUNUN SONU ---

        # Veritabanından diğer bilgileri çek
        self.cur.execute("SELECT channel_id, winner_count, prize FROM giveaways WHERE message_id = ?", (message_id,))
        gw_data = self.cur.fetchone()
        if not gw_data: return

        channel_id, winner_count, prize = gw_data
        
        channel = self.bot.get_channel(channel_id)
        if not channel: return

        try:
            mesaj = await channel.fetch_message(message_id)
        except discord.NotFound:
            # Mesaj silinmişse zaten veritabanında pasif yapıldı, ek bir işlem gerekmez.
            return
        
        kullanıcılar = []
        for reaction in mesaj.reactions:
            if str(reaction.emoji) == "🎟️":
                async for user in reaction.users():
                    if not user.bot:
                        kullanıcılar.append(user)
                break # İYİLEŞTİRME: Doğru emojiyi bulunca döngüden çık, performansı artır.
        
        # İYİLEŞTİRME: Olası çift kayıtları temizlemek için listeyi set'e çevirip tekrar list yap.
        kullanıcılar = list(set(kullanıcılar))

        yeni_embed = mesaj.embeds[0]
        yeni_embed.set_footer(text="Çekiliş Sona Erdi!")
        if "**Bitiş Zamanı:**" in yeni_embed.description:
            yeni_embed.description = yeni_embed.description.replace("**Bitiş Zamanı:**", "**Sona Erdi:**")

        if len(kullanıcılar) == 0:
            await mesaj.edit(embed=yeni_embed)
            if not was_offline:
                await mesaj.channel.send("❌ Kimse çekilişe katılmadı.")
        else:
            kazananlar = random.sample(kullanıcılar, min(winner_count, len(kullanıcılar)))
            kazanan_etiket = ", ".join([k.mention for k in kazananlar])

            # İYİLEŞTİRME: Reroll gibi durumlarda eski kazananlar alanı varsa temizle.
            yeni_embed.clear_fields()
            yeni_embed.add_field(name="🏆 Kazanan(lar)", value=kazanan_etiket, inline=False)
            await mesaj.edit(embed=yeni_embed)

            if not was_offline:
                await mesaj.channel.send(
                    f"🎊 Çekiliş sona erdi! Kazananlar: {kazanan_etiket}\nÖdül: **{prize}**\n🎫 Ticket için: <#{TICKET_KANAL_ID}>"
                )
                for kazanan in kazananlar:
                    try:
                        await kazanan.send(f"🎉 Tebrikler! **{prize}** kazandınız! Ticket açarak ödülünüzü alabilirsiniz: <#{TICKET_KANAL_ID}>")
                    except discord.Forbidden:
                        pass # Kullanıcının DM'i kapalıysa hata vermeden geç

        # Not: Veritabanı güncellemesi en başta yapıldığı için burada tekrar yapmaya gerek yok.

    # !sonlandır komutu
    @commands.command()
    async def sonlandır(self, ctx, mesaj_id: int):
        await ctx.message.delete()
        if not ctx.author.guild_permissions.manage_guild:
            return await ctx.send("❌ Bu komutu kullanmak için `Sunucuyu Yönet` yetkisine sahip olmalısınız.", delete_after=5)

        self.cur.execute("SELECT is_active FROM giveaways WHERE message_id = ?", (mesaj_id,))
        result = self.cur.fetchone()

        if result and result[0] == 1:
            # Aktif görevi iptal et
            if mesaj_id in self.active_tasks:
                self.active_tasks[mesaj_id].cancel()
            # Çekilişi manuel olarak sonlandır (yeni güvenli fonksiyonu kullanacak)
            await self.end_giveaway(mesaj_id)
            await ctx.send("✅ Çekiliş başarıyla sonlandırıldı.", delete_after=5)
        else:
            await ctx.send("❌ Aktif ve bu ID'ye sahip bir çekiliş bulunamadı.", delete_after=5)
            
    # !iptal komutu
    @commands.command()
    async def iptal(self, ctx, mesaj_id: int):
        await ctx.message.delete()
        if not ctx.author.guild_permissions.manage_guild:
            return await ctx.send("❌ Bu komutu kullanmak için `Sunucuyu Yönet` yetkisine sahip olmalısınız.", delete_after=5)

        self.cur.execute("SELECT channel_id, is_active FROM giveaways WHERE message_id = ?", (mesaj_id,))
        result = self.cur.fetchone()

        if result and result[1] == 1:
            channel_id = result[0]
            # Aktif görevi iptal et
            if mesaj_id in self.active_tasks:
                self.active_tasks[mesaj_id].cancel()
                del self.active_tasks[mesaj_id]
            
            # Veritabanından sil
            self.cur.execute("DELETE FROM giveaways WHERE message_id = ?", (mesaj_id,))
            self.con.commit()

            # Mesajı sil
            try:
                channel = self.bot.get_channel(channel_id)
                mesaj = await channel.fetch_message(mesaj_id)
                await mesaj.delete()
            except discord.NotFound:
                pass # Mesaj zaten silinmiş
            
            await ctx.send("✅ Çekiliş başarıyla iptal edildi.", delete_after=5)
        else:
            await ctx.send("❌ Aktif ve bu ID'ye sahip bir çekiliş bulunamadı.", delete_after=5)
            
    # !t (reroll) komutu
    @commands.command(name="t", aliases=["tekrar", "re-roll"])
    async def tekrar_cek(self, ctx, mesaj_id: int):
        await ctx.message.delete()
        if not (ctx.author.guild_permissions.administrator or ctx.author.id == ctx.guild.owner_id):
            return await ctx.send("❌ Bu komutu kullanmaya yetkiniz yok.", delete_after=5)
        
        try:
            mesaj = await ctx.fetch_message(mesaj_id)
        except discord.NotFound:
            return await ctx.send("❌ Belirtilen ID'ye sahip mesaj bulunamadı.", delete_after=5)

        if not mesaj.embeds or "ÇEKİLİŞ" not in mesaj.embeds[0].title:
             return await ctx.send("❌ Bu bir çekiliş mesajı gibi görünmüyor.", delete_after=5)

        embed = mesaj.embeds[0]
        ödül = "Bilinmiyor"
        kazanan_sayısı = 1 
        
        # Daha güvenli veri çekme
        for line in embed.description.split('\n'):
            if "**ÖDÜL :**" in line:
                try: ödül = line.split('__**')[-1].replace('**__', '')
                except: pass
            if "Kazanan sayısı:" in line:
                 try: kazanan_sayısı = int(line.split(':')[-1].strip())
                 except: pass

        kullanıcılar = []
        for reaction in mesaj.reactions:
            if str(reaction.emoji) == "🎟️":
                async for user in reaction.users():
                    if not user.bot:
                        kullanıcılar.append(user)
                break 

        if not kullanıcılar:
            return await ctx.send("❌ Kimse çekilişe katılmamış, tekrar çekiliş yapılamaz.", delete_after=5)
        
        yeni_kazananlar = random.sample(kullanıcılar, min(kazanan_sayısı, len(kullanıcılar)))
        kazanan_etiket = ", ".join([k.mention for k in yeni_kazananlar])

        await ctx.send(
            f"🔁 **TEKRAR ÇEKİLİŞ** sonuçlandı! Yeni kazanan(lar): {kazanan_etiket}\nÖdül: **{ödül}**\n🎫 Ticket için: <#{TICKET_KANAL_ID}>"
        )
        
        for kazanan in yeni_kazananlar:
            try:
                await kazanan.send(f"🎉 **TEKRAR ÇEKİLİŞ** ile kazandınız! **{ödül}** ödülünü aldınız! Ticket açarak ödülünüzü alabilirsiniz: <#{TICKET_KANAL_ID}>")
            except discord.Forbidden:
                pass


async def setup(bot):
    await bot.add_cog(Cekilis(bot))