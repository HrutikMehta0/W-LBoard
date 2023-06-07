import discord
from discord.ext import commands
import aiosqlite
import asyncio


class wlboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Ready")
        setattr(self.bot, "db", await aiosqlite.connect("./data/wlboard.db"))
        await asyncio.sleep(2)
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("CREATE TABLE IF NOT EXISTS wlSetup (wlLimit INTEGER, channel INTEGER, guild INTEGER)")
        await self.bot.db.commit()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        emoji = payload.emoji
        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        wls = 0
        print("Reaction Added")
        if emoji.name == "🇼":
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("SELECT wlLimit FROM wlSetup WHERE guild = ?", (guild.id,))
                wlLimit = await cursor.fetchone()
                await cursor.execute("SELECT channel FROM wlSetup WHERE guild = ?", (guild.id,))
                channelTest = await cursor.fetchone()
                if wlLimit:
                    wlLimit = wlLimit[0]
                    channelData = guild.get_channel(channelTest[0])
                    for reaction in message.reactions:
                        if reaction.emoji == "🇼":
                            wls += 1
                            if reaction.count >= wlLimit:
                                embed = discord.Embed(title="New W", color=message.author.color,
                                                      timestamp=message.created_at)
                                fields = [("Author", message.author.mention, False),
                                          ("",message.content, False)]
                                for name, value, inline in fields:
                                    print(name, value, inline)
                                    embed.add_field(name=name, value=value, inline=inline)
                                if len(message.attachments):
                                    embed.set_image(url=message.attachments[0].url)
                                await channelData.send(f"**{reaction.count}** 🇼 | {channel}", embed=embed)
                                print("Sent")
        elif emoji.name == "🇱":
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("SELECT wlLimit FROM wlSetup WHERE guild = ?", (guild.id,))
                wlLimit = await cursor.fetchone()
                await cursor.execute("SELECT channel FROM wlSetup WHERE guild = ?", (guild.id,))
                channelTest = await cursor.fetchone()
                if wlLimit:
                    wlLimit = wlLimit[0]
                    channelData = guild.get_channel(channelTest[0])
                    for reaction in message.reactions:
                        if reaction.emoji == "🇱":
                            wls -= 1
                            if reaction.count >= wlLimit:
                                embed = discord.Embed(title="New L", description=f"{message.content}")
                                if len(message.attachments):
                                    embed.set_image(url=message.attachments[0].url)
                                await channelData.send(embed=embed)
        else:
            print("Nope")
        # if wls < 0:
        #     embed = discord.Embed(title="New L", description=f"{message.content}")
        #     await channelData.send(embed=embed)
        # elif wls > 0:
        #     embed = discord.Embed(title="New W", description=f"{message.content}")
        #     await channelData.send(embed=embed)

    @commands.group(pass_context=True)
    async def setup(self, ctx):
        if ctx.invoked_subcommand is None:
            return await ctx.send("This doesn't exist")

    @setup.command()
    @commands.has_permissions(manage_guild=True)
    async def channel(self, ctx, channel: discord.TextChannel):
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT channel FROM wlSetup WHERE guild = ?", (ctx.guild.id,))
            channelData = await cursor.fetchone()
            if channelData:
                channelData = channelData[0]
                if channelData == channel.id:
                    return await ctx.send("This channel is already the WLBoard channel")
                await cursor.execute("UPDATE wlSetup SET channel = ? WHERE guild = ?", (channel.id, ctx.guild.id))
                await ctx.send(f"Updated WLBoard channel to {channel.mention}")
            else:
                await cursor.execute("INSERT INTO wlSetup VALUES (?, ?, ?)", (5, channel.id, ctx.guild.id))
                await ctx.send(f"Set WLBoard channel to {channel.mention}")
        await self.bot.db.commit()

    @setup.command()
    @commands.has_permissions(manage_guild=True)
    async def limit(self, ctx, wl: int):
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT wlLimit FROM wlSetup WHERE guild = ?", (ctx.guild.id,))
            wlData = await cursor.fetchone()
            if wlData:
                wlData = wlData[0]
                if wlData == wl:
                    return await ctx.send(f"This {wlData} is already the WL Limit")
                await cursor.execute("UPDATE wlSetup SET wlLimit = ? WHERE guild = ?", (wl, ctx.guild.id))
                await ctx.send(f"Set WL Limit to {wl}")
            else:
                await cursor.execute("INSERT INTO wlSetup VALUES (?, ?, ?)", (wl, 0, ctx.guild.id))
                await ctx.send(f"Set WL Limit to {wl}")

        await self.bot.db.commit()

    @commands.command()
    async def ping(self, ctx):
        await ctx.send("Hello")


async def setup(bot):
    await bot.add_cog(wlboard(bot))
