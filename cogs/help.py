from   discord.ext import commands
from   discord     import Embed
import discord


class BotHelp(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def get_content_list(self):
        return {
            "!avatar ([user name])": "アバター画像を表示します. 名前を指定するとそのユーザの画像を表示します",
            "!echo": "メッセージのオウム返しをします",
            "!google [keyword]": 'googleで検索します',
            "!janken [hand type]": "BOTとじゃんけんします",
            "!menber": "このサーバにいるメンバーの合計数を表示します",
            "!nether_gate": "minecraftのオープンワールド座標をネザーの座標に変換します",
            "!poll [question] *[choices]": "アンケートを作成します",
            "!poll_end": "投票を終了します (投票作成者のみ実行可能)",
            "!prime_factorization [number]": "素因数分解します",
            "!roles": "自分についている役職を確認します",
            "!time": "日本標準時間を表示します",
            "!wly": "ワークラボの予約時間を表示します",
            "!summon": "自分の入っているボイスチャンネルにBOTを呼び出します",
            "!play ([music name])": "曲のリストを表示します. 曲名を指定した場合はその曲を再生します.\n再生中の場合はプレイリストに追加します",
            "!pause": "曲を一時停止します",
            "!resume": "曲の再生を再開します",
            "!stop": "曲の再生を停止します. プレイリストに曲がある場合は次の曲を再生します",
            "!playlist": "プレイリストに登録されている曲を表示します",
            "!exit": "BOTを今いるボイスチャンネルから切断します",
        }

    def get_help_embed(self, page):
        commands_dic = self.get_content_list()
        embed = Embed(
            title=f'コマンド一覧 page{page+1}',
            color=0x00c0ff
        )
        i = 0
        for command, text in commands_dic.items():
            if i >= 4*page and i < 4*page+4:
                embed.add_field(
                    name=command,
                    value=text,
                    inline=False,
                )
            i += 1
        return embed


    @commands.command()
    async def help(self, ctx):
        page_count = 0 #ヘルプの現在表示しているページ数
        page_content_list = ["このBOTのコマンド一覧です。\n➡を押すと次のページへ",
            """**google**：　googleで検索します 　例!google 近くの本屋
**nether_gate [x] [z]**：　minecraftのオープンワールド座標をネザーの座標に変換します
**poll [question] *[Choices]**：　アンケートを作成します
**poll_end**：　投票を終了します 投票を作った人のみ終了できます
**graph *[options]**：　グラフを作成します 　例!graph liner 0 10 -2
**member**：　このサーバにいるメンバーの合計数を表示します
**avatar ([user name])：　
**info**：　この一覧を表示します""",
            """DDLCのサウンドトラック再生機能の使い方
:one:　ボイスチャンネルに入り !summon を送信するとBOTが接続します
:two:　!play を送信
:three:　出てきた曲の一覧から任意の番号を選択
※　"!play music_name"　のように曲を直接指定することも可能""",
            """音楽再生中使用できるコマンド一覧
**summon**：　BOTをボイスチャンネルへ接続
**pause**：　曲の一時停止
**resume**：　曲を再び再生
**stop**：　曲の再生を終了
**playing**：　再生中の曲の曲名を表示
**exit**：　BOTをボイスチャンネルから切断""",
            ] #ヘルプの各ページ内容

        send_message = await ctx.send(embed=self.get_help_embed(0)) #最初のページ投稿
        await send_message.add_reaction("➡")

        def help_react_check(reaction,user):
            '''
            ヘルプに対する、ヘルプリクエスト者本人からのリアクションかをチェックする
            '''
            emoji = str(reaction.emoji)
            if reaction.message.id != send_message.id:
                return 0
            if emoji == "➡" or emoji == "⬅":
                if user != ctx.author:
                    return 0
                else:
                    return 1

        while not self.bot.is_closed():
            try:
                reaction, user = await self.bot.wait_for('reaction_add',check=help_react_check, timeout=180)
            except:
                await send_message.clear_reactions()
                return #時間制限が来たら、それ以降は処理しない
            else:
                emoji = str(reaction.emoji)
                if emoji == "➡" and page_count < 5:
                    page_count += 1
                if emoji == "⬅" and page_count > 0:
                    page_count -= 1

                await send_message.clear_reactions() #事前に消去する
                await send_message.edit(embed=self.get_help_embed(page_count))
                try:
                    if page_count == 0:
                        await send_message.add_reaction("➡")
                    elif page_count >= 5:
                        await send_message.add_reaction("⬅")
                    else:
                        await send_message.add_reaction("⬅")
                        await send_message.add_reaction("➡")
                except KeyError:
                    pass

    @commands.command(hidden=True)
    async def last_update(self, ctx):
        embed = Embed(
            title=''
        )

def setup(bot):
    bot.add_cog(BotHelp(bot))