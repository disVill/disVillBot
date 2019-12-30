from   discord.ext import commands
from   discord     import Embed
import discord

from   .config     import SiteUrls


class WlyBook:
    def __init__(self):
        ...

    def get_wly_book():
        wly_book_list = [
            '01/05(日) 10:00-20:00',
            '01/08(水) 14:00-20:00',
            '01/12(日) 10:00-20:00',
        ]
        return wly_book_list


    def book_list_embed():
        list_text = ""

        # 予約リストをメッセージに入れる
        for day in WlyBook.get_wly_book():
            list_text += f"{day}\n"


        # できたオブジェクトから埋め込み生成
        embed = Embed(
            title       = 'ワークラボの予約',
            description = list_text,
            color       = 0x00ffff,
        )

        return  embed


class WorkLabYatsugatake(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def wly(self, ctx, *args):
        if ctx.invoked_subcommand is None:
            embed = WlyBook.book_list_embed()
            await ctx.send(embed = embed)

    @wly.group()
    async def site(self, ctx):
        await ctx.send(SiteUrls.url['wly'])


def setup(bot):
    bot.add_cog(WorkLabYatsugatake(bot))