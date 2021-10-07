import requests

from config import settings


class BaseSMS:
    def __init__(self):
        self.api_endpoint = 'https://msg.elitbuzz-bd.com/smsapi'
        self.api_key = settings.SMS_API_KEY
        self.sender_id = settings.SMS_SENDER_ID
        self.sms_end_point = f'{self.api_endpoint}?api_key={self.api_key}&type=text' \
                             f'&senderid={self.sender_id}'

    def send_sms(self, message: str, contact_number: int):
        message = message
        sms = self.sms_end_point
        sms += f'&contacts={contact_number}&msg={message}'
        requests.get(sms, verify=False)
