import datetime
import os
import sys
import traceback
from unicodedata import numeric

import discord
from discord import Embed
from discord.ext import commands

from cogs.config import GuildId
from cogs.manage import is_developer

TOKEN, prefix = GuildId().get_token_and_prefix()

class config(commands.Cog):
    """BOTの設定"""
    def __init__(self, bot):
        self.bot = bot
        self.cog_list = GuildId().cog_list

    def choice_extension(self):
        list_text = ""
        numbers = ('one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten')
        for number, ext in zip(numbers, self.cog_list):
            list_text += f":{number}: : {ext}\n"
        list_text += ":zero: All extension reload"

        embed = Embed(
            title='**Which extension would you reload?**',
            description=list_text,
            color=0x00ffff,)

        return embed

    async def load_extensions(self, ctx, func_name: object, ext_list: list, text: str='ロード') -> None:
        await ctx.send('-' * 30)
        for ext_name in ext_list:
            try:
                func_name(ext_name)
            except Exception as e:
                fmt = '{}に失敗しました： ```py\n{}: {}\n```'
                await ctx.send(fmt.format(text, type(e).__name__, e))
                await ctx.send('-' * 30)

                print(f'Failed to road extension {ext_name}.', file=sys.stderr)
                traceback.print_exc()
                print('-' * 30)
            else:
                await ctx.send(f"'{ext_name}' を{text}しました")
                await ctx.send('-' * 30)

        await ctx.send(f'すべての{text}を終了しました')
        await ctx.send('-' * 30)

    @commands.command()
    @is_developer()
    async def reload(self, ctx, *extensions: str):
        channel  = ctx.channel
        author = ctx.author.id
        ext_list = []

        if not len(extensions):
            embed = self.choice_extension()
            await ctx.send(embed=embed)

            def check(m):
                return m.channel == channel and m.author.id == author
            num = await self.bot.wait_for('message', check=check)

            for number in num.content.split():
                if number == '0':
                    ext_list = self.cog_list
                    break
                elif number.isnumeric():
                    ext_list.append(self.cog_list[int(num.content) - 1])
        else:
            for extension in extensions:
                ext_list.append(extension)

        await self.load_extensions(ctx, self.bot.reload_extension, ext_list)

    @commands.command()
    @is_developer()
    async def load(self, ctx, *extensions: str):
        await self.load_extensions(ctx, self.bot.load_extension, extensions)

    @commands.command()
    @is_developer()
    async def unload(self, ctx, *extensions: str):
        await self.load_extensions(ctx, self.bot.unload_extension, extensions, 'アンロード')

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def activity_init(self, ctx):
        activity = discord.Activity()
        await self.bot.change_presence(status=discord.Status.online, activity=activity)

    # change bot's activity
    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def activity(self, ctx, *, text: str):
        activity = discord.Activity(name=text, type=discord.ActivityType.watching)
        await self.bot.change_presence(status=discord.Status.online, activity=activity)

    @commands.command()
    @is_developer()
    async def restart(self, ctx):
        await ctx.send('再起動します')
        [self.bot.unload_extension(e) for e in self.cog_list]
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
