from fastapi import Request  # HTTPリクエスト1件を表すオブジェクト
from slowapi import Limiter  # slowapiはFastAPI用のレートリミットライブラリ


def rate_limit_key(request: Request) -> str:
    """誰のカウントとなるかを返す。認証機能実装前は1つの枠を共有"""
    # request.stateはリクエスト処理中に情報を格納できる。user_idを入れる。
    return getattr(request.state, "user_id", "pre-auth-shared")


# カウンタはプロセスメモリに保存するためコンテナ再起動で消える
limiter = Limiter(
    key_func=rate_limit_key,
    storage_uri="memory://",
    key_style="endpoint",
)
