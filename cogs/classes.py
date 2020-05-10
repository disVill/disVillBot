import json

import discord
from discord import Embed
from discord.ext import commands
from discord.ext import tasks

class SusClasses(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def search_class(self, name):
        return_dict = {}
        with open('cogs/class_data.json', encoding="utf-8") as f:
            json_load = json.load(f)

            for k, v in json_load.items():
                if name in k:
                    return_dict[k] = v

            return return_dict

    @commands.command(name='class')
    async def class_(self, ctx, name):
        class_dict = self.search_class(name.upper())
        if not class_dict:
            await ctx.send("> 授業が見つかりませんでした")
            return

        embed = Embed(
            title="検索結果",
            description=f"{len(class_dict)}件",
            color=0x008000,
        )

        fmt = "教員名　：`{}`\n曜日時限：`{}`\n授業番号：`{}`\n[SORA](https://sus.mrooms.net/course/view.php?id={})"

        for name, v in class_dict.items():
            embed.add_field(
                name=name,
                value=fmt.format(v['teacher'], v['day'], v['no'], v['id'])
            )

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(SusClasses(bot))