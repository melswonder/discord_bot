"""Discord Bot メインエントリーポイント"""
import discord
from discord import app_commands

from config import DISCORD_TOKEN, gdf
from health import start_health_server
from commands import setup_all
from database import init_db


class PrefectureBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()


bot = PrefectureBot()

# 全コマンドを登録
setup_all(bot)


@bot.event
async def on_ready():
    print(f'{bot.user} としてログインしました')
    print(f'{len(gdf)}個の都道府県データを読み込みました')


if __name__ == '__main__':
    # データベースを初期化
    init_db()
    # ヘルスチェックサーバーを起動
    start_health_server()
    # Botを起動
    bot.run(DISCORD_TOKEN)
