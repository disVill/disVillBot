from   discord.ext import commands
from   discord     import Embed
from   discord     import FFmpegPCMAudio as FFmpeg
import discord

import asyncio
import random
import sys
import traceback
from   unicodedata import numeric

from   .manage     import is_developer

# ffmpeg.exeのパスを指定する
# bot.pyと同じディレクトリにある時はいらない
# ffmpeg_path = r"C:\your\path\ffmpeg.exe"


# ドキドキ文芸部のサントラ 曲名
def music_list():
    return [
        'Doki Doki Literature Club!',
        'Ohayou Sayori!',
        'Dreams Of Love and Literature',
        'Okay, Everyone!',
        'Play With Me',
        'Poem Panic!',
        'Daijoubu!',
        'My Feelings',
        'My Confession',
        'Sayo-nara',
        'Just Monika.',
        'I Still Love You',
        'Your Reality (Credits)',
        'Poems Are Forever (Bonus Track)',
        'Doki Doki (Bonus Track)',
    ]


class music(commands.Cog):
    """mp3の音楽再生機能
    """

    def __init__(self, bot):
        self.bot          = bot
        self.voice        = None
        self.play_next    = asyncio.Event()
        self.songs        = asyncio.Queue()
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())


    # 曲リストから埋め込みメッセージ作成
    def music_list_embed(self):
        list_text = ""
        choices   = 1

        # 曲リストをメッセージに入れる
        for name in music_list():
            list_text += f"**{choices}**:   {name}\n"
            choices   += 1

        list_text += '\n**0**:   ランダムに曲を再生'

        # できたオブジェクトから埋め込み生成
        embed = Embed(
            title       = '**再生する曲の番号を選択してください**',
            description = list_text,
            color       = 0x00ffff,
        )

        return embed


    def toggle_next(self, error):
        self.bot.loop.call_soon_threadsafe(self.play_next.set)
        print('error check:' + error)


    # songsキューに入れた曲リストを一つづつ取り出して再生
    async def audio_player_task(self):
        while True:
            self.play_next.clear()
            self.playing_music = await self.songs.get()
            self.path = f"DDLC/{self.playing_music}.mp3"

            self.voice.play(FFmpeg(source=self.path), after=self.toggle_next)
            # ffmpeg_pathを指定したときは下の引数をFFmpeg()へ追加する
            # executable=ffmpeg_path

            await self.play_next.wait()


    # ボイスチャンネルにBOTを接続する
    @commands.command(enabled=False)
    async def summon(self, ctx):
        if not discord.opus.is_loaded():
            discord.opus.load_opus("heroku-buildpack-libopus")

        try:
            await ctx.send('ボイスチャンネルへ接続します')
            self.voice = await ctx.author.voice.channel.connect()

        except Exception as e:
            fmt = 'エラー　ボイスチャンネルに接続しているか確認してください： ```py\n{}: {}\n```'
            await ctx.send(fmt.format(type(e).__name__, e))
            print(f'Failed to connect voic3 channel', file=sys.stderr)
            traceback.print_exc()
            print('-----')
            return


    # 曲を再生するコマンド
    @commands.command(enabled=False)
    async def play(self, ctx, *music_name):
        author  = ctx.author.id
        channel = ctx.channel

        # ボイスチャンネルに接続しているか確認
        if (self.voice is None) or (not self.voice.is_connected()):
            if ctx.author.voice is None:
                await ctx.send('ボイスチャンネルに接続してください')
                return
            else:
                await ctx.invoke(self.summon)

        # 曲名が指定されているか確認
        if len(music_name) == 0:

            # 指定されていないとき
            embed = self.music_list_embed()
            await ctx.send(embed=embed)

            # ユーザからの曲番号メッセージ待ちとチェック
            def check(m):
                return m.channel == channel and m.author.id == author
            num = await self.bot.wait_for('message', check=check)

            # 指定された曲を変数へ代入
            if num.content.isnumeric:
                if num.content == '0':
                    music_name = random.choice(music_list())
                else:
                    music_name = music_list()[int(num.content) - 1]

            else:
                music_name = ' '.join(num.content)

        else:
            # 引数の曲名をつなげてセットする
            music_name = ' '.join(music_name)

        # 曲を再生
        if self.voice.is_playing():
            await ctx.send(f"'{music_name}' プレイリストに追加しました")
        else:
            await ctx.send(f"'{music_name}' を再生します")

        await self.songs.put(music_name)


    # 曲の一時停止
    @commands.command(enabled=False)
    async def pause(self, ctx):
        if self.voice.is_playing():
            self.voice.pause()
        else:
            await ctx.send('曲が再生されていません')


    # 曲の一時停止を解除
    @commands.command(enabled=False)
    async def resume(self, ctx):
        if self.voice.is_paused():
            self.voice.resume()
        else:
            await ctx.send('一時停止されている曲はありません')


    # 再生されている曲の名前確認
    @commands.command(enabled=False)
    async def playing(self, ctx):
        if self.voice.is_playing:
            await ctx.send(f"'{self.playing_music}' が再生されています")
        else:
            await ctx.send('再生されている曲はありません')


    # プレイリストの次の曲を再生
    @commands.command(enabled=False)
    async def stop(self, ctx):
        if self.voice.is_playing():
            self.voice.stop()
        else:
            await ctx.send('曲が再生されていません')


    # プレイリストの曲の確認
    @commands.command(enabled=False)
    async def playlist(self, ctx):
        song_list = ''

        for name in self.songs._queue:
            song_list += f"'{name}'  "

        if song_list is None:
            await ctx.send('プレイリストに登録されている曲はありません')
        else:
            await ctx.send(song_list)


    # ボイスチャンネルからBOTを退出
    @commands.command(enabled=False)
    async def exit(self, ctx):
        await ctx.send('ボイスチャンネルから切断します')
        await self.voice.disconnect()


    # eval
    @commands.command(name='eval_m', enabled=False)
    @is_developer()
    async def evaluation_music(self, ctx, *args):
        x = eval(str(' '.join(args)))
        await ctx.send(x)


    # exec
    @commands.command(name='exec_m', enabled=False)
    @is_developer()
    async def execution_music(self, ctx, *args):
        exec(str(' '.join(args)))


def setup(bot):
    bot.add_cog(music(bot))