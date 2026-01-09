# main.py
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()  # lê o arquivo .env
TOKEN = os.getenv("TOKEN")  # pega o token secreto


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

    cogs = os.listdir('cogs')
    for folder in cogs:
        if not folder.startswith('__'):
            arqs = os.listdir(f'cogs/{folder}')
            for cmd in arqs:
                if cmd.endswith('.py') and not cmd.startswith('__'):
                    try:
                        await bot.load_extension(f'cogs.{folder}.{cmd[:-3]}')
                        print(f"✅ {cmd} carregada")
                    except Exception as e:
                        print(f"❌ Erro ao carregar {cmd}: {e}")

    # Sincroniza todos os slash commands
    synced = await bot.tree.sync()
    print(f"🌸 {len(synced)} slash commands sincronizados")


# ⚠️ Atribui a função de setup_hook ao bot
bot.setup_hook = setup_hook

# ======================================================
# INICIA O BOT
# ======================================================
bot.run(f'{TOKEN}')
