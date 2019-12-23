from   discord.ext import commands
import discord

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


    # BOTのアクティビティを変更
    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def activity(self, ctx, *args):
        game = discord.Game(' '.join(args))
        await self.bot.change_presence(status=discord.Status.online, activity=game)


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
    async def shutdown(self, ctx):
        await ctx.send('ﾉｼ')
        await self.bot.logout()


def setup(bot):
    bot.add_cog(config(bot))