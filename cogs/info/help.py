import discord
from discord.ext import commands
from discord import app_commands

ROSA = 0xFFB6C1


class Help(commands.Cog):
    """
    Cog de ajuda simples (SEM botões / SEM embed interativo)
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="help",
        description="Central de ajuda da Tuna Bot"
    )
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🌸 Central de Ajuda — Tuna",
            description=(
                "**Oi! Eu sou a Tuna 🐟💖**\n\n"
                "Use **`/`** no chat para ver todos os comandos disponíveis.\n\n"
                "📌 Principais comandos:\n"
                "• `/ping`\n"
                "• `/avatar`\n"
                "• `/invite`\n"
                "• `/painel_admin`\n"
                "• `/limpar`\n"
                "• `/mute`\n"
                "• `/unmute`\n"
                "• `/changelogstuna`\n\n"
                "🚧 O bot está em desenvolvimento contínuo."
            ),
            color=ROSA
        )

        embed.set_footer(text="Tuna Bot • Desenvolvido por Feldhe | CobraDevs")

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))
