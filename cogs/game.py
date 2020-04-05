import random

import discord
from discord.ext import commands

class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['ng'])
    async def nether_gate(self, ctx, x: int, z: int):
        x /= 8
        z /= 8
        await ctx.send(f'x = {x}, z = {z}')

    def janken_game(self, hand: str) -> str:
        emoji = ('fist', 'v', 'hand_splayed')
        h_type = ('rock', 'scissors', 'paper')
        cp = random.randint(0, 2)

        if h_type.index(hand) == cp:
            return 'botの手 : :{}: 引き分け！'.format(emoji[cp])
        if (h_type.index(hand) + 1) % 3 == cp:
            return 'botの手 : :{}: あなたの勝ち！'.format(emoji[cp])
        return 'botの手 : :{}: あなたの負け...'.format(emoji[cp])

    # janken game command
    @commands.command()
    async def janken(self, ctx, *hand):
        if hand not in ('rock', 'scissors', 'paper'):
            return await ctx.send("引数に'rock, scissors, paper'のどれかを入れてね")

        result_msg = self.janken_game(hand)
        await ctx.send(result_msg)


def setup(bot):
    bot.add_cog(Game(bot))
