import os

BOT_TOKEN = ''
DAMMY_TOKEN = 'Th1s1SD4MmYT0kEnS0Y0uC4n.N0tUS3Th1sT0K3n.pL34s3us3yourT0ken' # 偽トークン
COMMAND_PREFIX = '!'

class SiteUrls:
    def __init__(self):
        self.github_url = "https://github.com/disVill/disVillBot"
        self.shinonome_twitter_url = "https://twitter.com/pgsus_info"
        self.wly_url = "https://wly.jp/"

    def get_shinonome_twitter_url(self):
        return self.shinonome_twitter_url

    def get_github_url(self):
        return self.github_url

    def get_wly_url(self):
        return self.wly_url

class GuildId:
    def __init__(self):
        self.token = BOT_TOKEN or os.environ.get('TOKEN')
        self.prefix = COMMAND_PREFIX or '!'
        self.id_list = {
            'user': {
                'develop' : 578507026943049728,
            },
            'channel': {
                'info'    : 626681636716675073,
                'member'  : 626402047251578880,
                'logs'    : 659252702890557450,
                'bot'     : 626401965315719178,
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
        self.keycap_list = (
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

    def get_id(self):
        return self.id_list

    def get_keycap(self):
        return self.keycap_list
