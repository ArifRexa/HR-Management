import requests

from config import settings
from job_board.models.candidate import Candidate


class CandidateSMS:
    def __init__(self, candidate: Candidate):
        self.candidate = candidate
        self.api_endpoint = 'https://msg.elitbuzz-bd.com/smsapi'
        self.api_key = settings.SMS_API_KEY
        self.sender_id = settings.SMS_SENDER_ID
        self.sms_end_point = f'{self.api_endpoint}?api_key={self.api_key}&type=text' \
                             f'&contacts={self.candidate.phone}' \
                             f'&senderid={self.sender_id}'

    def promotional_sms(self, message):
        message = message.format(full_name=self.candidate.full_name, candidate_job='')
        self.sms_end_point += f'&msg={message}'
        requests.get(self.sms_end_point, verify=False)
