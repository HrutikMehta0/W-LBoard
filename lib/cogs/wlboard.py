from datetime import datetime
from discord.ext.commands import Cog
from discord import Embed
from ..db import db


class wlboard(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            await self.bot.wlboard_channel.send("W-LBoard is now online!")
            self.bot.cogs_ready.ready_up("wlboard")

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.emoji.name == "🇼":
            message = await self.wlboard_channel.fetch_message(payload.message_id)
            stars = db.field("SELECT Stars FROM wlboard WHERE MessageID = ?", message.id) or 0
            if not message.author.bot and payload.member.id != message.author.id:
                embed = Embed(title="W Message", colour=message.author.colour, timestamp=datetime.utcnow())
                fields = [("Author", message.author.mention, False),
                          ("Content", message.content or "See attachment", False), ("Stars", stars + 1, False)]
                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)
                if len(message.attachments):
                    embed.set_image(url=message.attachments[0].url)

                await self.wlboard_channel.send(embed=embed)

            else:
                embed = Embed(title="W Message", colour=message.author.colour, timestamp=datetime.utcnow())
                fields = [("Author", message.author.mention, False),
                          ("Content", message.content or "See attachment", False), ("Stars", stars + 1, False)]
                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)
                if len(message.attachments):
                    embed.set_image(url=message.attachments[0].url)

                await self.wlboard_channel.send(embed=embed)
        else:
            print("ERROR")

def setup(bot):
    bot.add_cog(wlboard(bot))