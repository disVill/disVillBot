from   discord.ext import commands
import discord

import matplotlib.pyplot as plt
import numpy             as np
import math

from .manage       import is_developer


class MakeGraph(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.group()
    async def graph(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("引数が足りません")


    @graph.command()
    async def show(self, ctx):
        await ctx.send(file=discord.File('figure.png'))


    @graph.command(name='-liner')
    async def liner(self, ctx, begin: float, end: float, Inclination: float = 1):
        x = np.arange(begin, end, 0.001)
        y = x * Inclination
        plt.plot(x,y)
        plt.xlabel('X-axis')
        plt.ylabel('Y-axis')
        plt.grid()
        plt.savefig('figure.png')
        await ctx.send(file=discord.File('figure.png'))
        plt.figure()


    @graph.command()
    @commands.has_permissions(administrator=True)
    async def _exec(self, ctx, *args):
        exec(str(' '.join(args)))
        plt.savefig('figure.png')
        await ctx.send(file=discord.File('figure.png'))
        plt.figure()


    @graph.group(name='--help')
    async def graph_help(self, ctx):
        embed = Embed(
            title       = 'graph command help',
            description = '!graph [liner] [begin] [end] [inclination]',
            color       = 0x00ffff,
        )

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(MakeGraph(bot))
