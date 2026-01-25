"""コマンドモジュール"""
from .uo import setup as setup_uo
from .clip import setup as setup_clip
from .weekend import setup as setup_weekend
from .quiz import setup as setup_quiz
from .rate import setup as setup_rate


def setup_all(bot):
    """全てのコマンドをBotに登録"""
    setup_uo(bot)
    setup_clip(bot)
    setup_weekend(bot)
    setup_quiz(bot)
    setup_rate(bot)
