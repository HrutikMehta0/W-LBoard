import os

from asyncio import sleep
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord import Intents
from discord import Embed
from discord.ext.commands import Bot as BotBase

currDir = os.path.dirname(__file__)
PREFIX = "-"
OWNER_IDS = []
COGS = [x for x in os.listdir(os.path.join(os.path.split(currDir)[0], "cogs")) if x.endswith(".py")]


class Ready(object):
    def __init__(self):
        for cog in COGS:
            setattr(self, os.path.splitext(os.path.basename(cog))[0], False)

    def ready_up(self, cog):
        setattr(self, os.path.splitext(os.path.basename(cog))[0], True)
        print(f"{cog} cog ready")

    def all_ready(self):
        return all([getattr(self, os.path.splitext(os.path.basename(cog))[0]) for cog in COGS])


class WLBoard(BotBase):
    def __init__(self, guild, channels):
        self.wlboard_channel = None
        self.PREFIX = PREFIX
        self.ready = False
        self.guild = None
        self.cogs_ready = Ready()
        self.guildVal = guild
        self.channels = channels
        self.scheduler = AsyncIOScheduler()
        super().__init__(
            command_prefix=PREFIX,
            owner_ids=OWNER_IDS,
            intents=Intents.all()
        )

    def setup(self):
        for cog in COGS:
            self.load_extension(f"lib.cogs.{cog}")
        print("setup complete")

    def run(self):
        with open("./lib/bot/token", "r", encoding="utf-8") as tf:
            self.TOKEN = tf.read()

        print("Running bot...")
        super().run(self.TOKEN, reconnect=True)

    async def on_connect(self):
        print("bot connected")

    async def on_disconnect(self):
        print("bot disconnected")

    async def on_error(self, event_method, *args, **kwargs):
        if event_method == "on_command_error":
            await args[0].send("Something went wrong.")
        await self.stdout.send("An error occurred.")
        raise

    async def on_ready(self):
        if not self.ready:
            self.ready = True
            self.wlboard_channel = self.get_channel(774440654465269781)
            self.guild = self.get_guild(self.guildVal)
            print("bot ready")
        else:
            print("bot reconnected")

    async def on_message(self, message):
        pass

    async def on_member_join(self, member):
        pass
