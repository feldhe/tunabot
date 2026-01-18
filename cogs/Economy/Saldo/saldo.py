import discord
from database import db_instance
from discord import app_commands
from discord.ext import commands

from cogs.Economy.Saldo.Ui.embeds import EmbedSaldo, EmbedSaldoError

async def tc_coins(interaction: discord.Interaction):
     # Criar user caso não tenha
     user_id = interaction.user.id
     user_name = interaction.user.name
     guild_id = interaction.guild_id
     await db_instance.create_user(user_id=user_id, user_name=user_name, guild_id=guild_id)

     tc = await db_instance.check_coins(user_id=user_id, guild_id=guild_id)
     return tc

class Saldo(commands.Cog):
     def __init__(self, bot: commands.Bot):
          self.bot = bot
          super().__init__()

     @app_commands.checks.cooldown(rate=1, per=5, key=lambda i: i.user.id)
     @app_commands.command(name='saldo', description='Economia | Verificar seu saldo.')
     async def saldo(self, interaction: discord.Interaction):
          tc = await tc_coins(interaction=interaction)
          embed = EmbedSaldo(tc=tc)
          await interaction.response.send_message(embed=embed)

     async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
          if isinstance(error, app_commands.CommandOnCooldown):
               embed = EmbedSaldoError(interaction=interaction, time=error.retry_after)
               await interaction.response.send_message(embed=embed, ephemeral=True)
     
async def setup(bot: commands.Bot):
     await bot.add_cog(Saldo(bot=bot))