from   discord.ext import commands
from   discord     import Embed
import discord

import asyncio


class BotHelp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cmd_list = (
            ("!avatar ([user name])", "アバター画像を表示します. 名前を指定するとそのユーザの画像を表示します"),
            ("!echo *[message]", "メッセージのオウム返しをします"),
            ("!emoji *[Custom-Emoji's name]", "BOTが指定したカスタム絵文字をリアクションします"),
            ("!eval *[python code]", "簡単なPythonのコードを実行します\n一部の組み込み関数のみ使用可能です"),
            ("!google *[keyword]", 'googleで検索します'),
            ("!janken [hand type]", "BOTとじゃんけんします"),
            ("!menber", "このサーバにいるメンバーの合計数を表示します"),
            ("!nether_gate [x] [z]  or  !ng [x] [z]", "minecraftのオープンワールド座標をネザーの座標に変換します"),
            ("!latency", "Discord WebSocketプロトコル遅延を計測してミリ秒単位で表示します"),
            ("!poll [question] *[choices] lt 10", "アンケートを作成します"),
            ("~~!prime_factorization [number]  or  !pf [number]~~", "~~素因数分解します 0 ≤ number ≤ 65535~~ "),
            ("!roles", "自分についている役職を確認します"),
            ("!time", "日本標準時間を表示します"),
            ("!timer [time] *([label])", "タイマーを設定します\nラベルを入れると通知と一緒に表示します"),
            ("!wly", "ワークラボの予約時間を表示します"),
            ("!summon", "自分の入っているボイスチャンネルにBOTを呼び出します"),
            ("!play [music name or YouTube URL]", "曲名かYouTubeのURLを指定するとその曲を再生します"),
            ("!pause", "曲を一時停止します"),
            ("!playing", "再生中の曲名を表示します"),
            ("!resume", "曲の再生を再開します"),
            ("!stop", "曲の再生を停止します"),
            ("!exit", "BOTを今いるボイスチャンネルから切断します"),
        )

    def get_help_embed(self, page: int, per_page: int) -> object:
        embed = Embed(
            title=f'コマンド一覧 page {page}, {len(self.cmd_list)} commands',
            color=0x00c0ff
        )

        offset = per_page * (page - 1)
        for _, cmd in zip(range(per_page), self.cmd_list[offset:]):
            embed.add_field(name=cmd[0], value=cmd[1], inline=False)

        return embed

    async def add_react(self, msg: object, max_page: int, page: int = 1) -> None:
        try:
            if page == 1:
                [await msg.add_reaction(r) for r in ("▶", "⏩")]
            elif page >= max_page:
                [await msg.add_reaction(r) for r in ("⏪", "◀")]
            else:
                [await msg.add_reaction(r) for r in ("⏪", "◀", "▶", "⏩")]
        except KeyError: ...

    @commands.command()
    async def help(self, ctx, per_page: int = 4):
        page = 1
        msg = await ctx.send(embed=self.get_help_embed(page, per_page))
        max_page = len(self.cmd_list) // per_page + 1 if len(self.cmd_list) % per_page else 0
        await self.add_react(msg, max_page)

        def react_check(r: object, u: object) -> bool:
            if r.message.id != msg.id:
                return
            return str(r.emoji) in ("⏪", "◀", "▶", "⏩") and u == ctx.author

        while not self.bot.is_closed():
            try:
                reaction, _ = await self.bot.wait_for('reaction_add',check=react_check, timeout=180)
            except asyncio.TimeoutError:
                await msg.clear_reactions()
                return

            if (emoji := str(reaction.emoji)) == "▶" and page < max_page:
                page += 1
            if emoji == "◀" and page > 1:
                page -= 1
            page = 1 if emoji == "⏪" else max_page if emoji == "⏩" else page

            await msg.clear_reactions()
            await msg.edit(embed=self.get_help_embed(page, per_page))

            await self.add_react(msg, max_page, page)

    @commands.command(hideen=True)
    async def what_is_new(self, ctx):
        embed = Embed(
            description='BOTの更新 v1.2.8/nアンケート機能の仕様変更',
            color=0x00ffff,
        )
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(BotHelp(bot))