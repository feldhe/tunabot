import os
import logging
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

class Database:
    def __init__(self):
        self.client = None
        self.db = None

    async def connect(self):
        uri = os.getenv("MONGO_URI")
        if not uri:
            logging.error("❌ MONGO_URI não encontrada no .env!")
            return
        
        try:
            # 1. Cria o cliente
            self.client = AsyncIOMotorClient(uri)
            
            # 2. Define o banco de dados (Garante que não seja None)
            self.db = self.client["tunabot_db"] 
            
            # 3. Força uma verificação real de conexão
            await self.client.admin.command('ping')
            logging.info("✅ MongoDB conectado e autenticado com sucesso!")
            
        except Exception as e:
            logging.error(f"❌ Erro crítico ao conectar ao MongoDB: {e}")
            self.db = None

    async def create_user(self, user_id, user_name, guild_id, tc=100):

        # Verifica se a Conexão foi feita
        if not self.db is None:

            collection = self.db.get_collection('users')
            user = await self.read_user(user_id=user_id, guild_id=guild_id)
            # Caso não tenha user, cria um
            if not user:
                document = {"user_id": user_id,
                        "user_name": user_name,
                        "guild_id": guild_id,
                        "tc": tc
                         }
                await collection.insert_one(document)

        else:
            logging.error(f"❌ Use o 'db_instance.connect()'")
    
    async def read_user(self, user_id, guild_id):

        # Verifica se a Conexão foi feita
        if not self.db is None:

            filt = {"user_id": user_id, "guild_id": guild_id}

            collection = self.db.get_collection('users')
            user = await collection.find_one(filter=filt)
            return user

        else:
            logging.error(f"❌ Use o 'db_instance.connect()'")
    
    async def add_coins(self, user_id, user_name, guild_id, tc):
        
        # Verifica se a Conexão foi feita
        if not self.db is None:

            # Cria um user se não tiver
            await self.create_user(user_id=user_id, user_name=user_name, guild_id=guild_id, tc=tc)

            # Pega a quantidade de coins do user
            user = await self.read_user(user_id=user_id, guild_id=guild_id)
            if user:
                old_tc = user.get('tc')

                # Adiciona as coins
                collection = self.db.get_collection('users')
                filt = {"user_id": user_id, "guild_id": guild_id}
                await collection.update_one(filter=filt, update={"$set": {"tc": tc+old_tc}})
        
        else:
            logging.error(f"❌ Use o 'db_instance.connect()'")
    
    async def check_coins(self, user_id, guild_id):
        
        user = await self.read_user(user_id=user_id, guild_id=guild_id)
        if user:
           return user.get('tc')
            

# Instância única para o bot
db_instance = Database()