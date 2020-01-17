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
            embed = Embed(
                title = 'Send message',
                color = 0x98eb34,
                description=f'{msg.content}',
                timestamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
            )
            embed.set_author(name=msg.author, icon_url=msg.author.avatar_url)
            embed.set_footer(text=msg.channel.name, icon_url=msg.guild.icon_url)
            await self.logs_channel.send(embed=embed)

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
            embed = Embed(
                title = 'Edit message',
                color = 0x34abeb,
                timestamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
            )
            embed.add_field(name='before',value=b.content)
            embed.add_field(name='after',value=a.content)
            embed.set_author(name=a.author, icon_url=a.author.avatar_url)
            embed.set_footer(text=a.channel.name, icon_url=a.guild.icon_url)
            await self.logs_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await self.logs_channel.send(f'**Removed menber**\n{member}')

def setup(bot):
    bot.add_cog(event(bot))
