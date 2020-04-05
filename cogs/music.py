import asyncio
import random
import sys
import traceback
from unicodedata import numeric

import discord
import googlesearch
import youtube_dl
from discord import Embed
from discord.ext import commands

from .manage import is_developer
from cogs.config import GuildId

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
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
is_enabled = True

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.3):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(source=filename, **ffmpeg_options), data=data)

class music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice = None
        self.playing_music = None
        self.play_next = asyncio.Event()
        self.songs = asyncio.Queue()
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())
        self.bot_ch_id = GuildId().id_list['channel']['bot2']

    async def add_react(self, msg: object) -> None:
        try:
            if self.voice.is_playing():
                [await msg.add_reaction(r) for r in ("⏸", "⏹")]
            elif self.voice.is_paused():
                [await msg.add_reaction(r) for r in ("▶", "⏹")]
        except discord.HTTPException: ...

    async def m_player(self, msg: object) -> None:
        def check(r: object, u: object) -> bool:
            if r.message.id == msg.id and not u.bot:
                return str(r.emoji) in ("▶", "⏹", "⏸")

        await self.add_react(msg)

        while self.voice.is_playing() or self.voice.is_paused():
            try:
                react, _ = await self.bot.wait_for('reaction_add',check=check, timeout=10)
            except asyncio.TimeoutError: continue

            if (emoji := str(react.emoji)) == "⏸" and not self.voice.is_paused():
                self.voice.pause()
            elif emoji == "▶" and self.voice.is_paused():
                self.voice.resume()
            elif emoji == "⏹":
                self.voice.stop()
                break

            await msg.clear_reactions()
            await self.add_react(msg)

        await msg.clear_reactions()

    def toggle_next(self, error):
        self.bot.loop.call_soon_threadsafe(self.play_next.set)
        print('error check:' + error)

    async def audio_player_task(self):
        while not self.bot.is_closed():
            self.play_next.clear()

            bot_ch = self.bot.get_channel(id=self.bot_ch_id)

            player = await self.songs.get()
            self.voice.play(player, after=self.toggle_next)
            self.playing_music = player.title

            embed = Embed(
                title="再生中",
                color=0x00bfff,
                description=f"{player.title}"
            )
            msg = await bot_ch.send(embed=embed)
            await self.m_player(msg)

            await self.play_next.wait()

    # YouTube-URLまたは曲名から曲を再生
    @commands.command(enabled=is_enabled)
    async def play(self, ctx, *, url: str):
        if (self.voice is None) or (not self.voice.is_connected()):
            if ctx.author.voice is None:
                return await ctx.send('ボイスチャンネルに接続してください')
            await ctx.invoke(self.summon)

        if not url.startswith("https://www.youtube.com/watch?v="):
            url = googlesearch.search(url, lang='jp', num=1, tpe='vid').__next__()

        player = await YTDLSource.from_url(url, loop=self.bot.loop)
        if player is None:
            return await ctx.send("曲のダウンロードに失敗しました")

        if not self.songs.empty() or self.voice.is_playing() or self.voice.is_paused():
            embed = Embed(
                description=f"キューに追加: {player.title}",
                color=0x00bfff,
            )
            await ctx.send(embed=embed)
        await self.songs.put(player)

    # ボイスチャンネルにBOTを接続する
    @commands.command(enabled=is_enabled)
    async def summon(self, ctx):
        if not discord.opus.is_loaded():
            discord.opus.load_opus("heroku-buildpack-libopus")

        try:
            await ctx.send('ボイスチャンネルへ接続します')
            self.voice = await ctx.author.voice.channel.connect()
        except Exception as e:
            fmt = 'ボイスチャンネルに接続しているか確認してください： ```py\n{}: {}\n```'
            await ctx.send(fmt.format(type(e).__name__, e))
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
    async def playing(self, ctx):
        if self.voice.is_playing or self.voice.is_paused():
            embed = Embed(
                title='再生中の曲',
                color=0x00bfff,
                description=f'{self.playing_music}'
            )
            return await ctx.send(embed=embed)
        await ctx.send('再生されている曲はありません')

    # キューに入っている曲の確認
    @commands.command(name='queue', enabled=is_enabled)
    async def queue_(self, ctx):
        song_list = ""
        for i, p in enumerate(self.songs._queue):
            song_list += f"{i + 1}) {p.title}\n"

        if not song_list:
            return await ctx.send("キューに追加されている曲はありません")

        await ctx.send("```py\n" + song_list + "```")

    # 曲の停止
    @commands.command(enabled=is_enabled)
    async def stop(self, ctx):
        if self.voice.is_playing():
            return self.voice.stop()
        await ctx.send('曲が再生されていません')

    # ボイスチャンネルからBOTを退出
    @commands.command(enabled=is_enabled)
    async def exit(self, ctx):
        await ctx.send('ボイスチャンネルから切断します')
        await self.voice.disconnect()
        self.voice = None


def setup(bot):
    bot.add_cog(music(bot))
