# main.py
import discord
from discord.ext import commands

# ======================================================
# INTENTS (permissões que o bot pode "enxergar")
# ======================================================
intents = discord.Intents.default()
intents.members = True  # Necessário se futuramente quiser detectar entradas de membros

# ======================================================
# INICIALIZAÇÃO DO BOT
# ======================================================
bot = commands.Bot(
    command_prefix="!",  # Não usado se tudo for slash commands
    intents=intents
)

# ======================================================
# EVENTO: BOT LIGOU
# ======================================================
@bot.event
async def on_ready():
    print(f"🤖 Conectado como {bot.user}")
    print(f"🌸 Servidores: {len(bot.guilds)}")
    print(f"🧠 Cogs carregadas: {len(bot.cogs)}")


# ======================================================
# FUNÇÃO DE CARREGAMENTO AUTOMÁTICO DE COGS
# ======================================================
async def setup_hook():
    print("🔁 Carregando cogs...")

    cogs = [
        "cogs.cog_admin",
        "cogs.cog_utilidades",
        "cogs.cog_embeds",
        "cogs.cog_help",
        "cogs.cog_server",
        "cogs.cog_voice"
    ]

    for cog in cogs:
        try:
            await bot.load_extension(cog)
            print(f"✅ {cog} carregada")
        except Exception as e:
            print(f"❌ Erro ao carregar {cog}: {e}")

    # Sincroniza todos os slash commands
    synced = await bot.tree.sync()
    print(f"🌸 {len(synced)} slash commands sincronizados")


# ⚠️ Atribui a função de setup_hook ao bot
bot.setup_hook = setup_hook

# ======================================================
# INICIA O BOT
# ======================================================
bot.run("MTQ1MDU4NDM4OTY4Njc4ODMwMg.G6_grH.GOh5W6mgbAGYheLs6T4z4fGq09EOl_Rmxv3SNs")
