import datetime
import sys
import traceback

import discord
from discord import Embed
from discord.ext import commands

class event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # エラーが起きたら通知
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.author.send('このコマンドはDMで使用できません')

        elif isinstance(error, commands.DisabledCommand):
            await ctx.send('このコマンドは現在無効になっています')

        elif isinstance(error, commands.CommandNotFound):
            await ctx.send(f'コマンド {ctx.message.content.split()[0]} は存在しません')

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('コマンドの引数が足りません')

        elif isinstance(error, commands.TooManyArguments):
            await ctx.send('コマンドの引数が多すぎます')

        elif isinstance(error, commands.BadArgument):
            await ctx.send('コマンドの引数が正しいか確認してください')

        elif isinstance(error, commands.ArgumentParsingError):
            await ctx.send('クォーテーションが正しいか確認してください')

        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(
                f">>> コマンドを実行する権限が不足しています\n必要な権限: {', '.join(error.missing_perms)}"
            )

        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(f">>> BOTの権限が不足しています\n必要な権限: {', '.join(error.missing_perms)}")

        elif isinstance(error, commands.NotOwner):
            await ctx.send('BOT開発者専用のコマンドです')

        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send('コマンドの実行に失敗しました')

        elif isinstance(error, commands.CheckFailure):
            await ctx.send('コマンドの実行チェックでエラーが発生しました')

        elif isinstance(error, commands.ExtensionError):
            await ctx.send('cogでエラーが発生しました')

        elif isinstance(error, commands.UserInputError):
            await ctx.send('入力されたコマンドに誤りがあります')

        try:
            print(f'In {ctx.command.qualified_name}:', file=sys.stderr)
            original = error.original
            traceback.print_tb(original.__traceback__)
            print(f'{original.__class__.__name__}: {original}', file=sys.stderr)
        except AttributeError: ...

    # 新しいユーザが入ってきたら通知
    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        member_role = discord.utils.find(lambda role: role.name == 'member', guild.roles)

        if guild.system_channel is not None:
            to_send = '{0.mention}{1.name}へようこそ\nあなたは{1.member_count}人目のメンバーです'.format(member, guild)
            await guild.system_channel.send(to_send)

        if member_role is not None:
            try:
                await member.add_roles(member_role)
            except commands.BotMissingPermissions:
                pass

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
