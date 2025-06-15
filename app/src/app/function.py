import os
from app.handler import SlackHandler

# 環境変数からトークン取得
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]

# Slack アプリ初期化
slack_handler = SlackHandler(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET
)


# Lambda ハンドラー関数
def lambda_handler(event, context):
    print(f"Received event: {event}, context: {context}")
    return slack_handler.handle(event, context)
