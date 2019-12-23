from   discord.ext import commands
import discord

import random


class Game(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['ng'])
    async def nether_gate(ctx, x: int, z: int):
        x /= 8
        z /= 8
        await ctx.send(f'**x = {x}, z = {z}**')

    # じゃんけんゲーム
    # 勝ち負け判定
    def janken_game(self, ctx, hand):
        emoji  = ['fist', 'v', 'hand_splayed']
        h_type = ['rock', 'scissors', 'paper']
        cp     = random.randint(0, 2)

        if h_type.index(hand) == cp:
            return 'botの手 : :{}: 引き分け！'.format(emoji[cp])

        elif (h_type.index(hand) + 1) % 3 == cp:
            return 'botの手 : :{}: あなたの勝ち！'.format(emoji[cp])

        else:
            return 'botの手 : :{}: あなたの負け...'.format(emoji[cp])

    # じゃんけん鬼畜バージョン
    def j_game(self, _, hand):
        emoji  = ['fist', 'v', 'hand_splayed', 'fist']
        h_type = ['rock', 'scissors', 'paper', 'rock']
        result = random.randint(0, 99)

        if result < 45:
            cp = h_type.index(hand)
            return 'botの手 : :{}: 引き分け！'.format(emoji[cp])

        elif result < 90:
            cp = (h_type.index(hand) + 1) % 3
            return 'botの手 : :{}: あなたの負け...'.format(emoji[cp])

        else:
            cp = h_type.index(hand) + 1
            return 'botの手 : :{}: あなたの勝ち！'.format(emoji[cp])


    # 本体
    @commands.group()
    async def janken(self, ctx, hand):
        if hand not in ['rock', 'scissors', 'paper']:
            await ctx.send("引数に'rock, scissors, paper'のどれかを入れてね")
            return
        else:
            janken_message = self.janken_game(ctx, hand)
            await ctx.send(janken_message)


def setup(bot):
    bot.add_cog(Game(bot))