from discord import Embed
from discord.ext import commands
import discord

from .config import GuildId
import asyncio

config_instance = GuildId()
ID = config_instance.get_id()
KEYCAP = ("1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣")
NUMBERS = ('one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine')
COLORS = ('yellow', 'green', 'purple', 'brown', 'red', 'blue', 'orange', 'white_large', 'black_large')


class PollEmbed(object):
    def __init__(self, bot: object, embed: object, author_id: int, choices: list):
        self.bot = bot
        self.choices = choices
        self.embed = embed.copy()
        self.poll_author_id = author_id
        self.voted = []
        self.votes = [0 for i in range(len(choices))]

    @classmethod
    def mk_poll_embed(cls, bot: object, author: object, que: str, choices: list) -> classmethod:
        embed = Embed(title=que, color=0xffff00)

        for number, choice in zip(NUMBERS, choices):
            embed.add_field(name=f":{number}:  {choice}\n", value=f"0 votes: 0%", inline=False)
        embed.set_author(name=author.name, icon_url=author.avatar_url)

        return cls(bot, embed, author.id, choices)

    def edit_embed(self, most_voter: bool=False) -> object:
        self.embed.clear_fields()
        i = 0
        max_votes = max(self.votes)
        for number, choice, col in zip(NUMBERS, self.choices, COLORS):
            v_cnt = self.votes[i]
            v_pnt = int(v_cnt / sum(self.votes) * 100)

            value = f"{v_cnt} votes: {v_pnt}% \n" + f":{col}_square:" * (v_pnt // 10)
            if most_voter and v_cnt >= max_votes:
                value += ":white_flower:"
            self.embed.add_field(name=f":{number}: {choice}\n", value=value, inline=False)
            i += 1

        return self.embed

    async def add_react(self, msg: object) -> None:
        try:
            [await msg.add_reaction(r) for r in KEYCAP[:len(self.votes)]]
            await msg.add_reaction("🔚")
        except KeyError: ...

    async def wait_poll(self, msg: object) -> None:
        await self.add_react(msg)

        def react_check(r: object, u: object) -> bool:
            if r.message.id != msg.id or u.bot:
                return False
            return str(r.emoji) in KEYCAP or emoji == "🔚"

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

            await self.add_react(msg)

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
    async def poll(self, ctx, que: str, *choices):
        if len(choices) > 9:
            await ctx.send("選択肢が多すぎます")
            return
        poll_cls = PollEmbed.mk_poll_embed(self.bot, ctx.author, que, choices)
        poll_msg = await self.poll_channel.send(embed=poll_cls.embed)

        if ctx.channel.id != self.poll_channel.id:
            c = self.bot.get_channel(self.poll_channel.id)
            await ctx.send(f"{c.mention} に {que} を作成しました")

        await poll_cls.wait_poll(poll_msg)

def setup(bot):
    bot.add_cog(Poll(bot))