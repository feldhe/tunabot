import discord
import datetime as dt

class EmbedSaldo(discord.Embed):
     def __init__(self, tc):

          # Dt BRT
          time_utc = dt.datetime.utcnow()
          diff = dt.timedelta(hours=3)
          time_BRT = time_utc - diff

          super().__init__(colour=discord.Colour.green(), title=f'Saldo 💵',timestamp=time_BRT, description=f'**Tc<:TunaCoin:1462165809840394421>: {tc}**')

class EmbedSaldoError(discord.Embed):
     def __init__(self, interaction: discord.Interaction, time: float):

          # Dt BRT
          time_utc = dt.datetime.utcnow()
          diff = dt.timedelta(hours=3)
          time_BRT = time_utc - diff

          super().__init__(color=discord.Colour.red(), title=f'❌ Você acabou de verificar seu `/saldo`. Aguarde ⏳ `{int(time)}s`.', timestamp=time_BRT)
          name = interaction.user.name
          avatar = interaction.user.avatar
          self.set_author(name=name, icon_url=avatar)