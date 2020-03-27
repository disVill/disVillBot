import datetime

import discord
from discord import Embed
from discord.ext import commands, tasks

from cogs.config import GuildId, SiteUrls

config_instance = GuildId()
ID = config_instance.get_id()


class WlyBook:
    def __init__(self):
        self.wly_book_list = {
            # '00/00': '00/00() 00:00-00:00',
        }

    def get_wly_book_list(self):
        return self.wly_book_list or {'00/00': '予約はありません :timer:'}


class WorkLabYatsugatake(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.notice_loop.start()
        self.wly_instance = WlyBook()
        self.wly_book_list = self.wly_instance.get_wly_book_list()

    def book_list_embed(self):
        list_text = ""
        for _, day in self.wly_book_list.items():
            list_text += f"{day}\n"

        embed = Embed(
            title = 'ワークラボの予約',
            description = list_text,
            color = 0x00ffff,
        )
        return  embed

    @tasks.loop(hours=1)
    async def notice_loop(self):
        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime('%m/%d/%H')

        for day, time in self.wly_book_list.items():
            if now == day + '/08':
                channel = self.bot.get_channel(id=ID['channel']['chat'])
                await channel.send(f'@everyone\n今日はワークラボの予約日です\n{time.split().pop(1)}')

    @commands.command()
    async def wly(self, ctx, *args):
        if ctx.invoked_subcommand is None:
            embed = self.book_list_embed()
            await ctx.send(embed = embed)


def setup(bot):
    bot.add_cog(WorkLabYatsugatake(bot))
