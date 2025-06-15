import unittest
from unittest.mock import MagicMock
from slack_sdk import WebClient
from app.handler import handle_shortcut, handle_submission


class TestSlackHandler(unittest.TestCase):

    def test_handle_shortcut(self):
        # モックの設定
        event = {
            "type": "shortcut",
            "callback_id": "sample-form",
            "user": {"id": "U12345"},
            "trigger_id": "T12345",
        }
        ack = MagicMock()
        client = WebClient(token="xoxb-test-token")
        client.views_open = MagicMock()

        # ハンドラの実行
        handle_shortcut(event, ack, client)

        # モーダルが正しく開かれたか確認
        client.views_open.assert_called_once_with(
            trigger_id="T12345",
            view={
                "type": "modal",
                "callback_id": "form_submission",
                "title": {"type": "plain_text", "text": "情報入力"},
                "submit": {"type": "plain_text", "text": "送信"},
                "close": {"type": "plain_text", "text": "キャンセル"},
                "private_metadata": event["user"]["id"],
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
        )
 
    def test_handle_submission(self):
        # モックの設定
        payload = {
            "type": "view_submission",
            "state": {
                "values": {
                    "input_block": {
                        "input_value": {
                            "value": "テスト入力"
                        }
                    }
                }
            },
            "private_metadata": "U12345",
        }
        ack = MagicMock()
        client = WebClient(token="xoxb-test-token")
        client.chat_postMessage = MagicMock()

        # ハンドラの実行
        handle_submission(payload, ack, client)

        # メッセージが正しく送信されたか確認
        client.chat_postMessage.assert_called_once_with(
            channel="U12345",
            text="あなたが入力した情報: *テスト入力*",
        )
        ack.assert_called_once_with(
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
                            "text": "あなたが入力した情報: *テスト入力*"
                        }
                    }
                ],
                "close": {"type": "plain_text", "text": "閉じる"},
            }
        )
