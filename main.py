import os
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv
from database import db_instance # Importamos a conexão que você criou

# ======================================================
# CARREGA .ENV E CONFIGURAÇÕES
# ======================================================
load_dotenv()

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise RuntimeError("TOKEN não encontrado no arquivo .env")

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
)

# ======================================================
# INTENTS
# ======================================================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True # Importante para comandos de prefixo (!)

# ======================================================
# CLASSE PRINCIPAL DO BOT
# ======================================================
class TunaBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents
        )

    async def setup_hook(self):
        # 1. Inicializa o MongoDB
        await db_instance.connect()
        
        # 2. Carrega as Cogs de forma recursiva (dentro de subpastas)
        await self.load_all_cogs()
        
        # 3. Sincroniza comandos Slash
        try:
            synced = await self.tree.sync()
            logging.info(f"✅ {len(synced)} slash commands sincronizados")
        except Exception as e:
            logging.error(f"❌ Erro ao sincronizar comandos: {e}")

    async def load_all_cogs(self):

        """Varre a pasta cogs e suas subpastas para carregar os arquivos .py"""
        cogs = os.listdir('cogs')
        for categ in cogs:
            if not categ.startswith('_'):
                categ_folder = os.listdir(f'cogs/{categ}')
                for cmd_folder in categ_folder:
                    if not cmd_folder.startswith('_'):
                        cmds_arqs = os.listdir(f'cogs/{categ}/{cmd_folder}')
                        for cmd in cmds_arqs:
                            if not cmd.startswith('_') and cmd.endswith('.py'):
                                
                                # Transforma o caminho no formato 'cogs.pasta.arquivo'
                                extension = f"cogs.{categ}.{cmd_folder}.{cmd[:-3]}"
                                try:
                                    await self.load_extension(extension)
                                    logging.info(f"🧩 Cog carregada: {extension}")
                                except Exception as e:
                                    logging.error(f"❌ Erro ao carregar {extension}: {e}")

    async def on_ready(self):
        logging.info(f"🚀 Conectado como {self.user}")

# ======================================================
# EXECUÇÃO
# ======================================================
bot = TunaBot()
bot.run(TOKEN)