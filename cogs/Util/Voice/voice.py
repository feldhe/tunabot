# cogs/cog_voice.py
import discord
from discord.ext import commands


class VoiceCog(commands.Cog):
    """
    Cog responsável por:
    - Conectar automaticamente o bot a uma call fixa
    - Reforçar a conexão caso o bot seja movido ou kickado
    """

    # ===============================
    # IDs FIXOS (modifique conforme seu servidor)
    # ===============================
    GUILD_ID = 1457730028606324937
    VOICE_CHANNEL_ID = 1457730031819165842

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ===============================
    # Evento: Bot fica online
    # ===============================
    @commands.Cog.listener()
    async def on_ready(self):
        print("[VoiceCog] 🤖 Bot online. Conectando na call...")
        await self.force_connect()

    # ===============================
    # Evento: Estado de voz de algum membro mudou
    # ===============================
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.id != self.bot.user.id:
            return

        # Se o bot foi removido da call, reconectar
        if before.channel is not None and after.channel is None:
            print("[VoiceCog] 🚨 Bot removido da call! Reconectando...")
            await self.force_connect()

    # ===============================
    # Função principal de conexão
    # ===============================
    async def force_connect(self):
        guild = self.bot.get_guild(self.GUILD_ID)
        if not guild:
            print(f"[VoiceCog] ❌ Servidor {self.GUILD_ID} não encontrado")
            return

        channel = guild.get_channel(self.VOICE_CHANNEL_ID)
        if not channel or not isinstance(channel, discord.VoiceChannel):
            print(f"[VoiceCog] ❌ Canal de voz {self.VOICE_CHANNEL_ID} inválido")
            return

        # Verifica se o bot já está conectado
        if guild.voice_client:
            if guild.voice_client.channel.id == channel.id:
                return
            await guild.voice_client.disconnect(force=True)

        try:
            await channel.connect(reconnect=True)
            print(f"[VoiceCog] 🔒 Bot conectado em '{channel.name}' ({channel.id})")
        except Exception as e:
            print(f"[VoiceCog] ❌ Erro ao conectar na call: {e}")


# ===============================
# Setup obrigatório para o bot
# ===============================
async def setup(bot: commands.Bot):
    await bot.add_cog(VoiceCog(bot))
