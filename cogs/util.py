from   discord.ext import commands
from   discord     import Embed
import discord

import copy

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
    async def LUL(self, ctx):
        emoji = discord.utils.get(ctx.guild.emojis, name='LUL')
        if emoji:
            await ctx.add_reaction(emoji)


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

    @commands.command()
    async def prime_factorization(self, ctx, number: int = 758936553):
        text = ''

        while number % 2 == 0:
            text += '2 '
            number / 2

        for i in range(3, number, 2):
            while number % i == 0:
                text += f'{i} '
                number /= i

        # if i > 1: text += f'{i}'

        await ctx.send(text)


    @commands.command()
    async def echo(self, ctx):
        await ctx.send(ctx.message.content[6:])


def setup(bot):
    bot.add_cog(util(bot))