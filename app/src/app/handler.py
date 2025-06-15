from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler


class SlackHandler:
    def __init__(self, token, signing_secret):
        app = App(token=token, signing_secret=signing_secret)
        self.app = register_event_listeners(app)
        self.slack_request_handler = SlackRequestHandler(app=app)

    def handle(self, event, context):
        """
        Lambda ハンドラー関数。
        Slack イベントを処理するためのエントリポイント。
        """
        print(f"Received event: {event}, context: {context}")
        return self.slack_request_handler.handle(event, context)


def _parse_text(text: str) -> str:
    """
    テキストを解析して、必要な情報を抽出する関数。
    ここでは単純にテキストをそのまま返す。
    """
    # ここに解析ロジックを追加
    return text.strip() if text else "No text provided"


def _modal_view(user_id) -> dict:
    """
    モーダルのビューを定義する関数。
    """
    return {
                "type": "modal",
                "callback_id": "form_submission",
                "title": {"type": "plain_text", "text": "情報入力"},
                "submit": {"type": "plain_text", "text": "送信"},
                "close": {"type": "plain_text", "text": "キャンセル"},
                "private_metadata": user_id,
                "blocks": [
                    {
                        "type": "input",
                        "block_id": "input_block",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "input_value"
                        },
                        "label": {"type": "plain_text", "text": "情報を入力してください"}
                    }
                ],
            }


def register_event_listeners(app: App):
    """
    Slack アプリのイベントリスナーを登録する関数
    """
    # イベントリスナーの登録
    app.command("/echo")(repeat_text)
    app.command("/sample-form")(handle_command)
    app.shortcut("sample-form")(handle_shortcut)
    app.view("form_submission")(handle_submission)
    app.event("app_home_opened")(handle_app_home_opened)
    app.action("sample_form_button")(handle_sample_form_button)

    return app


# /echo コマンドのイベントリスナー
def repeat_text(ack, respond, command):
    print("Received command payload:", command)
    respond(f"{command['text']}")
    ack()


# /sample-form コマンドのイベントリスナー
def handle_command(payload, ack, client):
    print("Received command payload:", payload)

    trigger_id = payload["trigger_id"]

    # モーダル表示
    client.views_open(
        trigger_id=trigger_id,
        view=_modal_view(user_id=payload["user"]["id"])
    )
    ack()


# ショートカットコマンドのイベントリスナー
def handle_shortcut(payload, ack, client):
    print("Received command payload:", payload)

    trigger_id = payload["trigger_id"]

    # モーダル表示
    client.views_open(
        trigger_id=trigger_id,
        view=_modal_view(user_id=payload["user"]["id"])
    )
    ack()


# モーダル送信イベントリスナー
def handle_submission(payload, ack, client):
    print("Received view submission payload:", payload)
    submitted = payload["state"]["values"]["input_block"]["input_value"]

    user_id = payload["private_metadata"]
    if user_id:
        # dm を送る
        client.chat_postMessage(
            channel=user_id,
            text=f"あなたが入力した情報: *{submitted['value']}*"
        )

    # 処理が内容を表示
    ack(
        response_action="update",
        view={
            "type": "modal",
            "callback_id": "form_submission",
            "title": {"type": "plain_text", "text": "情報入力"},
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"あなたが入力した情報: *{submitted['value']}*"
                    }
                }
            ],
            "close": {"type": "plain_text", "text": "閉じる"},
        }
    )


# app home イベントリスナー
def handle_app_home_opened(ack, event, client):
    print("Received app home opened event:", event)
    # app home のボタンを表示
    client.views_publish(
        user_id=event["user"],
        view={
            "type": "home",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Welcome to the App Home!*"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Open Form"},
                            "action_id": "sample_form_button"
                        }
                    ]
                }
            ]
        }
    )
    ack()


# app home ボタンのイベントリスナー
def handle_sample_form_button(ack, body, client):
    print("Received sample form button click:", body)
    trigger_id = body["trigger_id"]

    # モーダル表示
    client.views_open(
        trigger_id=trigger_id,
        view=_modal_view(user_id=body["user"]["id"])
    )
    ack()
