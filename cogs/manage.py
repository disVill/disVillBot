import asyncio
import copy
import sys
import traceback
from unicodedata import numeric

import discord
from discord import Embed
from discord.ext import commands

from bot import fetch_extensions
from cogs.config import GuildId

ID = GuildId().get_id()

def is_developer():
    """コマンドの実行者が開発者か確認する"""
    async def predicate(ctx):
        if ctx.author.id == ID['user']['develop']:
            return True
        await ctx.send("実行する権限がありません")
    return commands.check(predicate)

class manage(commands.Cog):
    """discordサーバの管理系コマンド"""
    def __init__(self, bot):
        self.bot = bot
        self.channel_member = self.bot.get_channel(id=ID['channel']['member'])

    def choice_extension(self):
        list_text = ""
        numbers = ('one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten')
        extensions = fetch_extensions()
        for number, ext in zip(numbers, extensions):
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
    async def reload(self, ctx, *extensions: tuple):
        channel  = ctx.channel
        author   = ctx.author.id
        ext_list = []

        if not len(extensions):
            embed = self.choice_extension()
            await ctx.send(embed=embed)

            def check(m):
                return m.channel == channel and m.author.id == author
            num = await self.bot.wait_for('message', check=check)

            for number in num.content.split():
                if number == '0':
                    ext_list = fetch_extensions()
                    break
                elif number.isnumeric():
                    ext_list.append(fetch_extensions()[int(num.content) - 1])
        else:
            for extension in extensions:
                ext_list.append(extension)

        await self.load_extensions(ctx, self.bot.reload_extension, ext_list)

    @commands.command()
    @is_developer()
    async def load(self, ctx, *extensions: tuple):
        await self.load_extensions(ctx, self.bot.load_extension, extensions)

    @commands.command()
    @is_developer()
    async def unload(self, ctx, *extensions: tuple):
        await self.load_extensions(ctx, self.bot.unload_extension, extensions, 'アンロード')

    @commands.Cog.listener()
    async def on_member_join(self, new_member: object):
        if new_member.bot:
            return
        member_role = discord.utils.find(lambda role: role.name == 'member', new_member.guild.roles)
        member_num = new_member.guild.member_count

        if member_role is not None:
            await new_member.add_roles(member_role)
        await self.channel_member.send(
            f'{new_member.mention}Suwarikaサーバへようこそ\nあなたは{member_num}人目のメンバーです'
        )

    # eval
    @commands.command(name='eval_')
    @is_developer()
    async def evaluation(self, ctx, *, args: str):
        res = eval(args)
        await ctx.send(res)

    # exec
    @commands.command(name='exec_')
    @is_developer()
    async def execution(self, ctx, *, args: str):
        exec(args)

    # コマンドを別のユーザとして実行
    @commands.command(hidden=True)
    @is_developer()
    async def sudo(self, ctx, who: discord.User, *, command: str):
        channel = ctx.channel
        msg = copy.copy(ctx.message)
        msg.author = channel.guild.get_member(who.id) or who
        msg.channel = channel
        msg.content = ctx.prefix + command

        new_ctx = await self.bot.get_context(msg, cls=type(ctx))
        await self.bot.invoke(new_ctx)

def setup(bot):
    bot.add_cog(manage(bot))
