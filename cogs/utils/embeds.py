# cogs/cog_embeds.py
import discord
from discord.ext import commands
from discord import app_commands

ROSA = 0xFFB6C1


class Embeds(commands.Cog):
    """
    Cog responsável apenas por embeds informativos:
    - /comandos-tuna → Lista de comandos
    - /bot-info → Informações do bot
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ======================================================
    # /comandos-tuna
    # ======================================================
    @app_commands.command(
        name="comandos-tuna",
        description="Lista completa de comandos da Tuna Bot"
    )
    async def comandos_tuna(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🌸 Comandos da Tuna Bot",
            description="Use **`/`** no chat para ver os comandos disponíveis 💖",
            color=ROSA
        )

        # Administração
        embed.add_field(
            name="🛠️ Administração",
            value=(
                "`/painel_admin` → Painel administrativo\n"
                "`/limpar` → Limpar mensagens\n"
                "`/mute` → Silenciar usuário\n"
                "`/unmute` → Remover silêncio\n"
                "`/kick` → Remover membro"
            ),
            inline=False
        )

        # Utilidades
        embed.add_field(
            name="⚙️ Utilidades",
            value=(
                "`/ping` → Latência do bot\n"
                "`/avatar` → Avatar de um usuário\n"
                "`/invite` → Convite do bot"
            ),
            inline=False
        )

        # Informações
        embed.add_field(
            name="ℹ️ Informações",
            value="`/bot-info` → Informações do bot",
            inline=False
        )

        embed.set_footer(text="Tuna Bot • CobraDevs")

        # Envia o embed corretamente sem erro 40060
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ======================================================
    # /bot-info
    # ======================================================
    @app_commands.command(
        name="bot-info",
        description="Informações detalhadas sobre a Tuna Bot"
    )
    async def info_bot(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🤖 Tuna Bot — Informações",
            description=(
                "**Tuna Bot** é um bot público em desenvolvimento contínuo.\n\n"
                "🎯 Focado em:\n"
                "• Administração de servidores\n"
                "• Automação\n"
                "• Sistemas avançados de controle\n"
                "• Futuro sistema de economia\n\n"
                "Inspirado em bots como **Loritta** e **Rio Bot**."
            ),
            color=ROSA
        )

        embed.add_field(
            name="📊 Status",
            value=(
                f"🟢 Online\n"
                f"🏓 Latência: `{round(self.bot.latency * 1000)}ms`\n"
                f"🌍 Servidores: `{len(self.bot.guilds)}`\n"
                f"🧠 Cogs carregadas: `{len(self.bot.cogs)}`"
            ),
            inline=False
        )

        embed.add_field(
            name="🚧 Aviso",
            value="O bot está em constante desenvolvimento 💖",
            inline=False
        )

        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text="Tuna Bot • Desenvolvido por Feldhe | CobraDevs")

        await interaction.response.send_message(embed=embed, ephemeral=True)


# ======================================================
# SETUP
# ======================================================
async def setup(bot: commands.Bot):
    await bot.add_cog(Embeds(bot))
