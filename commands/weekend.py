"""weekendコマンド - 週末投票"""
import discord
from datetime import timedelta


def setup(bot):
    @bot.tree.command(name="weekend", description="週末の参加可能な時間帯を投票します")
    async def weekend(interaction: discord.Interaction):
        """土曜午前/午後、日曜午前/午後の投票を作成"""
        poll = discord.Poll(
            question="週末の参加可能時間を教えてください",
            duration=timedelta(days=7),
            multiple=True
        )
        poll.add_answer(text="土曜午前")
        poll.add_answer(text="土曜午後")
        poll.add_answer(text="日曜午前")
        poll.add_answer(text="日曜午後")

        await interaction.response.send_message(poll=poll)
