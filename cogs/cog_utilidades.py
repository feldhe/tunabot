# cogs/cog_utilidades.py
import discord
from discord.ext import commands
from discord import app_commands

ROSA = 0xFFB6C1


class Utilidades(commands.Cog):
    """
    Cog de utilidades gerais:
    - ping
    - avatar
    - invite
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ======================================================
    # /ping
    # ======================================================
    @app_commands.command(
        name="ping",
        description="Mostra a latência do bot"
    )
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"🏓 Pong! Latência: `{round(self.bot.latency * 1000)}ms`"
        )

    # ======================================================
    # /avatar
    # ======================================================
    @app_commands.command(
        name="avatar",
        description="Mostra o avatar de um usuário"
    )
    async def avatar(
        self,
        interaction: discord.Interaction,
        user: discord.User | None = None
    ):
        user = user or interaction.user
        embed = discord.Embed(
            title=f"Avatar de {user}",
            color=ROSA
        )
        embed.set_image(url=user.display_avatar.url)
        embed.set_footer(text=f"Solicitado por {interaction.user}", icon_url=interaction.user.display_avatar.url)

        await interaction.response.send_message(embed=embed)

    # ======================================================
    # /invite
    # ======================================================
    @app_commands.command(
        name="invite",
        description="Link para adicionar a Tuna Bot ao seu servidor"
    )
    async def invite(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "🌹 **Adicione a Tuna Bot ao seu servidor:**\n"
            "[Clique aqui para adicionar](https://discord.com/oauth2/authorize?client_id=1450584389686788302&scope=bot%20applications.commands&permissions=8)"
        )


# ======================================================
# SETUP
# ======================================================
async def setup(bot: commands.Bot):
    await bot.add_cog(Utilidades(bot))
