import discord
from discord import app_commands
import random
import geopandas as gpd
import matplotlib
matplotlib.use('Agg')  # GUIなし環境でも動作するように設定
import matplotlib.pyplot as plt
from io import BytesIO
import json
from dotenv import load_dotenv
import os
from datetime import timedelta
import asyncio
import tempfile
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
load_dotenv()

# Koyebヘルスチェック用のシンプルなHTTPサーバー
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')

    def log_message(self, format, *args):
        pass  # ログを抑制

def start_health_server():
    port = int(os.getenv('PORT', 8000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# ヘルスチェックサーバーをバックグラウンドで起動
health_thread = threading.Thread(target=start_health_server, daemon=True)
health_thread.start()

# GeoJSONファイルから都道府県データを読み込む
gdf = gpd.read_file('prefectures.geojson')

# バリデーションメッセージを読み込む
with open('collect_messages.json', 'r', encoding='utf-8') as f:
    collect_messages = json.load(f)

with open('faild_messages.json', 'r', encoding='utf-8') as f:
    faild_messages = json.load(f)

with open('invalid_messages.json', 'r', encoding='utf-8') as f:
    invalid_messages = json.load(f)

# クリップデータを読み込む
with open('clips.json', 'r', encoding='utf-8') as f:
    clips = json.load(f)

# クイズの状態を管理する辞書 {channel_id: 正解の都道府県名}
active_quizzes = {}

def get_random_message(message_list, correct_answer):
    """メッセージリストからランダムに選択し、{correct_answer}を置き換える"""
    message = random.choice(message_list)
    return message['quote'].format(correct_answer=correct_answer)

def generate_map_image(prefecture_name):
    """指定された都道府県を塗りつぶした地図画像を生成"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))

    # 全ての都道府県を描画
    gdf.plot(ax=ax, color='lightgray', edgecolor='black', linewidth=0.5)

    # 指定された都道府県だけ赤く塗りつぶす
    selected = gdf[gdf['name'] == prefecture_name]
    selected.plot(ax=ax, color='#FF6B6B', edgecolor='black', linewidth=0.8)

    # 軸を非表示
    ax.axis('off')
    plt.tight_layout()

    # 画像をバイトストリームに保存
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)

    return buf

# Botの基本設定
class PrefectureBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # スラッシュコマンドをDiscordに同期
        await self.tree.sync()

bot = PrefectureBot()

@bot.event
async def on_ready():
    print(f'{bot.user} としてログインしました')
    print(f'{len(gdf)}個の都道府県データを読み込みました')

@bot.tree.command(name="uo", description="うおwと言います")
async def uo(interaction: discord.Interaction):
    await interaction.response.send_message("うぉw")

@bot.tree.command(name="clip", description="イタリアンブレインロッド")
async def clip(interaction: discord.Interaction):
    """brain.mp4からランダムなクリップを送信"""

    video_path = "brain.mp4"

    # ランダムにクリップを選択
    selected_clip = random.choice(clips)
    clip_name = selected_clip['name']
    starttime = selected_clip['starttime']
    duration = selected_clip['duration']

    await interaction.response.defer()

    try:
        # 動画ファイルの存在確認
        if not os.path.exists(video_path):
            await interaction.followup.send("brain.mp4が見つかりません")
            return

        with tempfile.TemporaryDirectory() as tmpdir:
            # ffmpegで切り出し
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
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=120)
            except asyncio.TimeoutError:
                process.kill()
                await interaction.followup.send("処理がタイムアウトしました")
                return

            if process.returncode != 0:
                await interaction.followup.send("動画の切り出しに失敗しました")
                return

            # ファイルサイズ確認（Discordの制限: 8MB、Nitroは50MB）
            file_size = os.path.getsize(output_path)
            if file_size > 8 * 1024 * 1024:
                await interaction.followup.send("ファイルサイズが大きすぎます（8MB以上）")
                return

            # Discordに送信
            file = discord.File(output_path, filename="clip.mp4")
            await interaction.followup.send(
                f"{clip_name}",
                file=file
            )

    except Exception as e:
        await interaction.followup.send(f"エラーが発生しました: {str(e)}")


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


@bot.tree.command(name="quiz", description="都道府県クイズを出題します（地図で表示）")
async def quiz(interaction: discord.Interaction):
    # Discordに「処理中」と伝える（画像生成に時間がかかるため）
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

    # デバッグ用
    print(f"メッセージ受信: {message.content} (チャンネルID: {message.channel.id})")
    print(f"アクティブなクイズ: {active_quizzes}")

    # このチャンネルでアクティブなクイズがあるか確認
    if message.channel.id in active_quizzes:
        correct_answer = active_quizzes[message.channel.id]
        user_answer = message.content.strip()

        print(f"正解: {correct_answer}, ユーザーの回答: {user_answer}")

        # ユーザーの回答と正解を比較
        if user_answer == correct_answer:
            # 正解の場合 - collect.jsonからランダムメッセージ
            reply_message = get_random_message(collect_messages, correct_answer)
            await message.reply(reply_message)
            # クイズを終了
            del active_quizzes[message.channel.id]
        elif user_answer in gdf['name'].tolist():
            # 都道府県名だが不正解の場合 - faild.jsonからランダムメッセージ
            reply_message = get_random_message(faild_messages, correct_answer)
            await message.reply(reply_message)
            del active_quizzes[message.channel.id]
        else:
            # 無効な入力の場合 - invalid.jsonからランダムメッセージ
            reply_message = get_random_message(invalid_messages, correct_answer)
            await message.reply(reply_message)
            del active_quizzes[message.channel.id]  
        
# Botトークンを環境変数から読み込む
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN が .env ファイルに設定されていません")

bot.run(DISCORD_TOKEN)
