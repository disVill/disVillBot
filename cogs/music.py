import asyncio
import random
import sys
import traceback
from collections import deque
from unicodedata import numeric

import discord
import googlesearch
import youtube_dl
from discord import Embed
from discord.ext import commands

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
is_enabled = True


class ExtendedQueue(asyncio.Queue):
    def __init__(self, maxsize=0, *, loop=None):
        super().__init__(maxsize, loop=loop)

    def clear(self):
        self._queue.clear()

    def _put_left(self, item):
        self._queue.appendleft(item)

    def put_left_nowait(self, item):
        if self.full():
            return
        self._put_left(item)
        self._unfinished_tasks += 1
        self._finished.clear()
        self._wakeup_next(self._getters)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, chID, url, *, data, volume=0.3):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')
        self.duration = data.get('duration')
        self.creator = data.get('creator')
        self.chID = chID
        self.url = url

    @classmethod
    async def from_url(cls, url, chID, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(source=filename, **ffmpeg_options), chID, url, data=data)


class music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice = None
        self.playing_music = ''
        self.play_next = asyncio.Event()
        self.songs = ExtendedQueue()
        self.is_repeat = False
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())

    def make_music_embed(self):
        embed = Embed(
            title='リピート中' if self.is_repeat else '再生中',
            color=0x00bfff,
            description=self.playing_music,
        )
        return embed

    def toggle_repeat(self):
        self.is_repeat = False if self.is_repeat else True

    async def add_react(self, msg: object) -> None:
        try:
            if self.voice.is_playing():
                [await msg.add_reaction(r) for r in ("⏸", "⏹", "🔄")]
            elif self.voice.is_paused():
                [await msg.add_reaction(r) for r in ("▶", "⏹", "🔄")]
        except discord.HTTPException: ...

    async def m_player(self, msg: object) -> None:
        def check(r: object, u: object) -> bool:
            if r.message.id == msg.id and not u.bot:
                return str(r.emoji) in ("▶", "⏹", "⏸", "🔄")

        await self.add_react(msg)

        while self.voice.is_playing() or self.voice.is_paused():
            try:
                react, _ = await self.bot.wait_for('reaction_add', check=check, timeout=10)
            except asyncio.TimeoutError:
                continue

            emoji = str(react.emoji)

            if emoji == "⏸" and not self.voice.is_paused():
                self.voice.pause()
            elif emoji == "▶" and self.voice.is_paused():
                self.voice.resume()
            elif emoji == "⏹":
                self.voice.stop()
                break
            elif emoji == "🔄":
                self.toggle_repeat()
                embed = self.make_music_embed()
                await msg.edit(embed=embed)

            await msg.clear_reactions()
            await self.add_react(msg)

        await msg.delete()

    async def repeat_song(self, url, channel_id):
        player = await YTDLSource.from_url(url, chID=channel_id, loop=self.bot.loop)
        try:
            self.songs.put_left_nowait(player)
        except Exception:
            traceback.print_exc()

    def toggle_next(self, error):
        self.bot.loop.call_soon_threadsafe(self.play_next.set)
        print('error check:', error)

    @commands.has_permissions(manage_messages=True)
    async def audio_player_task(self):
        while not self.bot.is_closed():
            self.play_next.clear()

            player = await self.songs.get()
            try:
                self.voice.play(player, after=self.toggle_next)
            except Exception:
                self.is_repeat = False
                print("In audio_player_task\n", traceback.format_exc())

            self.playing_music = player.title
            embed = self.make_music_embed()
            channel = self.bot.get_channel(id=player.chID)

            msg = await channel.send(embed=embed)
            try:
                await self.m_player(msg)
            except Exception:
                print("In music player", traceback.format_exc())

            if self.is_repeat:
                await self.repeat_song(player.url, player.chID)

            await self.play_next.wait()

    async def play_song(self, ctx, url, stream=False):
        if self.songs.qsize() >= 20:
            await ctx.send("追加できる曲数の上限に達しています")
            return

        if (self.voice is None) or (not self.voice.is_connected()):
            if ctx.author.voice is None:
                await ctx.send('ボイスチャンネルに接続してください')
                return
            await ctx.invoke(self.summon)

        if not (url.startswith("https://www.youtube.com/") and url.startswith('https://youtu.be/')):
            url = googlesearch.search(url, lang='jp', num=1, tpe='vid').__next__()

        try:
            player = await YTDLSource.from_url(url, chID=ctx.channel.id, loop=self.bot.loop)
        except Exception:
            await ctx.send("曲の再生に失敗しました")
            print(f'Failed to download music\n', traceback.format_exc())
            print('-' * 30)
            return

        if not self.songs.empty() or self.voice.is_playing() or self.voice.is_paused():
            embed = Embed(
                description=f"キューに追加: [{player.title}]({player.url})",
                color=0x00bfff,
            )
            await ctx.send(embed=embed)
        await self.songs.put(player)

    # YouTube-URLまたは曲名から曲を再生
    @commands.command(aliases=['p'], enabled=is_enabled)
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True)
    async def play(self, ctx, *, url):
        await self.play_song(ctx, url)

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True)
    async def stream(self, ctx, url: str):
        await self.play_song(ctx, url, stream=True)

    # ボイスチャンネルにBOTを接続する
    @commands.command(enabled=is_enabled)
    @commands.guild_only()
    async def summon(self, ctx):
        # herokuでデプロイするとき用
        # if not discord.opus.is_loaded():
        #     discord.opus.load_opus("heroku-buildpack-libopus")

        await ctx.send('ボイスチャンネルへ接続します')

        try:
            self.voice = await ctx.author.voice.channel.connect()
        except Exception:
            await ctx.send('ボイスチャンネルに接続できませんでした')
            print(f'Failed to connect voice channel', file=sys.stderr)
            traceback.print_exc()
            print('-----')

    # 曲の一時停止
    @commands.command(enabled=is_enabled)
    async def pause(self, ctx):
        if self.voice.is_playing():
            return self.voice.pause()
        await ctx.send('曲が再生されていません')

    # 曲の一時停止を解除
    @commands.command(enabled=is_enabled)
    async def resume(self, ctx):
        if self.voice.is_paused():
            return self.voice.resume()
        await ctx.send('一時停止されている曲はありません')

    # 再生されている曲の名前確認
    @commands.command(enabled=is_enabled)
    @commands.guild_only()
    async def playing(self, ctx):
        if self.voice.is_playing or self.voice.is_paused():
            embed = self.make_music_embed()
            return await ctx.send(embed=embed)
        await ctx.send('再生されている曲はありません')

    # キューに入っている曲の確認
    @commands.command(name='queue', aliases=['q'], enabled=is_enabled)
    @commands.guild_only()
    async def queue_(self, ctx):
        if self.voice is None:
            return

        song_list = ""
        for i, p in enumerate(self.songs._queue):
            song_list += f"{i + 2}) {p.title[:40].ljust(40)}  {p.duration // 60:3}:{p.duration % 60:02}\n"

        text = f"1) {self.playing_music[:40]}\n    ↑ Now {'repeat' if self.is_repeat else 'play'}ing\n"

        if not song_list:
            if self.voice.is_playing() or self.voice.is_paused():
                await ctx.send(f"```py\n{text}```")
            else:
                await ctx.send("```py\nキューに追加されている曲はありません```")
            return

        await ctx.send(f"```py\n{text}{song_list}```")

    # 曲の停止
    @commands.command(enabled=is_enabled)
    async def stop(self, ctx):
        if self.voice.is_playing():
            return self.voice.stop()
        await ctx.send('曲が再生されていません')

    @commands.command(enabled=is_enabled)
    @commands.guild_only()
    async def clear(self, ctx):
        self.songs.clear()
        await ctx.send("キューを空にしました")

    @commands.command(enabled=is_enabled)
    @commands.guild_only()
    async def repeat(self, ctx):
        self.toggle_repeat()
        await ctx.send("Repeat is {}enabled".format('' if self.is_repeat else 'dis'))

    # ボイスチャンネルからBOTを退出
    @commands.command(enabled=is_enabled)
    async def exit(self, ctx):
        await ctx.send('ボイスチャンネルから切断します')
        await self.voice.disconnect()
        self.voice = None

    @commands.command(hidden=True)
    @commands.is_owner()
    async def eval_m(self, ctx, *, form):
        try:
            text = eval(form)
        except Exception:
            await ctx.send(f"```py\n{traceback.format_exc()}```")
            return

        if text:
            await ctx.send(f"```py\n{text}```")
        else:
            await ctx.send('Done')

def setup(bot):
    bot.add_cog(music(bot))
