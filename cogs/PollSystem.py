from   discord     import Embed
from   discord.ext import commands
import discord

from   unicodedata import numeric
from   .config     import GuildId
import asyncio
import sys
import traceback

config_instance = GuildId()
ID = config_instance.get_id()
KEYCAP = ("1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟")
NUMBERS = ('one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'keycap_ten')

class PollEmbed(object):
    def __init__(self, bot, embed, author, que, choices):
        self.bot = bot
        self.choices = choices
        self.embed = embed.copy()
        self.colour = ('yellow', 'green', 'purple', 'brown', 'red', 'blue', 'orange', 'white_large', 'black_large')
        self.poll_author_id = author.id
        self.que = que
        self.votes = self.voted = []
        self.votes = [0 for i in range(len(choices))]

    @classmethod
    def mk_poll_embed(cls, bot, author, que, choices):
        embed = Embed(title = que, color = 0xffff00)

        for number, choice in zip(NUMBERS, choices):
            embed.add_field(name=f":{number}:  {choice}\n", value=f"0 votes: 0%", inline=False)
        embed.set_author(name=author.name, icon_url=author.avatar_url)

        return cls(bot, embed, author, que, choices)

    def edit_embed(self, most_voter=False):
        self.embed.clear_fields()
        i = 0
        max_votes = max(self.votes)
        for number, choice, col in zip(NUMBERS, self.choices, self.colour):
            v_cnt = self.votes[i]
            v_pnt = int(v_cnt / sum(self.votes) * 100)

            value = f"{v_cnt} votes: {v_pnt}% \n" + f":{col}_square:" * (v_pnt // 10)
            if most_voter and v_cnt >= max_votes:
                value += ":white_flower:"
            self.embed.add_field(name=f":{number}: {choice}\n", value=value, inline=False)
            i += 1

        return self.embed

    async def wait_poll(self, msg):
        [await msg.add_reaction(r) for r in KEYCAP[:len(self.votes)]]
        await msg.add_reaction("🔚")

        def react_check(reaction, user):
            if reaction.message.id != msg.id or user.bot:
                return
            if (emoji := str(reaction.emoji)) in KEYCAP or emoji == "🔚":
                return True

        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add',check=react_check)
                await msg.clear_reactions()
            except asyncio.TimeoutError:
                continue

            if (emoji := str(reaction.emoji)) == "🔚" and self.poll_author_id == user.id:
                await msg.edit(embed=self.edit_embed(most_voter=True))
                break
            if not user.id in self.voted:
                self.voted.append(user.id)
                self.votes[KEYCAP.index(emoji)] += 1
                await msg.edit(embed=self.edit_embed())

            try:
                [await msg.add_reaction(r) for r in KEYCAP[:len(self.votes)]]
                await msg.add_reaction("🔚")
            except KeyError:
                pass

        await msg.clear_reactions()
        self.embed.title += ": 投票終了"
        await msg.edit(embed=self.embed)


class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.poll_channel = self.bot.get_channel(id=ID['channel']['poll'])
        self.poll_list = []

    # アンケート作成コマンド
    @commands.command()
    async def poll(self, ctx, que, *choices):
        if len(choices) > 10:
            await ctx.send("選択肢が多すぎます")
            return
        poll_cls = PollEmbed.mk_poll_embed(self.bot, ctx.author, que, choices)
        poll_msg = await self.poll_channel.send(embed=poll_cls.embed)
        if ctx.channel.id != self.poll_channel.id:
            await ctx.send("アンケートチャンネルに \'" + que + "\' を作成しました")

        await poll_cls.wait_poll(poll_msg)

def setup(bot):
    bot.add_cog(Poll(bot))