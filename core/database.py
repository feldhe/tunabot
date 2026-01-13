import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient

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

# Instância única para o bot
db_instance = Database()