from   discord     import Embed
from   discord.ext import commands
import discord

from   unicodedata import numeric
from   .config     import GuildId
import sys
import traceback

ID = GuildId.get_id()

def get_numbers():
    return ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']


class poll(commands.Cog):
    def __init__(self, bot):
        self.bot          = bot
        self.poll_channel = self.bot.get_channel(id=ID['channel']['poll'])
        self.voted        = []
        self.votes        = []

    # 投票用埋め込みメッセージ作成
    def get_poll(self, ctx, que, *args):
        choices = 0
        numbers = get_numbers()
        text    = ""

        # 選択肢を格納、数をカウント
        for number, arg in zip(numbers, args):
            text    += f":{number}:  {arg}\n"
            choices += 1

        # 埋め込みを生成
        embed = Embed(
            title       = f"**{que}**",
            description = text,
            color       = 0xffff00,
        )

        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)

        return embed, choices

    # 投票数のメッセージを作成
    def get_poll_value(self, args):
        num        = get_numbers()
        polls_text = ""

        for number, poll in zip(num, args):
            polls_text += f":{number}: : {poll} \t"

        return polls_text

    # メッセージのリスナ
    @commands.Cog.listener()
    async def on_message(self, msg):
        # メッセージが数字で投票チャンネルに送られた時の処理
        if msg.content.isnumeric() and msg.channel == self.poll_channel:
            # すでに投票した人の場合
            if msg.author.id in self.voted:
                await msg.channel.send(msg.author.mention + '  すでに投票しています')
            # 投票数をプラスして既投票者リストに格納
            else:
                try:
                    poll_number = int(numeric(msg.content))
                    self.votes[poll_number - 1] += 1

                    value = self.get_poll_value(self.votes)
                    await self.poll_msg.edit(content="投票数\n" + value)

                    self.voted.append(msg.author.id)

                except Exception as e:
                    fmt = '{} 投票に失敗しました'
                    await msg.channel.send(fmt.format(msg.author.mention))

                    print(f'Failed to poll', file=sys.stderr)
                    traceback.print_exc()
                    print('-----')

    # アンケート作成コマンド
    @commands.command()
    async def poll(self, ctx, que, *args):
        # 投票数と投票者リストの初期化
        self.votes, self.voted = [], []

        # 投票用メッセージ生成、送信
        (embed, choices) = self.get_poll(ctx, que, *args)
        self.poll_msg = await self.poll_channel.send(embed=embed)

        # 投票数リストに選択肢の数だけ０を生成
        for i in range(choices):
            self.votes.append(0)

        # 投票者のIDを保存
        self.poll_author = ctx.author.id

        # コマンドが送られたのが投票チャンネルではなかった時
        if ctx.channel.id != self.poll_channel.id:
            await ctx.send("アンケートチャンネルに \'" + que + "\' を作成しました")
            print(ctx.channel.id)

    # 投票締め切り
    @commands.command(aliases=['pe'])
    async def poll_end(self, ctx):

        # 投票作成者本人かどうか
        if ctx.author.id == self.poll_author:

            # 投票にかかわるリストなどを初期化
            self.poll_msg    = '0'
            self.poll_author = '0'
            self.votes       = []
            self.voted       = []

            mention          = ctx.author.mention
            await self.poll_channel.send(f'{mention} が投票を締め切りました')

        elif self.poll_msg != '0':
            await ctx.send('投票を開始した人しか締め切ることができません')

def setup(bot):
    bot.add_cog(poll(bot))