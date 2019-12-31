from   discord.ext import commands
from   discord     import Embed
import discord

from   unicodedata import numeric
from   contextlib  import redirect_stdout
import asyncio
import copy
import io
import sys
import textwrap
import traceback

from   bot         import fetch_extensions
from   .PollSystem import get_numbers
from   .config     import GuildId

ID = GuildId.get_id()


def is_developer():
    async def predicate(ctx):
        if ctx.author.id == ID['user']['develop']:
            return True

        else:
            await ctx.send("実行する権限がありません")
            return False

    return commands.check(predicate)


class manage(commands.Cog):
    """discordサーバの管理系コマンド

    """

    def __init__(self, bot):
        self.bot = bot
        self.channel_member = self.bot.get_channel(id=ID['channel']['member'])
        self._last_result = None


    def choice_extension(self):
        list_text  = ""
        numbers    = get_numbers()
        extensions = fetch_extensions()

        for number, ext in zip(numbers, extensions):
            list_text += f":{number}: : {ext}\n"

        list_text += ":zero: All extension reload"

        embed = Embed(
            title='**Which extension would you reload?**',
            description=list_text,
            color=0x00ffff,)

        return embed


    async def reload_extensions(self, ctx, ext_list):
        await ctx.send('-' * 30)
        for ext_name in ext_list:
            try:
                self.bot.reload_extension(ext_name)

            except Exception as e:
                fmt = '読み込みに失敗しました： ```py\n{}: {}\n```'
                await ctx.send(fmt.format(type(e).__name__, e))
                await ctx.send('-' * 30)

                print(f'Failed to reload extension {ext_name}.', file=sys.stderr)
                traceback.print_exc()
                print('-' * 30)

            else:
                await ctx.send(f"reload extension '{ext_name}' with no errors")
                await ctx.send('-' * 30)

        await ctx.send('All finished')
        await ctx.send('-' * 30)

    def cleanup_code(self, content):
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    @commands.command()
    @is_developer()
    async def reload(self, ctx, *extensions):
        channel  = ctx.channel
        author   = ctx.author.id
        ext_list = []

        if len(extensions) == 0:
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

        await self.reload_extensions(ctx, ext_list)


    @commands.Cog.listener()
    async def on_member_join(self, new_member):
        if new_member.bot:
            return
        else:
            new_member_role = select_roll(new_member.guild.roles, name='member')
            member_num      = new_member.guild.member_count
            mention         = new_member.mention

            await new_member.add_roles(new_member_role)
            await self.channel_member.send(
                f'{mention}Suwarikaサーバへようこそ\nあなたは{member_num}人目のメンバーです'
            )


    # eval
    @commands.command(name='_eval')
    @is_developer()
    async def evaluation(self, ctx, *args):
        x = eval(str(' '.join(args)))
        await ctx.send(x)


    @commands.command(pass_context=True, hidden=True, name='eval')
    async def _eval(self, ctx, *, body: str):
        """Evaluates a code"""

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')

    # exec
    @commands.command(name='exec')
    @is_developer()
    async def execution(self, ctx, *args):
        exec(str(' '.join(args)))


    # コマンドを別のユーザとして実行
    @commands.command(hidden=True)
    @is_developer()
    async def sudo(self, ctx, who: discord.User, *, command: str):

        msg         = copy.copy(ctx.message)
        channel     = ctx.channel
        msg.channel = channel
        msg.author  = channel.guild.get_member(who.id) or who
        msg.content = ctx.prefix + command

        new_ctx     = await self.bot.get_context(msg, cls=type(ctx))

        await self.bot.invoke(new_ctx)


def setup(bot):
    bot.add_cog(manage(bot))