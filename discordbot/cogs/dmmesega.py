# hosgeldin_cog.py

import discord
from discord.ext import commands

class HosGeldin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Sunucuya yeni bir üye katıldığında bu fonksiyon otomatik olarak tetiklenir."""
        
        # Sunucuya yeni katılan üyeye özel bir mesaj hazırlıyoruz.
        # member.name, kullanıcının adını alır.
        # member.guild.name, katıldığı sunucunun adını alır.
        mesaj = (
            f"Merhaba {member.name}! **{member.guild.name}** sunucumuza hoş geldin! 🎉\n\n"
            "Burada keyifli alışverişler ve harika zaman geçirmeni dileriz. "
            "Herhangi bir sorun veya sorun olursa yöneticilere yazmaktan çekinme!"
        )
        
        try:
            # Hazırladığımız mesajı direkt olarak yeni üyeye (member) gönderiyoruz.
            await member.send(mesaj)
            print(f"BİLGİ: {member.name} sunucuya katıldı ve kendisine DM gönderildi.")
        
        except discord.Forbidden:
            # Eğer kullanıcının direkt mesajları kapalıysa, bot hata alır.
            # Bu hatayı yakalayıp botun çökmesini engelliyoruz ve konsola bilgi veriyoruz.
            print(f"UYARI: {member.name} kullanıcısının direkt mesajları kapalı. DM gönderilemedi.")
            
        except Exception as e:
            # Beklenmedik başka bir hata olursa diye genel bir kontrol sağlıyoruz.
            print(f"HATA: {member.name} kullanıcısına DM gönderilirken bir hata oluştu: {e}")

# Bu özel fonksiyon, bu cog'un bot.py tarafından yüklenebilmesini sağlar.
async def setup(bot):
    await bot.add_cog(HosGeldin(bot))