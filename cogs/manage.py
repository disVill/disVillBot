import asyncio
import copy
import sys

import discord
from discord import Embed
from discord.ext import commands

from cogs.config import GuildId

def is_developer():
    """コマンドの実行者が開発者か確認する"""
    async def predicate(ctx):
        if ctx.author.id == GuildId().id_list['user']['develop']:
            return True
        await ctx.send("実行する権限がありません")
    return commands.check(predicate)

class manage(commands.Cog):
    """discordサーバの管理系コマンド"""
    def __init__(self, bot):
        self.bot = bot

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

    # eval
    @commands.command(name='eval_')
    @is_developer()
    async def evaluate(self, ctx, *, args: str):
        res = eval(args)
        await ctx.send(res)

    # exec
    @commands.command(name='exec_')
    @is_developer()
    async def execute(self, ctx, *, args: str):
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
