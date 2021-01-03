from discord.ext import commands
from env import TOKEN
from cogs.configuration import get_prefix

bot = commands.Bot(command_prefix=get_prefix)
COGS = ['configuration', 'voice']

for cog in COGS:
    bot.load_extension(f"cogs.{cog}")

@bot.event
async def on_ready():
    print(f"Bot has logged in as {bot.user}!")

bot.run(TOKEN)