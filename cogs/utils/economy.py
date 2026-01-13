import discord
from discord.ext import commands
from discord import app_commands
from core.database import db_instance
import random
import asyncio
import gc  # Garbage Collector para limpeza de memória RAM
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import aiohttp

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.collection = None
        self.coin_emoji = "<:tuna_coin:1460334873628901498>"

    async def get_collection(self):
        if self.collection is None:
            self.collection = db_instance.db["users"]
        return self.collection

    async def clean_inactive_users(self):
        """Remove usuários inativos há mais de 10 dias e atualiza o timestamp do atual."""
        col = await self.get_collection()
        limite = datetime.utcnow() - timedelta(days=10)
        # Deleta documentos onde a última atividade foi há mais de 10 dias
        await col.delete_many({"last_active": {"$lt": limite}})

    async def update_activity(self, user_id, user_name):
        """Atualiza a data de última atividade do usuário."""
        col = await self.get_collection()
        await col.update_one(
            {"_id": user_id},
            {"$set": {"last_active": datetime.utcnow(), "username": user_name}},
            upsert=True
        )

    async def get_user_name(self, user_id):
        user = self.bot.get_user(user_id)
        if user: return user.display_name
        try:
            user = await self.bot.fetch_user(user_id)
            return user.display_name
        except: return "Membro Saiu"

    async def get_round_avatar(self, user_id, size):
        try:
            user = self.bot.get_user(user_id) or await self.bot.fetch_user(user_id)
            url = user.display_avatar.with_format("png").url
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200: return None
                    data = await resp.read()
            
            with Image.open(io.BytesIO(data)) as av_raw:
                av_img = av_raw.convert("RGBA").resize((size, size))
                mask = Image.new('L', (size, size), 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, size, size), fill=255)
                output = ImageOps.fit(av_img, mask.size, centering=(0.5, 0.5))
                output.putalpha(mask)
                return output
        except: return None

    async def create_pretty_rank(self, title, users):
        try:
            with Image.open("fundo.png").convert("RGBA").resize((1000, 680)) as img:
                draw = ImageDraw.Draw(img)
                try:
                    font_nomes = ImageFont.truetype("fonte.ttf", 26)
                    font_podio = ImageFont.truetype("fonte.ttf", 22)
                    font_moedas = ImageFont.truetype("fonte.ttf", 20)
                    coin_icon = Image.open("coin.png").convert("RGBA").resize((22, 22))
                except:
                    font_nomes = font_podio = font_moedas = ImageFont.load_default()
                    coin_icon = None

                for i, user_data in enumerate(users, 1):
                    user_id = user_data["_id"]
                    moedas = user_data.get("moedas", 0)
                    name = await self.get_user_name(user_id)

                    if i <= 3:
                        pos_x, pos_y = (285, 300) if i == 1 else (140, 360) if i == 2 else (430, 380)
                        av_size = 110 if i == 1 else 90
                        avatar = await self.get_round_avatar(user_id, av_size)
                        if avatar:
                            img.paste(avatar, (pos_x - av_size//2, pos_y), avatar)
                            avatar.close()
                        
                        nome_podio = name[:12]
                        w = draw.textlength(nome_podio, font=font_podio)
                        draw.text((pos_x - w//2, pos_y + av_size + 5), nome_podio, fill="white", font=font_podio)

                    if i <= 6:
                        x_lista_base, y_lista = 635, 110 + (i-1) * 85 + 10
                        cor_txt = (255, 215, 0) if i == 1 else (255, 255, 255)
                        draw.text((x_lista_base, y_lista), f"{i}º {name[:14]}", fill=cor_txt, font=font_nomes)
                        txt_moedas = f"{moedas:,}"
                        draw.text((x_lista_base, y_lista + 32), txt_moedas, fill=(200, 200, 200), font=font_moedas)
                        if coin_icon:
                            img.paste(coin_icon, (int(x_lista_base + draw.textlength(txt_moedas, font=font_moedas) + 10), y_lista + 32), coin_icon)

                if coin_icon: coin_icon.close()
                buffer = io.BytesIO()
                img.save(buffer, format='PNG', optimize=True)
                buffer.seek(0)
                gc.collect()
                return buffer
        except: return None

    # --- COMANDOS ---

    @app_commands.command(name="coinflip", description="Aposte moedas no cara ou coroa contra outro jogador")
    async def coinflip(self, interaction: discord.Interaction, usuario: discord.Member, aposta: int, escolha: str):
        if usuario.id == interaction.user.id:
            return await interaction.response.send_message("❌ Você não pode jogar contra si mesmo!", ephemeral=True)
        if aposta <= 0:
            return await interaction.response.send_message("❌ A aposta deve ser maior que zero!", ephemeral=True)

        col = await self.get_collection()
        await self.update_activity(interaction.user.id, interaction.user.name)
        
        p1_data = await col.find_one({"_id": interaction.user.id})
        p2_data = await col.find_one({"_id": usuario.id})

        if not p1_data or p1_data.get("moedas", 0) < aposta:
            return await interaction.response.send_message("❌ Você não tem saldo suficiente!", ephemeral=True)
        if not p2_data or p2_data.get("moedas", 0) < aposta:
            return await interaction.response.send_message(f"❌ {usuario.display_name} não tem saldo suficiente!", ephemeral=True)

        escolha_oponente = "Coroa" if escolha.lower() == "cara" else "Cara"
        
        embed = discord.Embed(
            title="🪙 Desafio de Coinflip",
            description=f"{interaction.user.mention} desafiou {usuario.mention}!\n💰 **Valor:** {aposta:,} {self.coin_emoji}\n\n"
                        f"{interaction.user.display_name}: **{escolha.capitalize()}**\n"
                        f"{usuario.display_name}: **{escolha_oponente}**",
            color=0xF1C40F
        )

        class CoinflipView(discord.ui.View):
            def __init__(self, desafiado):
                super().__init__(timeout=60)
                self.value = None
                self.desafiado = desafiado

            @discord.ui.button(label="Aceitar", style=discord.ButtonStyle.green)
            async def accept(self, btn_inter, button):
                if btn_inter.user.id != self.desafiado.id:
                    return await btn_inter.response.send_message("Apenas o desafiado pode aceitar!", ephemeral=True)
                self.value = True
                self.stop()

            @discord.ui.button(label="Recusar", style=discord.ButtonStyle.red)
            async def decline(self, btn_inter, button):
                if btn_inter.user.id != self.desafiado.id:
                    return await btn_inter.response.send_message("Apenas o desafiado pode recusar!", ephemeral=True)
                self.value = False
                self.stop()

        view = CoinflipView(usuario)
        await interaction.response.send_message(content=usuario.mention, embed=embed, view=view)
        await view.wait()

        if view.value is True:
            p1 = await col.find_one({"_id": interaction.user.id})
            p2 = await col.find_one({"_id": usuario.id})
            if p1.get("moedas", 0) < aposta or p2.get("moedas", 0) < aposta:
                return await interaction.edit_original_response(content="❌ Saldo insuficiente de um dos jogadores.", embed=None, view=None)

            frames = ["🪙 Girando: .", "🪙 Girando: ..", "🪙 Girando: ...", f"🪙 Girando: {escolha.capitalize()}!", f"🪙 Girando: {escolha_oponente}!"]
            for frame in frames[:4]:
                await interaction.edit_original_response(content=f"**{frame}**", embed=None, view=None)
                await asyncio.sleep(0.5)

            resultado = random.choice(["cara", "coroa"])
            ganhador = interaction.user if resultado == escolha.lower() else usuario
            perdedor = usuario if ganhador == interaction.user else interaction.user

            await col.update_one({"_id": ganhador.id}, {"$inc": {"moedas": aposta}, "$set": {"last_active": datetime.utcnow()}})
            await col.update_one({"_id": perdedor.id}, {"$inc": {"moedas": -aposta}, "$set": {"last_active": datetime.utcnow()}})

            res_embed = discord.Embed(
                title=f"🪙 Resultado: {resultado.capitalize()}!",
                description=f"🎉 {ganhador.mention} venceu e ganhou **{aposta:,}** moedas!\n💀 {perdedor.mention} perdeu a aposta.",
                color=0x2ecc71
            )
            await interaction.edit_original_response(content=None, embed=res_embed, view=None)
        else:
            await interaction.edit_original_response(content="❌ Desafio cancelado.", embed=None, view=None)

    @app_commands.command(name="pay", description="Transfira moedas para outro usuário")
    async def pay(self, interaction: discord.Interaction, usuario: discord.Member, quantia: int):
        if usuario.id == interaction.user.id:
            return await interaction.response.send_message("❌ Você não pode pagar a si mesmo.", ephemeral=True)
        if quantia <= 0:
            return await interaction.response.send_message("❌ Valor inválido.", ephemeral=True)

        col = await self.get_collection()
        autor_data = await col.find_one({"_id": interaction.user.id})
        if not autor_data or autor_data.get("moedas", 0) < quantia:
            return await interaction.response.send_message("❌ Saldo insuficiente.", ephemeral=True)

        await col.update_one({"_id": interaction.user.id}, {"$inc": {"moedas": -quantia}, "$set": {"last_active": datetime.utcnow()}})
        await col.update_one({"_id": usuario.id}, {"$inc": {"moedas": quantia}, "$set": {"last_active": datetime.utcnow(), "username": usuario.name}}, upsert=True)
        await interaction.response.send_message(f"✅ Você enviou {self.coin_emoji} **{quantia:,}** para {usuario.mention}.")

    @app_commands.command(name="daily", description="Resgate suas moedas diárias")
    async def daily(self, interaction: discord.Interaction):
        await interaction.response.defer()
        col = await self.get_collection()
        await self.clean_inactive_users()
        
        user_id = interaction.user.id
        agora = datetime.utcnow()
        user_data = await col.find_one({"_id": user_id}) or {}
        last_daily = user_data.get("last_daily")

        if last_daily and agora < last_daily + timedelta(days=1):
            restante = (last_daily + timedelta(days=1)) - agora
            h, r = divmod(int(restante.total_seconds()), 3600)
            m, _ = divmod(r, 60)
            return await interaction.followup.send(f"⏳ Volte em **{h}h {m}m**.")

        quantia = random.randint(1900, 3000)
        await col.update_one(
            {"_id": user_id},
            {"$inc": {"moedas": quantia}, "$set": {"last_daily": agora, "last_active": agora, "username": interaction.user.name}},
            upsert=True
        )
        await interaction.followup.send(f"{self.coin_emoji} **{interaction.user.display_name}**, ganhou **{quantia}** moedas!")

    @app_commands.command(name="conta", description="Verifica o valor em sua conta.")
    async def atm(self, interaction: discord.Interaction, usuario: discord.Member = None):
        target = usuario or interaction.user
        col = await self.get_collection()
        user_data = await col.find_one({"_id": target.id})
        moedas = user_data.get("moedas", 0) if user_data else 0
        embed = discord.Embed(title="🏦 Banco Tuna", description=f"{target.mention}: {self.coin_emoji} **{moedas:,}**", color=0xFFD700)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="rank_global", description="Ranking Global")
    async def rank_global(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.clean_inactive_users() # Limpa inativos antes de gerar o rank
        col = await self.get_collection()
        
        # FILTRO: moedas deve ser maior que 0 para aparecer no ranking
        cursor = col.find({"moedas": {"$gt": 0}}).sort("moedas", -1).limit(6)
        top_users = await cursor.to_list(length=6)
        
        if not top_users:
            return await interaction.followup.send("Ninguém possui moedas no momento para o ranking.")

        buffer = await self.create_pretty_rank("TOP GLOBAL", top_users)
        await interaction.followup.send(file=discord.File(fp=buffer, filename='rank.png'))

async def setup(bot):
    await bot.add_cog(Economy(bot))