"""quizコマンド - 都道府県クイズ"""
import discord
import random

from config import gdf, collect_messages, faild_messages
from utils import get_random_message, generate_map_image

# クイズの状態を管理する辞書 {channel_id: 正解の都道府県名}
active_quizzes = {}


async def send_quiz(channel):
    """新しいクイズを出題"""
    correct_answer = random.choice(gdf['name'].tolist())
    active_quizzes[channel.id] = correct_answer
    image_buffer = generate_map_image(correct_answer)
    file = discord.File(fp=image_buffer, filename='quiz_map.png')
    await channel.send(
        f"🗾 **都道府県クイズ！**\n"
        f"赤く塗られた都道府県はどこでしょう？",
        file=file
    )


def setup(bot):
    @bot.tree.command(name="quiz", description="都道府県クイズを出題します（地図で表示）")
    async def quiz(interaction: discord.Interaction):
        await interaction.response.defer()
        await send_quiz(interaction.channel)
        await interaction.followup.send("クイズを開始しました！")

    @bot.event
    async def on_message(message):
        # Bot自身のメッセージは無視
        if message.author.bot:
            return

        # アクティブなクイズがないチャンネルは無視
        if message.channel.id not in active_quizzes:
            return

        user_answer = message.content.strip()
        prefecture_names = gdf['name'].tolist()

        # 都道府県名以外は無視
        if user_answer not in prefecture_names:
            return

        # クイズを取得して削除
        correct_answer = active_quizzes.pop(message.channel.id, None)
        if correct_answer is None:
            return

        if user_answer == correct_answer:
            # 正解 → 次の問題を出題
            reply_message = get_random_message(collect_messages, correct_answer)
            await message.reply(reply_message)
            await send_quiz(message.channel)
        else:
            # 不正解
            reply_message = get_random_message(faild_messages, correct_answer)
            await message.reply(reply_message)
            await send_quiz(message.channel)
