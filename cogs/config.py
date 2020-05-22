import os

BOT_TOKEN = 'NjI2NDAzNzAxNDY0MTA0OTk2.XsSpOg.nQ0l2KbEwd3pfM7x65sPPBT-u34'
COMMAND_PREFIX = '?'
token_path = 'TOKEN'

class TokenNotFound(Exception):
    pass

class SiteUrls:
    def __init__(self):
        self._github_url = "https://github.com/disVill/disVillBot"
        self._shinonome_twitter_url = "https://twitter.com/pgsus_info"
        self._wly_url = "https://wly.jp/"

    @property
    def shinonome_twitter_url(self):
        return self._shinonome_twitter_url

    @property
    def github_url(self):
        return self._github_url

    @property
    def wly_url(self):
        return self._wly_url

class GuildId:
    def __init__(self):
        self.token = BOT_TOKEN or os.environ.get(token_path)
        self.prefix = COMMAND_PREFIX or '!'
        self._cog_list = (
            'cogs.manage',
            'cogs.util',
            'cogs.BotConfig',
            'cogs.PollSystem',
            'cogs.game',
            'cogs.music',
            'cogs.help',
            'cogs.GoogleSearch',
            'cogs.wly',
            'cogs.event',
            'cogs.classes',
        )
        self._keycap_list = (
            "1\N{combining enclosing keycap}",
            "2\N{combining enclosing keycap}",
            "3\N{combining enclosing keycap}",
            "4\N{combining enclosing keycap}",
            "5\N{combining enclosing keycap}",
            "6\N{combining enclosing keycap}",
            "7\N{combining enclosing keycap}",
            "8\N{combining enclosing keycap}",
            "9\N{combining enclosing keycap}",
            "\N{keycap ten}",
        )

    def get_token_and_prefix(self):
        if self.token is None:
            raise TokenNotFound
        return self.token, self.prefix

    @property
    def cog_list(self):
        return self._cog_list

    @property
    def keycap_list(self):
        return self._keycap_list
