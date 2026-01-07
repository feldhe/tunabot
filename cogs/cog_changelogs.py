import discord
from discord.ext import commands
from discord import app_commands

ROSA = 0xFFB6C1


class Changelogs(commands.Cog):
    """
    Cog responsável por mostrar as changelogs do bot
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ======================================================
    # /changelogstuna
    # ======================================================
    @app_commands.command(
        name="changelogstuna",
        description="Mostra as alterações da versão atual do Tuna Bot"
    )
    async def changelogstuna(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🌸 Tuna Bot — Atualização v1.1.0",
            description=(
                "Esta atualização trouxe grandes melhorias na "
                "estrutura, administração e estabilidade do bot.\n\n"

                "🧠 **Administração**\n"
                "• Painel administrativo interativo\n"
                "• Controle de permissões por cargo\n"
                "• Comandos restritos a administradores\n\n"

                "🧹 **Moderação**\n"
                "• Limpeza de mensagens com confirmação\n"
                "• Sistema de mute e unmute\n"
                "• Comando de kick aprimorado\n\n"

                "📜 **Sistema de Logs**\n"
                "• Logs configuráveis pelo painel\n"
                "• Escolha do canal de logs\n"
                "• Registro das ações do bot\n\n"

                "🔊 **Sistema de Voz**\n"
                "• Conexão automática em call fixa\n"
                "• Reconexão instantânea\n"
                "• Uso de IDs fixos (nome do canal pode mudar)\n\n"

                "🛠️ **Melhorias Técnicas**\n"
                "• Correções de erros críticos\n"
                "• Código reorganizado e comentado\n"
                "• Base sólida para próximas versões\n\n"

                "🚧 O bot continua em desenvolvimento contínuo 💖"
            ),
            color=ROSA
        )

        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(
            text="Tuna Bot v1.1.0 • Desenvolvido por Feldhe | CobraDevs"
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Changelogs(bot))
