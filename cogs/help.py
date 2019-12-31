from   discord.ext import commands
from   discord     import Embed
import discord


class BotHelp(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.page_count = 1
        self.min_page = 1
        self.max_page = 6
        self.display_num = 4

    def get_content_list(self):
        return {
            "!avatar ([user name])": "アバター画像を表示します. 名前を指定するとそのユーザの画像を表示します",
            "!echo *[message]": "メッセージのオウム返しをします",
            "!emoji *[Custom Emoji's name]": "BOTが指定したカスタム絵文字をリアクションします",
            "!google [keyword]": 'googleで検索します',
            "!janken [hand type]": "BOTとじゃんけんします",
            "!menber": "このサーバにいるメンバーの合計数を表示します",
            "!nether_gate [x] [z]  or  !ng [x] [z]": "minecraftのオープンワールド座標をネザーの座標に変換します",
            "!poll [question] *[choices]": "アンケートを作成します",
            "!poll_end  or  !pe": "投票を終了します (投票作成者のみ実行可能)",
            "~~!prime_factorization [number]  or  !pf [number]~~": "~~素因数分解します 0 ≤ number ≤ 65535~~ ",
            "!roles": "自分についている役職を確認します",
            "!time": "日本標準時間を表示します",
            "!timer [time]": "タイマーを設定します",
            "!wly": "ワークラボの予約時間を表示します",
            "~~!summon~~": "~~自分の入っているボイスチャンネルにBOTを呼び出します~~",
            "~~!play ([music name])~~": "~~曲のリストを表示します. 曲名を指定した場合はその曲を再生します.~~\n~~再生中の場合はプレイリストに追加します~~",
            "~~!pause~~": "~~曲を一時停止します~~",
            "~~!resume~~": "~~曲の再生を再開します~~",
            "~~!stop~~": "~~曲の再生を停止します. プレイリストに曲がある場合は次の曲を再生します~~",
            "~~!playlist~~": "~~プレイリストに登録されている曲を表示します~~",
            "~~!exit~~": "~~BOTを今いるボイスチャンネルから切断します~~",
        }

    def get_help_embed(self, page):
        commands_dic = self.get_content_list()

        embed = Embed(
            title=f'コマンド一覧 page{page}',
            color=0x00c0ff
        )
        i = 0
        cmd_block = self.display_num * (page -1)

        for command, text in commands_dic.items():
            if i >= cmd_block and i < cmd_block + self.display_num:
                embed.add_field(
                    name=command,
                    value=text,
                    inline=False,
                )
            i += 1
        return embed

    @commands.command()
    async def help(self, ctx):
        send_message = await ctx.send(embed=self.get_help_embed(1))
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
                return

            else:
                emoji = str(reaction.emoji)
                if emoji == "➡" and self.page_count < self.max_page:
                    self.page_count += 1
                if emoji == "⬅" and self.page_count > self.min_page:
                    self.page_count -= 1

                await send_message.clear_reactions() #事前に消去する
                await send_message.edit(embed=self.get_help_embed(self.page_count))

                try:
                    if self.page_count == self.min_page:
                        await send_message.add_reaction("➡")

                    elif self.page_count >= self.max_page:
                        await send_message.add_reaction("⬅")

                    else:
                        await send_message.add_reaction("⬅")
                        await send_message.add_reaction("➡")
                except KeyError:
                    pass

    @commands.command()
    async def what_is_new(self, ctx):
        embed = Embed(
            title='BOTの更新',
            description='・!timerコマンド, !emojiコマンドの追加\n・helpの内容更新\n・一部コマンドの無効化',
            color=0x00ffff,
        )
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(BotHelp(bot))