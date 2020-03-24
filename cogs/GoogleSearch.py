from discord.ext   import commands
from discord       import Embed
import discord

from googlesearch  import search
from googletrans import Translator


class Google(commands.Cog):
    """
    google関係
    """

    def __init__(self, bot):
        self.bot = bot

    # 引数に入れた単語をgoogleで検索
    @commands.group()
    async def google(self, ctx):
        if ctx.invoked_subcommand is None:
            keyword = ' '.join(ctx.message.content.split()[1:])
            print(f'google search log: {keyword}')

            url = search(keyword, lang='jp', num=1).__next__()
            await ctx.send(url)

    # google検索のヘルプ
    @google.group(name='--help')
    async def google_help(self, ctx):
        embed = Embed(
            title       = 'google search',
            description = '!google [serach keywords]',
            color       = 0x00ffff,
        )

        await ctx.send(embed=embed)

    @commands.command(aliases=['googletrans', 'googletranslate', 'trans'])
    async def translate(self, ctx, *, text):
        translator = Translator()
        dest = 'ja'
        translated = translator.translate(text, dest=dest)
        await ctx.send(f"From: **{translated.src}**, To: **{dest}**\n{translated.text}")


def setup(bot):
    bot.add_cog(Google(bot))