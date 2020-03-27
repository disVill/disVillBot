import discord
from discord import Embed
from discord.ext import commands
from googlesearch import search

from googletrans import Translator


class Google(commands.Cog):
    """google関係"""
    def __init__(self, bot):
        self.bot = bot

    # 引数に入ったキーワードをgoogleで検索
    @commands.command()
    async def google(self, ctx, *, keyword):
        url = search(keyword, lang='jp', num=1).__next__()
        await ctx.send(url)

    # 引数に入ったキーワードをgoogle翻訳で日本語へ翻訳する
    @commands.command(aliases=['googletrans', 'googleTrans', 'googletranslate', 'trans'])
    async def translate(self, ctx, *, text):
        dest = 'ja'
        translated = Translator().translate(text, dest=dest)
        await ctx.send(f"From: **{translated.src}**, To: **{dest}**\n{translated.text}")


def setup(bot):
    bot.add_cog(Google(bot))
