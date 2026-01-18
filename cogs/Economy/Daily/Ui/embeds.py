import discord
import datetime as dt

class EmbedDaily(discord.Embed):
     def __init__(self, interaction: discord.Interaction, tc: int):

          # Dt BRT
          time_utc = dt.datetime.utcnow()
          diff = dt.timedelta(hours=3)
          time_BRT = time_utc - diff


          self.name = interaction.user.name
          self.avatar = interaction.user.avatar
          super().__init__(color=discord.Colour.green(), title=f'🎉 Você resgatou `{tc}` <:TunaCoin:1462165809840394421> diárias', description='Use `/saldo` para verificar seu saldo.', timestamp=time_BRT)
          self.set_author(name=self.name, icon_url=self.avatar)

class EmbedDailyError(discord.Embed):
     def __init__(self, interaction: discord.Interaction, time: list):

          # Dt BRT
          time_utc = dt.datetime.utcnow()
          diff = dt.timedelta(hours=3)
          time_BRT = time_utc - diff

          self.hour = time[0]
          self.min = time[1]
          super().__init__(color=discord.Colour.red(), title=f'❌ Você só pode usar `/daily` uma vez por dia. Volte daqui a ⏳ `{self.hour}:{self.min}`', timestamp=time_BRT)
          name = interaction.user.name
          avatar = interaction.user.avatar
          self.set_author(name=name, icon_url=avatar)