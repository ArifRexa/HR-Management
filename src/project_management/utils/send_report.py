from slack import WebClient
from slack.errors import SlackApiError


def send_report_slack(token: str, channel: str, message: str, is_user=None):
    client = WebClient(token=token)
    try:
        payload = {
            'channel': channel,
            'text': message

        }
        if is_user:
            payload['as_user'] = True
        response = client.chat_postMessage(**payload)
    except SlackApiError as e:
        assert e.response["ok"] is False
