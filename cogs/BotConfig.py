from   discord.ext import commands
import discord

import datetime
import os
import sys

from   bot         import fetch_extensions
from   .manage     import is_developer
from   .config     import GuildId

config_instance  = GuildId()
(TOKEN, prefix) = config_instance.get_token_and_prefix()

class config(commands.Cog):
    """BOTの設定
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def activity_init(self, ctx):
        activity = discord.Activity(
            name='Is the Order a Rabbit?',
            url='http://www.dokidokivisual.com/',
            type=discord.ActivityType.watching,
            state='In front of TV',
            details='カフェラテ・カフェモカ・カプチーノ！',
            start=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))),
            large_image_url='https://gochiusa.com/01/core_sys/images/main/logo.png',
            large_image_text='ご注文はうさぎですか？',
            )
        await self.bot.change_presence(status=discord.Status.online, activity=activity)

    # BOTのアクティビティを変更
    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def activity(self, ctx, *args):
        activity = discord.Activity(name=' '.join(args), type=discord.ActivityType.watching)
        await self.bot.change_presence(status=discord.Status.online, activity=activity)

    # BOTの再起動
    @commands.command()
    @is_developer()
    async def restart(self, ctx):
        await ctx.send('再起動します')

        # extensionをアンロードする
        for ext_name in fetch_extensions():
            self.bot.unload_extension(ext_name)

        # BOTを再オープンする
        self.bot.clear()

        # BOTをDiscordにログイン、接続
        await self.bot.login(token=TOKEN, bot=True)
        await self.bot.connect()

    # BOTをシャットダウンする
    @commands.command()
    @is_developer()
    async def shutdown(self, ctx, Option):
        if Option != '-q':
            def check(m):
                return m.channel == ctx.channel and m.author.id == ctx.author.id
            await ctx.send('シャットダウンします\n続行するには [y] を送信してください')
            msg = await self.bot.wait_for('message', check=check)

            if msg.content == 'y' or msg.content == 'Y':
                await ctx.send('ﾉｼ')
                await self.bot.logout()

        else:
            await ctx.send('ﾉｼ')
            await self.bot.logout()

def setup(bot):
    bot.add_cog(config(bot))