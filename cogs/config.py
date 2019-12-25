import os


class BotAuth:
    bot_token      = '' or os.environ.get('TOKEN')
    dammy_token    = 'Th1s1SD4MmYT0kEnS0Y0uC4n.N0tUS3Th1sT0K3n.pL34s3us3yourT0ken'
    command_prefix = '!'


class SiteUrls:
    url = {
        'wly': 'https://wly.jp/',
    }



class GuildId:
    def __init__(self):
        self.token  = BotAuth.bot_token
        self.prefix = BotAuth.command_prefix or '!'


    def get_token_and_prefix(self):
        if self.token is None or len(self.token) != 59:
            return os.environ.get('TOKEN'), self.prefix
        else:
            return self.token, self.prefix


    def get_id():
        return {
            'user': {
                'develop' : 578507026943049728,
            },
            'channel': {
                'chat'    : 626401720607703053,
                'login'   : 626401965315719178,
                'bot'     : 626401965315719178,
                'logs'    : 659252702890557450,
                'info'    : 626681636716675073,
                'poll'    : 627093469722181642,
                'member'  : 626402047251578880,
                'python'  : 627472625504878612,
                'js'      : 627472675962617856,
                'kotlin'  : 628843541577072650,
                'voice'   : 626401720607703057,
            },
            'category': {
                'guild'   : 626628017543970817,
                'common'  : 626401720607703051,
                'voice'   : 626401720607703055,
                'program' : 627472578642051072,
            },
            'guild': {
                'bot'     : 588305013072461844,
                'suwarika': 626401720053792768,
            },
        }


    def get_keycap():
        return (
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