import asyncio
import os
import discord
from discord.ext import commands

guild = 546243371602149406
channels = {'wlboard': 1113648494096420944, 'botSpam': 774440654465269781}

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='-', intents=intents)



async def load():
    for file in os.listdir('./cogs'):
        if file.endswith('.py'):
            await bot.load_extension(f'cogs.{file[:-3]}')
            print(f'Loaded {file[:-3]}')


async def main():
    await load()
    #with open('token.txt', 'r') as f:
     #   lines = f.readlines()
    await bot.start('')
    #await bot.start(os.environ['TOKEN']) # For Mac

asyncio.run(main())
