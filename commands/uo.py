"""uoコマンド"""
import discord


def setup(bot):
    @bot.tree.command(name="uo", description="うおwと言います")
    async def uo(interaction: discord.Interaction):
        await interaction.response.send_message("うぉw")
