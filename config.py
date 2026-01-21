"""設定と共通データの読み込み"""
import json
import os
import geopandas as gpd
from dotenv import load_dotenv

load_dotenv()

# 環境変数
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
PORT = int(os.getenv('PORT', 8000))

if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN が .env ファイルに設定されていません")

# GeoJSONファイルから都道府県データを読み込む
gdf = gpd.read_file('json/prefectures.geojson')

# JSONデータの読み込み
def _load_json(filename: str) -> list:
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

collect_messages = _load_json('json/collect_messages.json')
faild_messages = _load_json('json/faild_messages.json')
invalid_messages = _load_json('json/invalid_messages.json')
clips = _load_json('json/clips.json')