import discord
from discord.ext import commands
import aiosqlite
import asyncio
from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle

class messageLinkButton(discord.ui.Button):
    def __init__(self, url):
        super().__init__(style=discord.ButtonStyle.link, url=url, label="Message Link")


class wlboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.w = 0
        self.l = 0

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
        User = await self.bot.fetch_user(message.author.id)
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
                            self.w += 1
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
                            self.l += 1
        else:
            print("Nope")
        if self.w - self.l < 0:
            embed = discord.Embed(title="", color=0xf1415f,
                                  timestamp=message.created_at)
            embed.set_author(name=message.author.display_name, icon_url=User.avatar, url=message.jump_url)
            fields = [("", message.content, False)]
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
            if len(message.attachments):
                embed.set_image(url=message.attachments[0].url)
            await channelData.send(
                f"**{reaction.count}** :regional_indicator_l:| {channel.mention}", embed=embed)
        elif self.w - self.l > 0:
            embed = discord.Embed(title="", color=0x5dac61,
                                  timestamp=message.created_at)
            embed.set_author(name=message.author.display_name, icon_url=User.avatar, url=message.jump_url)
            fields = [("", message.content, False)]
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
            if len(message.attachments):
                embed.set_image(url=message.attachments[0].url)
            await channelData.send(
                f"**{reaction.count}** 🇼 | {channel.mention}", embed=embed)
        elif self.w - self.l == 0:
            embed = discord.Embed(title="", color=discord.Color.light_grey(),
                                  timestamp=message.created_at)
            embed.set_author(name=message.author.display_name, icon_url=User.avatar, url=message.jump_url)
            fields = [("", message.content, False)]
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
            if len(message.attachments):
                embed.set_image(url=message.attachments[0].url)
            await channelData.send(
                f"**{wlLimit}** 🇼s | **{wlLimit}** :regional_indicator_l:s  | {channel.mention}", embed=embed)

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
