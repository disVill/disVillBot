import datetime
import sys
import traceback

import discord
from discord import Embed
from discord.ext import commands

from cogs.config import GuildId

ID = GuildId().id_list

class event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_member = self.bot.get_channel(id=ID['channel']['member'])

    # エラーが起きたら通知
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.author.send('このコマンドはDMで使用できません')

        elif isinstance(error, commands.DisabledCommand):
            await ctx.send('このコマンドは現在無効になっています')

        elif isinstance(error, commands.CommandNotFound):
            await ctx.send(f'コマンド {ctx.message.content.split()[0]} は存在しません')

        elif isinstance(error, commands.CommandInvokeError):
            original = error.original
            if not isinstance(original, discord.HTTPException):
                print(f'In {ctx.command.qualified_name}:', file=sys.stderr)
                traceback.print_tb(original.__traceback__)
                print(f'{original.__class__.__name__}: {original}', file=sys.stderr)
            await ctx.send('コマンドの実行に失敗しました')

        elif isinstance(error, commands.ArgumentParsingError):
            await ctx.send(error)

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('コマンドの引数が足りません')

        elif isinstance(error, commands.UserInputError):
            await ctx.send('入力されたコマンドに誤りがあります')

        print(f'Failed to invoke command', file=sys.stderr)
        traceback.print_exc()
        print('-' * 30)

    # 新しいユーザが入ってきたら通知
    @commands.Cog.listener()
    async def on_member_join(self, new_member):
        if new_member.bot:
            return
        member_role = discord.utils.find(lambda role: role.name == 'member', new_member.guild.roles)
        member_num = new_member.guild.member_count

        if member_role is not None:
            await new_member.add_roles(member_role)
        await self.channel_member.send(
            f'{new_member.mention}Suwarikaサーバへようこそ\nあなたは{member_num}人目のメンバーです'
        )

    @commands.Cog.listener()
    async def on_message(self, msg): ...

    @commands.Cog.listener()
    async def on_message_delate(self, msg): ...

    @commands.Cog.listener()
    async def on_message_edit(self, before, after): ...

    @commands.Cog.listener()
    async def on_member_remove(self, member): ...


def setup(bot):
    bot.add_cog(event(bot))
