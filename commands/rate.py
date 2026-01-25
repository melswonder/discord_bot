"""rateコマンド - 正答率表示"""
import discord

from database import get_ranking


def setup(bot):
    @bot.tree.command(name="rate", description="クイズの正答率ランキングを表示します")
    async def rate(interaction: discord.Interaction):
        await interaction.response.defer()

        # ランキングを取得
        ranking = get_ranking(10)

        if ranking:
            ranking_text = "**正答率ランキング** \n"
            for i, row in enumerate(ranking, 1):
                medal = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else f"{i}."
                ranking_text += (
                    f"{medal} {row['username']}: "
                    f"{row['correct_count']}/{row['total_count']} "
                    f"({row['rate']}%)\n"
                )
        else:
            ranking_text = "**正答率ランキング**\nまだデータがありません"

        await interaction.followup.send(ranking_text)
