import asyncio

import discord
from discord import Embed
from discord.ext import commands

KEYCAP = ("1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣")
COLORS = ('yellow', 'green', 'purple', 'brown', 'red', 'blue', 'orange', 'white_large', 'black_large')


class PollEmbed(object):
    def __init__(self, bot: object, embed: object, author_id: int, choices: tuple):
        self.bot = bot
        self.choices = choices
        self.embed = embed.copy()
        self.poll_author_id = author_id
        self.voted = []
        self.votes = [0 for i in range(len(choices))]

    @classmethod
    def mk_poll_embed(cls, bot: object, author: object, que: str, choices: tuple) -> classmethod:
        embed = Embed(title=que, color=0xffff00)

        for keycap, choice in zip(KEYCAP, choices):
            embed.add_field(name=f"{keycap}  {choice}\n", value=f"0 votes: 0%", inline=False)
        embed.set_author(name=author.name, icon_url=author.avatar_url)

        return cls(bot, embed, author.id, choices)

    def edit_embed(self, most_voter: bool=False) -> object:
        self.embed.clear_fields()
        max_votes = max(self.votes)

        for v_cnt, keycap, choice, col in zip(self.votes, KEYCAP, self.choices, COLORS):
            v_sum = sum(self.votes) or 1
            v_pnt = int(v_cnt / v_sum * 100)
            value = f"{v_cnt} votes: {v_pnt}% \n" + f":{col}_square:" * (v_pnt // 10)
            if most_voter and v_cnt >= max_votes:
                value += ":white_flower:"
            self.embed.add_field(name=f"{keycap}: {choice}\n", value=value, inline=False)

        return self.embed

    async def add_react(self, msg: object) -> None:
        try:
            [await msg.add_reaction(r) for r in KEYCAP[:len(self.votes)]]
            await msg.add_reaction("🔚")
        except discord.HTTPException: ...

    async def wait_poll(self, msg: object) -> None:
        await self.add_react(msg)

        def react_check(r: object, u: object) -> bool:
            if r.message.id == msg.id or not u.bot:
                return (emoji := str(r.emoji)) in KEYCAP or emoji == "🔚"

        while not self.bot.is_closed():
            reaction, user = await self.bot.wait_for('reaction_add',check=react_check)
            await msg.clear_reactions()

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

    # アンケート作成コマンド
    @commands.command()
    async def poll(self, ctx, que: str, *choices: str):
        if len(choices) > 9:
            return await ctx.send("選択肢が多すぎます")
        poll_cls = PollEmbed.mk_poll_embed(self.bot, ctx.author, que, choices)
        poll_msg = await ctx.send(embed=poll_cls.embed)

        await poll_cls.wait_poll(poll_msg)

def setup(bot):
    bot.add_cog(Poll(bot))
