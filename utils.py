"""共通ユーティリティ関数"""
import random
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO

from config import gdf


def get_random_message(message_list: list, correct_answer: str) -> str:
    """メッセージリストからランダムに選択し、{correct_answer}を置き換える"""
    message = random.choice(message_list)
    return message['quote'].format(correct_answer=correct_answer)


def generate_map_image(prefecture_name: str) -> BytesIO:
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
