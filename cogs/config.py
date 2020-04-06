import os

BOT_TOKEN = ''
DAMMY_TOKEN = 'Th1s1SD4MmYT0kEnS0Y0uC4n.N0tUS3Th1sT0K3n.pL34s3us3yourT0ken' # 偽トークン
COMMAND_PREFIX = ''

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
        self.token = BOT_TOKEN or os.environ.get('TOKEN')
        self.prefix = COMMAND_PREFIX or '!'
        self._id_list = {
            'user': {
                'develop' : 578507026943049728,
            },
            'channel': {
                'info'    : 626681636716675073,
                'member'  : 626402047251578880,
                'bot'     : 626401965315719178,
                'bot2'    : 647656077424590849,
                'chat'    : 626401720607703053,
                'poll'    : 627093469722181642,
                'python'  : 627472625504878612,
                'js'      : 627472675962617856,
                'kotlin'  : 628843541577072650,
                'java'    : 663411580565848094,
                'voice'   : 626401720607703057,
                'login'   : 626401965315719178,
            },
            'category': {
                'guild'   : 626628017543970817,
                'common'  : 626401720607703051,
                'voice'   : 626401720607703055,
                'program' : 627472578642051072,
            },
            'guild': {
                'suwarika': 626401720053792768,
            },
        }
        self._cog_list = (
            'cogs.manage',
            'cogs.util',
            'cogs.BotConfig',
            'cogs.PollSystem',
            'cogs.game',
            # 'cogs.music',
            'cogs.help',
            'cogs.GoogleSearch',
            'cogs.wly',
            'cogs.event',
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
        if self.token is None or len(self.token) != 59:
            return DAMMY_TOKEN, self.prefix
        return self.token, self.prefix

    @property
    def id_list(self):
        return self._id_list

    @property
    def cog_list(self):
        return self._cog_list

    @property
    def keycap_list(self):
        return self._keycap_list
