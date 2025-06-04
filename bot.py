import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio
from views import CriarEscalacaoModal

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Definir intents
intents = discord.Intents.default()
intents.message_content = True

# Inicializar o bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Dicionário para controlar o tempo entre comandos por usuário
user_cooldowns = {}

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} comandos de barra sincronizados.")
    except Exception as e:
        print(f"❌ Erro ao sincronizar comandos: {e}")

# Comando de barra para iniciar a escalação
@bot.tree.command(name="escalar", description="Iniciar uma nova escalação")
async def escalar(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    current_time = asyncio.get_event_loop().time()
    
    # Verifica o cooldown do usuário cooldow def->5
    if user_id in user_cooldowns:
        time_diff = current_time - user_cooldowns[user_id]
        if time_diff < 5:
            wait_time = round(5 - time_diff)
            try:
                await interaction.response.send_message(
                    f"Por favor, aguarde {wait_time} segundos antes de usar o comando novamente.",
                    ephemeral=True
                )
            except discord.errors.InteractionResponded:
                return
            return
    
    try:
        # Tenta enviar o modal
        await interaction.response.send_modal(CriarEscalacaoModal())
        user_cooldowns[user_id] = current_time
    except discord.errors.NotFound:
        # Se a interação expirou, não podemos fazer nada
        return
    except discord.errors.HTTPException as e:
        # Se a interação ainda não foi respondida
        if not interaction.response.is_done():
            try:
                if e.code == 429:  # Rate limit
                    await interaction.response.send_message(
                        "O bot está recebendo muitos comandos. Por favor, tente novamente em alguns segundos.",
                        ephemeral=True
                    )
                else:
                    await interaction.response.send_message(
                        "Ocorreu um erro ao criar a escalação. Tente novamente.",
                        ephemeral=True
                    )
            except (discord.errors.InteractionResponded, discord.errors.NotFound):
                # Se a interação já foi respondida ou expirou, ignoramos
                pass

# Rodar o bot
bot.run(TOKEN)
