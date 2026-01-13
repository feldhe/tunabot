# cogs/cog_admin.py
import discord
from discord.ext import commands
from discord import app_commands
import os
from core.database import db_instance  # Import para checar o banco

OWNER_ID = 1207155298297577514  # Seu ID como desenvolvedor
COGS_PATH = "cogs"  # Pasta onde estão os cogs

class Admin(commands.Cog):
    """Comandos administrativos restritos ao dono do bot"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ======================================================
    # COMANDO RELOAD
    # ======================================================
    @app_commands.command(
        name="reload",
        description="Recarrega uma cog específica ou todas"
    )
    async def reload(self, interaction: discord.Interaction, cog: str = None):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message(
                "❌ Apenas meu desenvolvedor pode usar isso.",
                ephemeral=True
            )
            return

        # Recarregar todas
        if cog is None or cog.lower() == "all":
            failed = []
            for filename in os.listdir(COGS_PATH):
                if filename.endswith(".py") and filename != "__init__.py":
                    try:
                        await self.bot.reload_extension(f"{COGS_PATH}.{filename[:-3]}")
                    except Exception as e:
                        failed.append(f"{filename}: {e}")
            
            msg = "✅ Todas as cogs recarregadas!"
            if failed:
                msg += "\n⚠️ Algumas falharam:\n" + "\n".join(failed)
            await interaction.response.send_message(msg)
            return

        # Recarregar específico
        try:
            await self.bot.reload_extension(f"{COGS_PATH}.{cog}")
            await interaction.response.send_message(f"✅ Cog `{cog}` recarregada com sucesso!")
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Erro ao recarregar `{cog}`:\n```{e}```",
                ephemeral=True
            )

    # ======================================================
    # COMANDO DB STATS (Para monitorar o armazenamento)
    # ======================================================
    @app_commands.command(
        name="db_stats",
        description="Verifica o uso atual do banco de dados"
    )
    async def db_stats(self, interaction: discord.Interaction):
        if interaction.user.id != OWNER_ID:
            return await interaction.response.send_message("❌ Acesso negado.", ephemeral=True)

        try:
            # Puxa estatísticas reais do MongoDB
            stats = await db_instance.db.command("dbstats")
            
            # Conversão simples de bytes para MB
            data_size_mb = stats.get('dataSize', 0) / (1024 * 1024)
            storage_size_mb = stats.get('storageSize', 0) / (1024 * 1024)
            
            embed = discord.Embed(
                title="📊 Status do Armazenamento",
                color=discord.Color.blue(),
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="Documentos", value=f"`{stats.get('objects', 0)}`", inline=True)
            embed.add_field(name="Peso dos Dados", value=f"`{data_size_mb:.2f} MB`", inline=True)
            embed.add_field(name="Espaço em Disco", value=f"`{storage_size_mb:.2f} MB`", inline=True)
            embed.set_footer(text="Limite gratuito sugerido: 512MB")

            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erro ao ler banco: {e}", ephemeral=True)

# ======================================================
# SETUP
# ======================================================
async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))