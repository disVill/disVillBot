import sys
import traceback

import discord
from discord.ext import commands

from cogs.config import GuildId

TOKEN, prefix = GuildId().get_token_and_prefix()

# cog list
def fetch_extensions():
    return (
        'cogs.manage',
        'cogs.GoogleSearch',
        'cogs.PollSystem',
        # 'cogs.graph',
        'cogs.game',
        'cogs.BotConfig',
        'cogs.music',
        'cogs.help',
        'cogs.util',
        'cogs.wly',
        'cogs.event',
    )

class disVillBot(commands.Bot):
    def __init__(self, command_prefix):
        super().__init__(command_prefix, help_command=None)

    async def on_ready(self):
        print('-----')
        print(self.user.name)
        print(self.user.id)
        print('-----')

        for extension in fetch_extensions():
            try:
                self.load_extension(extension)
            except Exception:
                print(f'Failed to load extension {extension}.', file=sys.stderr)
                traceback.print_exc()
                print('-----')
            else:
                print('finished (no error)')
                print('-----')

if __name__ == '__main__':
    bot = disVillBot(command_prefix=prefix)
    bot.run(TOKEN)
