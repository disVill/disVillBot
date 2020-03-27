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

    async def add_react(self, msg: object) -> None:
        try:
            if self.voice.is_playing():
                [await msg.add_reaction(r) for r in ("⏸", "⏹")]
            elif self.voice.is_paused():
                [await msg.add_reaction(r) for r in ("▶", "⏹")]
        except discord.HTTPException: ...

    async def m_player(self, user_id: int, msg: object) -> None:
        await self.add_react(msg)

        def react_check(r: object, u: object) -> bool:
            if u.id != user_id or r.message.id != msg.id:
                return
            return str(r.emoji) in ("▶", "⏹", "⏸")

        while self.voice.is_playing() or self.voice.is_paused():
            try:
                reaction, _ = await self.bot.wait_for('reaction_add',check=react_check, timeout=30)
            except asyncio.TimeoutError: continue

            if (emoji := str(reaction.emoji)) == "⏸" and not self.voice.is_paused():
                self.voice.pause()
            elif emoji == "▶" and self.voice.is_paused():
                self.voice.resume()
            elif emoji == "⏹":
                self.voice.stop()
                break
            await msg.clear_reactions()

            await self.add_react(msg)

        await msg.clear_reactions()

    # 曲を再生するコマンド
    @commands.command(enabled=is_enabled)
    async def play(self, ctx, *, url):
        if (self.voice is None) or (not self.voice.is_connected()):
            if ctx.author.voice is None:
                return await ctx.send('ボイスチャンネルに接続してください')
            await ctx.invoke(self.summon)

        async with ctx.typing():
            if not url.startswith("https://www.youtube.com/watch?v="):
                url = googlesearch.search(url, lang='jp', num=1, tpe='vid').__next__()
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            self.voice.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        msg = await ctx.send('Now playing: {}'.format(player.title))
        self.playing_music = player.title
        await self.m_player(ctx.author.id, msg)

    # ボイスチャンネルにBOTを接続する
    @commands.command(enabled=is_enabled)
    async def summon(self, ctx):
        if not discord.opus.is_loaded():
            discord.opus.load_opus("heroku-buildpack-libopus")

        try:
            await ctx.send('ボイスチャンネルへ接続します')
            self.voice = await ctx.author.voice.channel.connect()
        except Exception as e:
            fmt = 'エラー ボイスチャンネルに接続しているか確認してください： ```py\n{}: {}\n```'
            await ctx.send(fmt.format(type(e).__name__, e))
            print(f'Failed to connect voic3 channel', file=sys.stderr)
            traceback.print_exc()
            print('-----')

    # 曲の一時停止
    @commands.command(enabled=is_enabled)
    async def pause(self, ctx):
        if self.voice.is_playing():
            self.voice.pause()
        else:
            await ctx.send('曲が再生されていません')

    # 曲の一時停止を解除
    @commands.command(enabled=is_enabled)
    async def resume(self, ctx):
        if self.voice.is_paused():
            self.voice.resume()
        else:
            await ctx.send('一時停止されている曲はありません')

    # 再生されている曲の名前確認
    @commands.command(enabled=is_enabled)
    async def playing(self, ctx):
        if self.voice.is_playing or self.voice.is_paused():
            await ctx.send(f"'{self.playing_music}' が再生されています")
        else:
            await ctx.send('再生されている曲はありません')

    # プレイリストの次の曲を再生
    @commands.command(enabled=is_enabled)
    async def stop(self, ctx):
        if self.voice.is_playing():
            self.voice.stop()
        else:
            await ctx.send('曲が再生されていません')

    # ボイスチャンネルからBOTを退出
    @commands.command(enabled=is_enabled)
    async def exit(self, ctx):
        await ctx.send('ボイスチャンネルから切断します')
        await self.voice.disconnect()
        self.voice = None

    # eval
    @commands.command(name='eval_m', enabled=is_enabled)
    @is_developer()
    async def evaluation_music(self, ctx, *args):
        x = eval(str(' '.join(args)))
        await ctx.send(x)

    # exec
    @commands.command(name='exec_m', enabled=is_enabled)
    @is_developer()
    async def execution_music(self, ctx, *args):
        exec(str(' '.join(args)))

def setup(bot):
    bot.add_cog(music(bot))
