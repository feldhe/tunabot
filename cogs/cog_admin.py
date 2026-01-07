# cogs/cog_admin.py
import discord
from discord.ext import commands
from discord import app_commands
import os

OWNER_ID = 1207155298297577514  # Seu ID como desenvolvedor
COGS_PATH = "cogs"  # Pasta onde estão os cogs


class Admin(commands.Cog):
    """Comandos administrativos restritos ao dono do bot"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

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
                if filename.endswith(".py"):
                    try:
                        await self.bot.reload_extension(f"{COGS_PATH}.{filename[:-3]}")
                    except Exception as e:
                        failed.append(f"{filename}: {e}")
            msg = "✅ Todas as cogs recarregadas!"
            if failed:
                msg += "\n⚠️ Alguns cogs falharam:\n" + "\n".join(failed)
            await interaction.response.send_message(msg)
            return

        # Recarregar cog específico
        try:
            await self.bot.reload_extension(f"{COGS_PATH}.{cog}")
            await interaction.response.send_message(f"✅ Cog `{cog}` recarregada com sucesso!")
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Erro ao recarregar `{cog}`:\n```{e}```",
                ephemeral=True
            )


# ======================================================
# SETUP
# ======================================================
async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))
