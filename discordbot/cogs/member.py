import discord
from discord.ext import commands

# Otomatik olarak verilecek rolün ID'sini buraya yazın.
# Nasıl alacağınızı aşağıda anlattım.
OTO_ROL_ID = 1380358937416700024 # <-- BURAYA KENDİ ROL ID'NİZİ YAZIN

class Member(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Sunucuya yeni bir üye katıldığında tetiklenir."""
        
        if member.bot:
            return

        print(f'{member.name} sunucuya katıldı. Rol verilecek...')

        # Sunucudaki rolü ID'sine göre bul
        guild = member.guild
        rol = guild.get_role(OTO_ROL_ID)

        if rol is None:
            # Eğer belirtilen ID'de bir rol sunucuda yoksa, konsola hata yazdır.
            print(f'HATA: ID\'si "{OTO_ROL_ID}" olan bir rol sunucuda bulunamadı!')
            print("Lütfen rol ID'sini kodda doğru yazdığınızdan emin olun.")
            return

        try:
            # Rolü üyeye ekle
            await member.add_roles(rol)
            print(f'BAŞARILI: {member.name} kullanıcısına "{rol.name}" rolü verildi.')
        except discord.Forbidden:
            # Botun yetkisi yoksa konsola hata yazdır.
            print(f'HATA: Botun yetkileri yetersiz! "{rol.name}" rolünü vermek için "Rolleri Yönet" izni gerekiyor.')
            print(f"Lütfen botun rolünü kontrol edin ve rol hiyerarşisinde '{rol.name}' rolünün üzerinde olduğundan emin olun.")
        except Exception as e:
            # Beklenmedik başka bir hata olursa konsola yazdır.
            print(f"Bir hata oluştu: {e}")


async def setup(bot):
    """Cog'u bota yüklemek için gerekli fonksiyon."""
    await bot.add_cog(Member(bot))