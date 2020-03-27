import datetime
import os
import sys

import discord
from discord.ext import commands

from bot import fetch_extensions
from cogs.config import GuildId
from cogs.manage import is_developer

TOKEN, prefix = GuildId().get_token_and_prefix()

class config(commands.Cog):
    """BOTの設定"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def activity_init(self, ctx):
        activity = discord.Activity(
            name='ご注文はうさぎですか？',
            url='http://www.dokidokivisual.com/',
            type=discord.ActivityType.watching,
            state='In front of TV',
            details='カフェラテ・カフェモカ・カプチーノ',
            start=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))),
            large_image_url='https://gochiusa.com/01/core_sys/images/main/logo.png',
            large_image_text='Is the Order a Rabbit?',
            )
        await self.bot.change_presence(status=discord.Status.online, activity=activity)

    # change bot's activity
    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def activity(self, ctx, *args):
        activity = discord.Activity(name=' '.join(args), type=discord.ActivityType.watching)
        await self.bot.change_presence(status=discord.Status.online, activity=activity)

    @commands.command()
    @is_developer()
    async def restart(self, ctx):
        await ctx.send('再起動します')
        [self.bot.unload_extension(e) for e in fetch_extensions()]
        self.bot.clear()

        await self.bot.login(token=TOKEN, bot=True)
        await self.bot.connect()

    @commands.command()
    @is_developer()
    async def shutdown(self, ctx, Option: str=""):
        if Option != '-q':
            def check(m: object) -> bool:
                return m.channel.id == ctx.channel.id and m.author.id == ctx.author.id
            await ctx.send('シャットダウンします\n続行するには [y] を送信してください')
            msg = await self.bot.wait_for('message', check=check)
            if not (msg.content in ['y', 'Y']):
                return

        await ctx.send('ﾉｼ')
        await self.bot.logout()

def setup(bot):
    bot.add_cog(config(bot))
