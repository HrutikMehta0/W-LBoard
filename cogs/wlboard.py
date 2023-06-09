import discord
import requests as requests
import re
from discord import ButtonStyle
from discord.ext import commands
import aiosqlite
import asyncio


class messageLinkButton(discord.ui.Button):
    def __init__(self, url):
        super().__init__(style=discord.ButtonStyle.link, url=url, label="Message Link")


class wlboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.w = 0
        self.l = 0
        self.wemoji = None
        self.lemoji = None
        self.wlLimit = 0
        self.channel = None

    def get_gif_url(view_url):

        # Get the page content
        page_content = requests.get(view_url).text

        # Regex to find the URL on the c.tenor.com domain that ends with .gif
        regex = r"(?i)\b((https?://c[.]tenor[.]com/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))[.]gif)"

        # Find and return the first match
        return re.findall(regex, page_content)[0][0]

    def set_reactionCount(self, message):
        for reaction in message.reactions:
            if ":w_:" in str(reaction.emoji):
                print(self.wemoji)
                if self.wemoji is None:
                    self.wemoji = reaction.emoji
                self.w = reaction.count
                print(reaction.count)
            elif ":l_:" in str(reaction.emoji):
                if self.lemoji is None:
                    self.lemoji = reaction.emoji
                self.l = reaction.count
                print(reaction.count)
        if not any(":w_:" in str(reaction.emoji) for reaction in message.reactions):
            self.w = 0
        if not any(":l_:" in str(reaction.emoji) for reaction in message.reactions):
            self.l = 0

    async def get_limit_channel(self, guild):
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT wlLimit FROM wlSetup WHERE guild = ?", (guild.id,))
            self.wlLimit = await cursor.fetchone()
            await cursor.execute("SELECT channel FROM wlSetup WHERE guild = ?", (guild.id,))
            self.channel = await cursor.fetchone()

    async def get_message(self, message, channelData):
        async for mes in channelData.history(limit=200):
            if len(mes.embeds) > 0:
                if message.content == mes.embeds[0].to_dict()["fields"][0]["value"]:
                    return mes

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
        guild = self.bot.get_guild(payload.guild_id)
        await self.get_limit_channel(guild)
        channel = guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        User = await self.bot.fetch_user(message.author.id)
        print("Reaction Added")
        wlLimit = self.wlLimit[0]
        channelData = guild.get_channel(self.channel[0])
        self.set_reactionCount(message)

        if ":w_" in str(payload.emoji) or ":l_" in str(payload.emoji):
            if self.w - self.l < 0 and self.l >= wlLimit:  # If it is an L and the limit is reached
                embed = discord.Embed(title="", color=0xf1415f,
                                      timestamp=message.created_at)
                embed.set_author(name=message.author.display_name, icon_url=User.avatar, url=message.jump_url)
                fields = [("", message.content, False)]
                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)
                if len(message.attachments):
                    embed.set_image(url=message.attachments[0].url)

                mes = await self.get_message(message, channelData)
                print(mes)
                if mes is not None:
                    if self.w > 0:
                        await mes.edit(
                            content=f"**{self.w}** {self.wemoji} | **{self.l}** {self.lemoji} | {channel.mention}",
                            embed=embed)
                    else:
                        await mes.edit(
                            content=f"**{self.l}** {self.lemoji}  | {channel.mention}",
                            embed=embed)
                elif self.w > 0:
                    await channelData.send(
                        content=f"**{self.w}** {self.wemoji} | **{self.l}** {self.lemoji}  | {channel.mention}",
                        embed=embed)
                else:
                    await channelData.send(
                        content=f"**{self.l}** {self.lemoji}  | {channel.mention}",
                        embed=embed)

            elif self.w - self.l > 0 and self.w >= wlLimit: # If it is a W and the limit is reached
                embed = discord.Embed(title="", color=0x5dac61,
                                      timestamp=message.created_at)
                embed.set_author(name=message.author.display_name, icon_url=User.avatar, url=message.jump_url)
                fields = [("", message.content, False)]
                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)
                if len(message.attachments):
                    embed.set_image(url=message.attachments[0].url)

                mes = await self.get_message(message, channelData)
                print(mes)
                if mes is not None:
                    if self.l > 0:
                        await mes.edit(
                            content=f"**{self.w}** {self.wemoji} | **{self.l}** {self.lemoji}  | {channel.mention}",
                            embed=embed)
                    else:
                        await mes.edit(
                            content=f"**{self.w}** {self.wemoji}  | {channel.mention}",
                            embed=embed)
                elif self.l > 0:
                    await channelData.send(
                        content=f"**{self.w}** {self.wemoji} | **{self.l}** {self.lemoji}  | {channel.mention}",
                        embed=embed)
                else:
                    await channelData.send(
                        content=f"**{self.w}** {self.wemoji}  | {channel.mention}",
                        embed=embed)

            elif self.w - self.l == 0 and self.w != 0 and self.w >= wlLimit: # If it is a W and the limit is reached
                embed = discord.Embed(title="", color=discord.Color.light_grey(),
                                      timestamp=message.created_at)
                embed.set_author(name=message.author.display_name, icon_url=User.avatar, url=message.jump_url)
                fields = [("", message.content, False)]
                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)
                if len(message.attachments):
                    embed.set_image(url=message.attachments[0].url)

                mes = await self.get_message(message, channelData)
                print(mes)
                if mes is not None:
                    await mes.edit(
                        content=f"**{self.w}** {self.wemoji} | **{self.l}** {self.lemoji}  | {channel.mention}",
                        embed=embed)
                else:
                    await channelData.send(
                        content=f"**{self.w}** {self.wemoji} | **{self.l}** {self.lemoji}  | {channel.mention}",
                        embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        await self.get_limit_channel(guild)
        channel = guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        User = await self.bot.fetch_user(message.author.id)
        print("Reaction Removed")
        wlLimit = self.wlLimit[0]
        channelData = guild.get_channel(self.channel[0])
        self.set_reactionCount(message)

        if self.w == 0 and self.l == 0:
            mes = await self.get_message(message, channelData)
            print(mes)
            if mes is not None:
                await mes.delete()
                return
        elif self.w - self.l < 0 and self.l >= wlLimit: # If it is an L and the limit is reached
            embed = discord.Embed(title="", color=0xf1415f,
                                  timestamp=message.created_at)
            embed.set_author(name=message.author.display_name, icon_url=User.avatar, url=message.jump_url)
            fields = [("", message.content, False)]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            if len(message.attachments):
                embed.set_image(url=message.attachments[0].url)

            mes = await self.get_message(message, channelData)
            print(mes)
            if mes is not None:
                if self.w > 0:
                    await mes.edit(
                        content=f"**{self.w}** {self.wemoji} | **{self.l}** {self.lemoji}  | {channel.mention}",
                        embed=embed)
                else:
                    await mes.edit(
                        content=f"**{self.l}** {self.lemoji}  | {channel.mention}",
                        embed=embed)

        elif self.w - self.l > 0 and self.w >= wlLimit: # If it is a W and the limit is reached
            embed = discord.Embed(title="", color=0x5dac61,
                                  timestamp=message.created_at)
            embed.set_author(name=message.author.display_name, icon_url=User.avatar, url=message.jump_url)
            fields = [("", message.content, False)]
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
            if len(message.attachments):
                embed.set_image(url=message.attachments[0].url)

            mes = await self.get_message(message, channelData)
            print(mes)
            if mes is not None:
                if self.l > 0:
                    await mes.edit(
                        content=f"**{self.w}** {self.wemoji} | **{self.l}** {self.lemoji}  | {channel.mention}",
                        embed=embed)
                else:
                    await mes.edit(
                        content=f"**{self.w}** {self.wemoji}  | {channel.mention}",
                        embed=embed)

        elif self.w - self.l == 0 and self.w != 0:
            embed = discord.Embed(title="", color=discord.Color.light_grey(),
                                  timestamp=message.created_at)
            embed.set_author(name=message.author.display_name, icon_url=User.avatar, url=message.jump_url)
            fields = [("", message.content, False)]
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
            if len(message.attachments):
                embed.set_image(url=message.attachments[0].url)

            mes = await self.get_message(message, channelData)
            print(mes)
            if mes is not None:
                await mes.edit(
                    content=f"**{self.w}** {self.wemoji} | **{self.l}** {self.lemoji}  | {channel.mention}",
                    embed=embed)

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
