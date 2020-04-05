import sys
import traceback
from datetime import datetime, timezone, timedelta

import discord
from discord.ext import commands

from cogs.config import GuildId

TOKEN, PREFIX = GuildId().get_token_and_prefix()
extension_list = GuildId().cog_list

class disVillBot(commands.Bot):
    def __init__(self, command_prefix):
        super().__init__(command_prefix, help_command=None)

    async def on_ready(self):
        print('-' * 30)
        print(self.user.name)
        print(self.user.id)
        print('-' * 30)

        for extension in extension_list:
            try:
                self.load_extension(extension)
            except:
                print(f'Failed to load extension: {extension}.', file=sys.stderr)
                traceback.print_exc()
                print('-' * 30)
            else:
                print(f'finished: {extension}')
                print('-' * 30)

        channel_id = GuildId().id_list['channel']['bot']
        channel = self.get_channel(id=channel_id)
        text = 'start-up at: {}'.format(datetime.now(timezone(timedelta(hours=9))))
        await channel.send(text)
        print(text)
        print('-' * 30)

        activity = discord.Activity(
            name='ご注文はうさぎですか？',
            type=discord.ActivityType.watching,
            )
        await self.change_presence(status=discord.Status.online, activity=activity)

if __name__ == '__main__':
    bot = disVillBot(command_prefix=PREFIX)
    bot.run(TOKEN)
