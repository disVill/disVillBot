from   discord.ext import commands
from   discord     import Embed
import discord

import asyncio
import copy
import datetime
import re
import time

from .manage       import is_developer


class util(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def avatar(self, ctx, who: discord.User = None):
        if ctx.invoked_subcommand is None:
            msg         = copy.copy(ctx.message)
            channel     = ctx.channel
            msg.channel = channel

            msg.author  = ctx.author if who is None else channel.guild.get_member(who.id)
            msg.content = ctx.prefix + "__avatar__"

            new_ctx     = await self.bot.get_context(msg, cls=type(ctx))

            await self.bot.invoke(new_ctx)

    @avatar.group(name='--help')
    async def avatar_help(self, ctx):
        embed = Embed(
            title       = 'avatar command',
            description = '!avatar ([user_name])',
            color       = 0x00ffff,
        )
        await ctx.send(embed=embed)

    @commands.command(hidden=True)
    async def __avatar__(self, ctx):
        embed = Embed(
            description = f'[{ctx.author.name}]({ctx.author.avatar_url})',
            color = 0xffff00,
        )

        embed.set_image(url=ctx.author.avatar_url)

        await ctx.send(embed=embed)

    @commands.command()
    async def member(self, ctx):
        arg  = ctx.guild.member_count
        text = f'このサーバーには{arg}人のメンバーがいます'
        await ctx.send(text)

    @commands.command()
    @is_developer()
    async def name(self, ctx, channel_name):
        await ctx.channel.edit(name=channel_name)

    @commands.command()
    @is_developer()
    async def topic(self, ctx, channel_topic):
        await ctx.channel.edit(topic=channel_topic)

    @commands.command()
    async def emoji(self, ctx, *emoji_names):
        if not emoji_names:
            await ctx.send('Custom Emojiの名前を入力してください')

        for emoji_name in emoji_names:
            emoji = discord.utils.get(ctx.guild.emojis, name=emoji_name)
            if emoji:
                await ctx.message.add_reaction(emoji)

    @commands.command()
    @is_developer()
    async def make_ch(self, ctx, arg):
        category_id = ctx.channel.category_id
        category    = ctx.guild.get_channel(category_id)
        await category.create_text_channel(name=arg)
        await ctx.send(f"新しいチャンネル'{arg}'を作りました")

    @commands.command(aliases=['role'])
    async def roles(self, ctx):
        roles = [x.name for x in ctx.author.roles]
        await ctx.send(' '.join(roles[1:]))

    @commands.command(aliases=['pf'], enabled=False)
    async def prime_factorization(self, ctx, number: int):
        if number is None or number > 65535 or number < 0:
            await ctx.send('無効な数字です')
            return
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
    async def timer(self, ctx, *args):
        times = re.findall(r'\d+', ctx.message.content)
        units = re.findall(r'[h,m,s]', ctx.message.content[6:])

        if len(times) != len(units) or not len(args):
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

        if times > 65535:
            await ctx.send('時間が長すぎます')
            return

        if seconds // 3600:
            text += f'{seconds//3600}時間'
        if seconds % 3600 // 60:
            text += f'{seconds%3600//60}分'
        if seconds % 3600 % 60:
            text += f'{seconds%3600%60}秒'

        await ctx.send(f'タイマーを{text}に設定しました:timer:')
        # await asyncio.sleep(seconds)
        await ctx.send(f'{ctx.author.mention} {text}が経過しました:timer:')

    @commands.command()
    async def time(self, ctx):
        time_now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
        await ctx.send(time_now)

    @commands.command()
    async def echo(self, ctx):
        await ctx.send(ctx.message.content[6:])


def setup(bot):
    bot.add_cog(util(bot))