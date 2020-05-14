import asyncio
import copy
import io
import random
import re
import textwrap
import time
import traceback
from datetime import datetime, timezone, timedelta
from contextlib import redirect_stdout

import discord
from discord import Embed
from discord.ext import commands

from cogs.config import SiteUrls

class util(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None

    def cleanup_code(self, content: str) -> str:
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        return content.strip('` \n')

    # show avatar
    @commands.command()
    async def avatar(self, ctx, *, who: discord.User = None):
        user = ctx.channel.guild.get_member(who.id) if who else ctx.author
        embed = Embed(
            description = f'[{user.name}]({user.avatar_url})',
            color = 0xffff00,
        )
        embed.set_image(url=user.avatar_url)

        await ctx.send(embed=embed)

    # count member
    @commands.command()
    @commands.guild_only()
    async def member(self, ctx):
        arg  = ctx.guild.member_count
        text = f'このサーバーには{arg}人のメンバーがいます'
        await ctx.send(text)

    # react custom emoji
    @commands.command()
    @commands.guild_only()
    async def emoji(self, ctx, *emoji_names: str):
        if not emoji_names:
            await ctx.send('Custom Emojiの名前を入力してください')

        for emoji_name in emoji_names:
            emoji = discord.utils.get(ctx.guild.emojis, name=emoji_name)
            if emoji:
                await ctx.message.add_reaction(emoji)

    @commands.command(aliases=['role'])
    @commands.guild_only()
    async def roles(self, ctx):
        roles = [r.name for r in ctx.author.roles]
        await ctx.send(' '.join(roles[1:]))

    @commands.command(aliases=['pf'], enabled=False)
    async def prime_factorization(self, ctx, number: int):
        if number is None or number > 65535 or number < 0:
            return await ctx.send('無効な数字です')
        await ctx.send(f'{number}を素因数分解します')
        text = ' '

        while number % 2 == 0:
            text += '2 '
            number / 2

        for i in range(3, number, 2):
            while number % i == 0:
                text += f'{i} '
                number /= i

        if i > 1: text += f'{i}'

        await ctx.send(text)

    @commands.command()
    async def timer(self, ctx, time, *, msg=''):
        times = re.findall(r'\d+', time)
        units = re.findall(r'[h,m,s]', time)

        if len(times) != len(units):
            return await ctx.send('時間指定の方法が誤っています')

        sec = 0
        for t, u in zip(times, units):
            if u == 'h':
                sec += 3600 * int(t)
            elif u == 'm':
                sec += 60 * int(t)
            elif u == 's':
                sec += int(t)

        if sec > 65535:
            return await ctx.send('時間が長すぎます')

        m, s = divmod(sec, 60)
        h, m = divmod(m, 60)
        text = f'{h}時間{m:2}分{s:2}秒'

        await ctx.send(f'タイマーを{text}に設定しました:timer:')
        await asyncio.sleep(sec)

        fin_txt = f"{ctx.author.mention} {msg if msg else f'{text}が経過しました'}:timer:"
        await ctx.send(fin_txt)

    @commands.command()
    async def cat(self, ctx, *option):
        while True:
            def check(m):
                return m.author.id == ctx.author.id
            try:
                msg = await self.bot.wait_for("message", check=check, timeout=60)
            except asyncio.TimeoutError:
                break

            await ctx.send(msg.content)

    @commands.command()
    async def seq(self, ctx, *, option):
        ...

    @commands.command()
    async def time(self, ctx):
        time_now = datetime.now(timezone(timedelta(hours=9)))
        await ctx.send(time_now)

    @commands.command()
    async def echo(self, ctx, *, txt):
        await ctx.send(txt)

    @commands.command()
    async def ping(self, ctx):
        await ctx.send('pong')

    @commands.command(name='latency')
    async def latency_(self, ctx):
        await ctx.send(f'{int(self.bot.latency * 1000)}[ms]')

    @commands.command(aliases=['git', 'source', 'code', 'sourcecode'])
    async def github(self, ctx):
        await ctx.send(SiteUrls().github_url)

    @commands.has_permissions(administrator=True)
    @commands.command(pass_context=True, name='eval')
    async def eval_(self, ctx, *, body: str):
        env = {
            # 'ctx': ctx,
            # 'channel': ctx.channel,
            # 'author': ctx.author,
            # 'guild': ctx.guild,
            # 'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            # HACK: 見ろ、コードがゴミのようだ
            exec(to_compile, {'__builtins__':{
                'print':print,'abs':abs,'bool':bool,'dict':dict,'dir':dir,'divmod':divmod,'format':format,'enumarate':enumerate,
                'float':float,'getattr':getattr,'hasattr':hasattr,'hex':hex,'int':int,'input':input,'len':len,'list':list,'map':map,
                'max':max,'min':min,'pow':pow,'random':random,'range':range,'reversed':reversed,'round':round,'set':set,'setattr':setattr,
                'slice':slice,'sorted':sorted,'str':str,'sum':sum,'time':time,'tuple':tuple,'type':type,'zip':zip,'_':self._last_result}}, env)
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


def setup(bot):
    bot.add_cog(util(bot))
