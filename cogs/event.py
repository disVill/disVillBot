from   discord.ext  import commands
from   discord      import Embed
import discord

import datetime
import sys
import traceback

from   .config      import GuildId

ID = GuildId.get_id()

class event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logs_channel = self.bot.get_channel(id=ID['channel']['logs'])

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot:
            return
        else:
            time_now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
            await self.logs_channel.send(f"**Send message**\n{msg.author}: {msg.channel}: {time_now}\n{msg.content}")

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
        print(error)

    @commands.Cog.listener()
    async def on_message_delate(self, m):
        if m.author.bot:
            return
        else:
            time_now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
            await self.logs_channel.send(f"**Delate message**\n{m.author}: {m.channel}: {time_now}\n{m.content}")

    @commands.Cog.listener()
    async def on_message_edit(self, b, a):
        if b.author.bot:
            return
        else:
            time_now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
            await self.logs_channel.send(f"**Edit message**\n{b.author}: {b.channel}: {time_now}\n{b.content}\nto\n{a.content}")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await self.logs_channel.send(f'**Removed menber**\n{member}')

def setup(bot):
    bot.add_cog(event(bot))
