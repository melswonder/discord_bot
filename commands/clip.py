"""clipコマンド - 動画クリップをランダム送信"""
import discord
import random
import asyncio
import os
import tempfile

from config import clips


def setup(bot):
    @bot.tree.command(name="clip", description="イタリアンブレインロッド")
    async def clip(interaction: discord.Interaction):
        """brain.mp4からランダムなクリップを送信"""
        video_path = "mp4/brain.mp4"

        # ランダムにクリップを選択
        selected_clip = random.choice(clips)
        clip_name = selected_clip['name']
        starttime = selected_clip['starttime']
        duration = selected_clip['duration']

        await interaction.response.defer()

        try:
            if not os.path.exists(video_path):
                await interaction.followup.send("brain.mp4が見つかりません")
                return

            with tempfile.TemporaryDirectory() as tmpdir:
                output_path = f'{tmpdir}/clip.mp4'
                cmd = [
                    'ffmpeg', '-y',
                    '-ss', str(starttime),
                    '-i', video_path,
                    '-t', str(duration),
                    '-c:v', 'libx264',
                    '-c:a', 'aac',
                    '-preset', 'fast',
                    '-crf', '28',
                    output_path
                ]
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                try:
                    await asyncio.wait_for(process.communicate(), timeout=120)
                except asyncio.TimeoutError:
                    process.kill()
                    await interaction.followup.send("処理がタイムアウトしました")
                    return

                if process.returncode != 0:
                    await interaction.followup.send("動画の切り出しに失敗しました")
                    return

                file_size = os.path.getsize(output_path)
                if file_size > 8 * 1024 * 1024:
                    await interaction.followup.send("ファイルサイズが大きすぎます（8MB以上）")
                    return

                file = discord.File(output_path, filename="clip.mp4")
                await interaction.followup.send(f"{clip_name}", file=file)

        except Exception as e:
            await interaction.followup.send(f"エラーが発生しました: {str(e)}")
