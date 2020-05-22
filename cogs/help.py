import asyncio

import discord
from discord import Embed
from discord.ext import commands

class BotHelp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cmd_list = (
            ("avatar ([user name])", "アバター画像を表示します. 名前を指定するとそのユーザの画像を表示します"),
            ("echo [message]", "メッセージのオウム返しをします"),
            # ("cat", "入力を出力へコピーします"),
            ("emoji *[Custom-Emoji's name]", "BOTが指定したカスタム絵文字をリアクションします"),
            ("google *[keyword]", 'googleで検索します'),
            ("help ([command name])", "コマンドのリストを表示します。\n名前を指定するとそのコマンドを表示します"),
            ("janken [hand type]", "BOTとじゃんけんします"),
            ("member", "このサーバにいるメンバーの合計数を表示します"),
            ("ng [x] [z]", "minecraftのオープンワールド座標をネザーの座標に変換します"),
            ("latency", "Discord WebSocketプロトコル遅延を計測してミリ秒単位で表示します"),
            ("poll [question] *[choices]", "アンケートを作成します"),
            # ("pf [number]", "素因数分解します (1 < number ≤ 65535)"),
            ("roles", "自分についている役職を確認します"),
            ("time", "日本標準時間を表示します"),
            ("timer [time] ([label])", "タイマーを設定します\nラベルを入れると通知と一緒に表示します"),
            ("wly", "ワークラボの予約時間を表示します"),
            ("summon", "自分の入っているボイスチャンネルにBOTを呼び出します"),
            ("play [music name or YouTube URL]", "曲名かYouTubeのURLを指定するとその曲を再生します"),
            ("queue", "キューに登録されている曲を表示します"),
            ("pause", "曲を一時停止します"),
            ("playing", "再生中の曲名を表示します"),
            ("resume", "曲の再生を再開します"),
            ("stop", "曲の再生を停止します"),
            ("exit", "BOTを今いるボイスチャンネルから切断します"),
        )
        self.cmd_with_permission_list = (
            ("activity_init", "Botのアクティビティを初期化します"),
            ("activity [activity name]", "Botのアクティビティを変更します"),
            ("eval [python code]", "簡単なPythonのコードを実行します\n一部の組み込み関数のみ使用可能です"),
            ("eval_ [formula]", "式を評価して結果を返します"),
            ("exec_ [sentence]", "文を実行します"),
            ("load [cog name]", "指定したcogをロードします"),
            ("mkch [channel name]", "コマンドを送信したカテゴリーに新しいチャンネルを作成します"),
            ("name [channel name]", "コマンドを送信したチャンネルの名前を変更します"),
            ("reroad *([cog name])", "cogを再読み込みします"),
            ("restart", "Botを再起動します"),
            ("shutdown ([option)]", "Botをシャットダウンします"),
            ("sudo [user name] [command]", "コマンドを指定したユーザとして実行します"),
            ("topic [channel topic]", "コマンドを送信したチャンネルのトピックを変更します"),
            ("unload [cog name]", "指定したcogをアンロードします"),
        )

    def get_help_embed(self, page: int, per_page: int, cmd_list) -> object:
        embed = Embed(
            title=f'コマンド一覧 page {page}, {len(cmd_list)} commands',
            color=0x00c0ff
        )

        offset = per_page * (page - 1)
        for _, cmd in zip(range(per_page), cmd_list[offset:]):
            embed.add_field(name=cmd[0], value=cmd[1], inline=False)

        return embed

    async def add_react(self, msg: object, max_page: int, page: int = 1) -> None:
        try:
            if page == 1:
                return [await msg.add_reaction(r) for r in ("▶", "⏩")]
            if page >= max_page:
                return [await msg.add_reaction(r) for r in ("⏪", "◀")]
            [await msg.add_reaction(r) for r in ("⏪", "◀", "▶", "⏩")]
        except discord.HTTPException: ...

    async def send_cmd_li(self, ctx, cmd_list):
        per_page, page = 4, 1
        max_page = len(cmd_list) // per_page
        max_page += 1 if len(cmd_list) % per_page else 0
        msg = await ctx.send(embed=self.get_help_embed(page, per_page, cmd_list))
        if max_page <= 1:
            return
        await self.add_react(msg, max_page)

        def react_check(r: object, u: object) -> bool:
            if u.bot or r.message.id != msg.id:
                return
            return str(r.emoji) in ("⏪", "◀", "▶", "⏩") and u.id == ctx.author.id

        while not self.bot.is_closed():
            try:
                reaction, _ = await self.bot.wait_for('reaction_add',check=react_check, timeout=90)
            except asyncio.TimeoutError:
                return await msg.clear_reactions()

            emoji = str(reaction.emoji)
            if emoji  == "▶" and page < max_page:
                page += 1
            if emoji == "◀" and page > 1:
                page -= 1
            page = 1 if emoji == "⏪" else max_page if emoji == "⏩" else page

            await msg.clear_reactions()
            await msg.edit(embed=self.get_help_embed(page, per_page, cmd_list))

            await self.add_react(msg, max_page, page)

    def find_cmd_by_name(self, cmd_names: str) -> int:
        send_cmd_list = []
        for cmd in self.cmd_list + self.cmd_with_permission_list:
            if cmd_names in cmd[0]:
                send_cmd_list.append(cmd)

        return send_cmd_list

    async def send_cmd_help(self, ctx, name: str) -> None:
        cmd_list = self.find_cmd_by_name(name)
        if not cmd_list:
            return await ctx.send("コマンドが見つかりませんでした")
        await self.send_cmd_li(ctx, cmd_list)

    @commands.command()
    async def help(self, ctx, name: str=''):
        if not name:
            return await self.send_cmd_li(ctx, self.cmd_list)
        return await self.send_cmd_help(ctx, name)


def setup(bot):
    bot.add_cog(BotHelp(bot))
