"""quizコマンド - 都道府県クイズ"""
import discord
import random

from config import gdf, collect_messages, faild_messages, invalid_messages
from utils import get_random_message, generate_map_image

# クイズの状態を管理する辞書 {channel_id: 正解の都道府県名}
active_quizzes = {}


def setup(bot):
    @bot.tree.command(name="quiz", description="都道府県クイズを出題します（地図で表示）")
    async def quiz(interaction: discord.Interaction):
        await interaction.response.defer()

        # ランダムに都道府県を選択
        correct_answer = random.choice(gdf['name'].tolist())

        # チャンネルIDをキーにして正解を保存
        active_quizzes[interaction.channel_id] = correct_answer

        # 地図画像を生成
        image_buffer = generate_map_image(correct_answer)

        # Discordに画像を送信
        file = discord.File(fp=image_buffer, filename='quiz_map.png')
        await interaction.followup.send(
            f"🗾 **都道府県クイズ！**\n"
            f"赤く塗られた都道府県はどこでしょう？\n"
            f"チャットで都道府県名を入力してください（例：東京都）",
            file=file
        )

    @bot.event
    async def on_message(message):
        # Bot自身のメッセージは無視
        if message.author.bot:
            return

        # アクティブなクイズがないチャンネルは無視
        if message.channel.id not in active_quizzes:
            return

        correct_answer = active_quizzes[message.channel.id]
        user_answer = message.content.strip()

        if user_answer == correct_answer:
            # 正解の場合
            reply_message = get_random_message(collect_messages, correct_answer)
            await message.reply(reply_message)
            del active_quizzes[message.channel.id]
        elif user_answer in gdf['name'].tolist():
            # 都道府県名だが不正解の場合
            reply_message = get_random_message(faild_messages, correct_answer)
            await message.reply(reply_message)
            del active_quizzes[message.channel.id]
        else:
            # 無効な入力の場合
            reply_message = get_random_message(invalid_messages, correct_answer)
            await message.reply(reply_message)
            del active_quizzes[message.channel.id]
