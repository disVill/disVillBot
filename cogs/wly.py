from   discord.ext import tasks, commands
from   discord     import Embed
import discord

import datetime

from   .config     import SiteUrls, GuildId

ID = GuildId.get_id()

class WlyBook:
    def __init__(self):
        self.wly_book_list = {
            '02/22': '02/23(日) 15:00-20:00',
        }

    def get_wly_book_list(self):
        return self.wly_book_list


class WorkLabYatsugatake(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.notice_loop.start()
        self.wly = WlyBook()
        self.wly_book_list = self.wly.get_wly_book_list()

    def book_list_embed(self):
        list_text = ""
        for _, day in self.wly_book_list.items():
            list_text += f"{day}\n"

        embed = Embed(
            title       = 'ワークラボの予約',
            description = list_text,
            color       = 0x00ffff,
        )
        return  embed

    @tasks.loop(hours=1)
    async def notice_loop(self):
        now = datetime.datetime.now().strftime('%m/%d/%H')

        for day, time in self.wly_book_list.items():
            if now == day + '/08':
                channel = self.bot.get_channel(id=ID['channel']['chat'])
                await channel.send(f'@everyone\n今日はワークラボの予約日です\n{time.split().pop(1)}')

    @commands.group()
    async def wly(self, ctx, *args):
        if ctx.invoked_subcommand is None:
            embed = self.book_list_embed()
            await ctx.send(embed = embed)

    @wly.group()
    async def site(self, ctx):
        await ctx.send(SiteUrls.url['wly'])


def setup(bot):
    bot.add_cog(WorkLabYatsugatake(bot))