import discord
import datetime as dt
from database import db_instance
from random import randint
from discord import app_commands
from discord.ext import commands

from cogs.Economy.Daily.Ui.embeds import EmbedDaily, EmbedDailyError

class Daily(commands.Cog):
     def __init__(self, bot: commands.Bot):
          self.bot = bot
          super().__init__()

     @app_commands.checks.cooldown(rate=1, per=5, key=lambda i: (i.guild_id, i.user.id))
     @app_commands.command(name='daily', description='Economia | Receba entre 80-120 TunaCoins diárias!')
     async def daily(self, interaction: discord.Interaction):
          
          # Add coins
          user_id = interaction.user.id
          user_name = interaction.user.name
          guild_id = interaction.guild_id
          tc = randint(80, 120)
          await db_instance.add_coins(user_id=user_id, user_name=user_name, guild_id=guild_id, tc=tc)

          embed = EmbedDaily(interaction=interaction, tc=tc)
          await interaction.response.send_message(embed=embed)
     
     async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
          if isinstance(error, app_commands.CommandOnCooldown):
               time = f'{dt.timedelta(seconds=int(error.retry_after))}'.split(':')
               embed_error = EmbedDailyError(interaction=interaction, time=time)
               await interaction.response.send_message(embed=embed_error, ephemeral=True)

async def setup(bot: commands.Bot):
     await bot.add_cog(Daily(bot=bot))