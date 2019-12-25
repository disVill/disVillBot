from   discord.ext  import commands
from   discord      import Embed
import discord

from   .config      import GuildId

class event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logs_channel = self.bot.get_channel(id=ID['channel']['logs'])

    @commands.Cog.listener()
    async def on_message(self, msg):
        await ctx.send(f"{}")