import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View
import asyncio

ROSA = 0xFFB6C1

# ======================================================
# CONFIGURAÇÃO DO SERVIDOR (em memória)
# ======================================================
SERVER_CONFIG = {}


class Server(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # --------------------------------------------------
    # VERIFICA SE É ADMIN
    # --------------------------------------------------
    def is_admin(self, interaction: discord.Interaction) -> bool:
        perms = interaction.user.guild_permissions
        return perms.administrator or perms.manage_guild

    # --------------------------------------------------
    # ENVIA LOG SE ATIVADO
    # --------------------------------------------------
    async def send_log(self, guild: discord.Guild, embed: discord.Embed):
        config = SERVER_CONFIG.get(guild.id)
        if not config or not config.get("logs_ativo"):
            return

        canal = guild.get_channel(config.get("canal_logs"))
        if canal:
            await canal.send(embed=embed)

    # ==================================================
    # PAINEL ADMINISTRATIVO
    # ==================================================
    @app_commands.command(
        name="painel_admin",
        description="Painel administrativo do servidor"
    )
    async def painel_admin(self, interaction: discord.Interaction):
        if not self.is_admin(interaction):
            await interaction.response.send_message(
                "❌ Apenas administradores podem usar este painel.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="🛠️ Painel Administrativo",
            description=(
                "**📌 Comandos:**\n"
                "🧹 `/limpar`\n"
                "🔇 `/mute`\n"
                "🔊 `/unmute`\n\n"
                "**⚙️ Configurações:**\n"
                "📜 Canal de logs\n"
                "🔇 Cargo de mute"
            ),
            color=ROSA
        )

        view = PainelAdminView(interaction.guild)

        await interaction.response.send_message(
            embed=embed,
            view=view,
            ephemeral=True
        )

    # ==================================================
    # /limpar
    # ==================================================
    @app_commands.command(
        name="limpar",
        description="Apaga mensagens com confirmação"
    )
    async def limpar(self, interaction: discord.Interaction, quantidade: int):
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message(
                "❌ Você não tem permissão.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="⚠️ Confirmação",
            description=f"Apagar **{quantidade} mensagens**?",
            color=ROSA
        )

        view = ConfirmarLimpezaView(
            guild=interaction.guild,
            channel=interaction.channel,
            quantidade=quantidade,
            autor=interaction.user,
            send_log=self.send_log
        )

        await interaction.response.send_message(
            embed=embed,
            view=view,
            ephemeral=True
        )

    # ==================================================
    # /mute TEMPORÁRIO
    # ==================================================
    @app_commands.command(
        name="mute",
        description="Muta um membro temporariamente"
    )
    async def mute(
        self,
        interaction: discord.Interaction,
        membro: discord.Member,
        minutos: int
    ):
        if not self.is_admin(interaction):
            await interaction.response.send_message(
                "❌ Apenas administradores.",
                ephemeral=True
            )
            return

        if membro.guild_permissions.administrator:
            await interaction.response.send_message(
                "🛑 Não é possível mutar administradores.",
                ephemeral=True
            )
            return

        config = SERVER_CONFIG.get(interaction.guild.id)
        if not config or "cargo_mute" not in config:
            await interaction.response.send_message(
                "⚠️ Cargo de mute não configurado.",
                ephemeral=True
            )
            return

        cargo = interaction.guild.get_role(config["cargo_mute"])
        if not cargo:
            await interaction.response.send_message(
                "❌ Cargo de mute inválido.",
                ephemeral=True
            )
            return

        await membro.add_roles(cargo)

        await interaction.response.send_message(
            f"🔇 {membro.mention} mutado por **{minutos} minutos**.",
            ephemeral=True
        )

        embed = discord.Embed(
            title="🔇 Mute aplicado",
            description=f"{membro.mention} mutado por {minutos} minutos.",
            color=ROSA
        )
        await self.send_log(interaction.guild, embed)

        await asyncio.sleep(minutos * 60)

        if cargo in membro.roles:
            await membro.remove_roles(cargo)

    # ==================================================
    # /unmute
    # ==================================================
    @app_commands.command(
        name="unmute",
        description="Remove o mute de um membro"
    )
    async def unmute(self, interaction: discord.Interaction, membro: discord.Member):
        if not self.is_admin(interaction):
            await interaction.response.send_message(
                "❌ Apenas administradores.",
                ephemeral=True
            )
            return

        config = SERVER_CONFIG.get(interaction.guild.id)
        if not config or "cargo_mute" not in config:
            await interaction.response.send_message(
                "⚠️ Cargo de mute não configurado.",
                ephemeral=True
            )
            return

        cargo = interaction.guild.get_role(config["cargo_mute"])
        if cargo and cargo in membro.roles:
            await membro.remove_roles(cargo)

        await interaction.response.send_message(
            f"🔊 {membro.mention} desmutado.",
            ephemeral=True
        )


# ======================================================
# VIEW DO PAINEL ADMIN
# ======================================================
class PainelAdminView(View):
    def __init__(self, guild):
        super().__init__(timeout=None)
        self.guild = guild

    @discord.ui.button(label="📜 Canal de Logs", style=discord.ButtonStyle.green)
    async def logs(self, interaction: discord.Interaction, button):
        await interaction.response.send_message(
            "Selecione o canal de logs:",
            view=SelecionarCanalLogsView(self.guild),
            ephemeral=True
        )

    @discord.ui.button(label="🔇 Cargo de Mute", style=discord.ButtonStyle.danger)
    async def mute(self, interaction: discord.Interaction, button):
        await interaction.response.send_message(
            "Selecione o cargo de mute:",
            view=SelecionarCargoMuteView(self.guild),
            ephemeral=True
        )


# ======================================================
# VIEW → SELETOR DE CANAL LOGS
# ======================================================
class SelecionarCanalLogsView(View):
    def __init__(self, guild):
        super().__init__(timeout=60)
        self.guild = guild

        # ChannelSelect com callback
        self.channel_select = discord.ui.ChannelSelect(
            placeholder="Selecione o canal",
            channel_types=[discord.ChannelType.text],
            min_values=1,
            max_values=1
        )
        self.channel_select.callback = self.canal_selected
        self.add_item(self.channel_select)

    async def canal_selected(self, interaction: discord.Interaction):
        canal_id = self.channel_select.values[0].id

        SERVER_CONFIG.setdefault(self.guild.id, {})
        SERVER_CONFIG[self.guild.id]["logs_ativo"] = True
        SERVER_CONFIG[self.guild.id]["canal_logs"] = canal_id

        await interaction.response.send_message(
            f"✅ Logs configurados em <#{canal_id}>",
            ephemeral=True
        )
        self.stop()


# ======================================================
# VIEW → SELETOR DE CARGO MUTE
# ======================================================
class SelecionarCargoMuteView(View):
    def __init__(self, guild):
        super().__init__(timeout=60)
        self.guild = guild

        # RoleSelect com callback
        self.role_select = discord.ui.RoleSelect(
            placeholder="Selecione o cargo de mute",
            min_values=1,
            max_values=1
        )
        self.role_select.callback = self.role_selected
        self.add_item(self.role_select)

    async def role_selected(self, interaction: discord.Interaction):
        cargo_id = self.role_select.values[0].id

        SERVER_CONFIG.setdefault(self.guild.id, {})
        SERVER_CONFIG[self.guild.id]["cargo_mute"] = cargo_id

        await interaction.response.send_message(
            f"✅ Cargo de mute configurado: <@&{cargo_id}>",
            ephemeral=True
        )
        self.stop()


# ======================================================
# VIEW → CONFIRMAÇÃO LIMPEZA
# ======================================================
class ConfirmarLimpezaView(View):
    def __init__(self, guild, channel, quantidade, autor, send_log):
        super().__init__(timeout=30)
        self.guild = guild
        self.channel = channel
        self.quantidade = quantidade
        self.autor = autor
        self.send_log = send_log

    @discord.ui.button(label="Confirmar", style=discord.ButtonStyle.danger)
    async def confirmar(self, interaction, button):
        if interaction.user.id != self.autor.id:
            await interaction.response.send_message(
                "❌ Apenas quem executou.",
                ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)
        await self.channel.purge(limit=self.quantidade + 1)

        embed = discord.Embed(
            title="🧹 Limpeza",
            description=f"{self.autor.mention} apagou {self.quantidade} mensagens.",
            color=ROSA
        )
        await self.send_log(self.guild, embed)

        self.stop()

    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.secondary)
    async def cancelar(self, interaction, button):
        await interaction.response.send_message(
            "❌ Cancelado.",
            ephemeral=True
        )
        self.stop()


# ======================================================
# SETUP
# ======================================================
async def setup(bot: commands.Bot):
    await bot.add_cog(Server(bot))
