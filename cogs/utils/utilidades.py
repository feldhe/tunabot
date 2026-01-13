# cogs/cog_utilidades.py
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional

ROSA = 0xFFB6C1


class Utilidades(commands.Cog):
    """
    Cog de utilidades gerais:
    - ping
    - avatar
    - invite
    - dizer (admin)
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
        user: Optional[discord.User] = None
    ):
        user = user or interaction.user
        embed = discord.Embed(
            title=f"Avatar de {user}",
            color=ROSA
        )
        embed.set_image(url=user.display_avatar.url)
        embed.set_footer(
            text=f"Solicitado por {interaction.user}",
            icon_url=interaction.user.display_avatar.url
        )

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
            "[Clique aqui para adicionar]"
            "(https://discord.com/oauth2/authorize"
            "?client_id=1450584389686788302"
            "&scope=bot%20applications.commands"
            "&permissions=8)"
        )

    # ======================================================
    # /dizer (ADMIN)
    # ======================================================
    @app_commands.command(
        name="dizer",
        description="O bot envia uma mensagem no canal atual (Administrador)"
    )
    @app_commands.describe(
        mensagem="Texto que o bot irá enviar",
        arquivo="Arquivo (imagem, PDF, etc.) para o bot enviar"
    )
    async def dizer(
        self,
        interaction: discord.Interaction,
        mensagem: Optional[str] = None,
        arquivo: Optional[discord.Attachment] = None
    ):
        # Verificação de permissão
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "⛔ Você não tem permissão para usar este comando.",
                ephemeral=True
            )
            return

        # Verificação de conteúdo
        if not mensagem and not arquivo:
            await interaction.response.send_message(
                "⚠️ Você deve informar uma mensagem ou anexar um arquivo.",
                ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        try:
            if mensagem and not arquivo:
                await interaction.channel.send(mensagem)

            elif arquivo and not mensagem:
                file = await arquivo.to_file()
                await interaction.channel.send(file=file)

            else:
                file = await arquivo.to_file()
                await interaction.channel.send(
                    content=mensagem,
                    file=file
                )

            await interaction.followup.send(
                "✅ Mensagem enviada com sucesso.",
                ephemeral=True
            )

        except Exception as e:
            await interaction.followup.send(
                f"❌ Erro ao enviar mensagem: `{e}`",
                ephemeral=True
            )


# ======================================================
# SETUP
# ======================================================
async def setup(bot: commands.Bot):
    await bot.add_cog(Utilidades(bot))
