import asyncio
import copy
import datetime
import io
import random
import re
import textwrap
import time
import traceback
from contextlib import redirect_stdout

import discord
from discord import Embed
from discord.ext import commands

from cogs.config import SiteUrls
from cogs.manage import is_developer

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
    async def member(self, ctx):
        arg  = ctx.guild.member_count
        text = f'このサーバーには{arg}人のメンバーがいます'
        await ctx.send(text)

    # change channel name
    @commands.command()
    @is_developer()
    async def name(self, ctx, *, channel_name: str):
        await ctx.channel.edit(name=channel_name)

    # change channel topic
    @commands.command()
    @is_developer()
    async def topic(self, ctx, *, channel_topic: str):
        await ctx.channel.edit(topic=channel_topic)

    # make new channel
    @commands.command()
    @is_developer()
    async def mkch(self, ctx, *, ch_name):
        category_id = ctx.channel.category_id
        category = ctx.guild.get_channel(category_id)
        await category.create_text_channel(name=ch_name)
        await ctx.send(f"新しいチャンネル'{ch_name}'を作りました")

    # react custom emoji
    @commands.command()
    async def emoji(self, ctx, *emoji_names: tuple):
        if not emoji_names:
            await ctx.send('Custom Emojiの名前を入力してください')

        for emoji_name in emoji_names:
            emoji = discord.utils.get(ctx.guild.emojis, name=emoji_name)
            if emoji:
                await ctx.message.add_reaction(emoji)

    @commands.command(aliases=['role'])
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
    async def timer(self, ctx, time, *msg):
        times = re.findall(r'\d+', time)
        units = re.findall(r'[h,m,s]', time)

        if len(times) != len(units):
            await ctx.send('時間指定の方法が誤っています')
            return

        seconds = 0
        text = ''

        if times and units:
            for t, u in zip(times, units):
                if u == 'h':
                    seconds += 3600 * int(t)
                elif u == 'm':
                    seconds += 60 * int(t)
                elif u == 's':
                    seconds += int(t)

        if seconds > 65535:
            return await ctx.send('時間が長すぎます')

        if seconds // 3600:
            text += f'{seconds//3600}時間'
        if seconds % 3600 // 60:
            text += f'{seconds%3600//60}分'
        if seconds % 3600 % 60:
            text += f'{seconds%3600%60}秒'

        await ctx.send(f'タイマーを{text}に設定しました:timer:')
        await asyncio.sleep(seconds)

        fin_txt = f"{ctx.author.mention} {' '.join(msg) if msg else f'{text}が経過しました'}:timer:"
        await ctx.send(fin_txt)

    @commands.command()
    async def time(self, ctx):
        time_now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
        await ctx.send(time_now)

    @commands.command()
    async def echo(self, ctx):
        await ctx.send(ctx.message.content[6:])

    @commands.command()
    async def ping(self, ctx):
        await ctx.send('pong')

    @commands.command(aliases=['latency'])
    async def latency_(self, ctx):
        await ctx.send(f'{int(self.bot.latency * 1000)}[ms]')

    @commands.command(aliases=['git', 'source', 'code', 'sourcecode'])
    async def github(self, ctx):
        await ctx.send(SiteUrls().get_github_url())

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
            # HACK: too long
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
