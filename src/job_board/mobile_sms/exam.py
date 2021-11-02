from config import settings
import requests

from job_board.models.candidate import CandidateAssessment


class ExamSMS:
    def __init__(self, candidate_assessment: CandidateAssessment):
        self.candidate_assessment = candidate_assessment
        self.api_endpoint = 'https://msg.elitbuzz-bd.com/smsapi'
        self.api_key = settings.SMS_API_KEY
        self.sender_id = settings.SMS_SENDER_ID
        self.sms_end_point = f'{self.api_endpoint}?api_key={self.api_key}&type=text' \
                             f'&contacts={self.candidate_assessment.candidate_job.candidate.phone}' \
                             f'&senderid={self.sender_id}'

    def reminder_sms(self):
        message = f'You have applied at ' \
                  f'the position {self.candidate_assessment.candidate_job.job.title}. ' \
                  f'\nCheck your email (inbox/spam/promotions) for the {self.candidate_assessment.assessment.type} exam.' \
                  f'\nQuery :01750020408'
        self.sms_end_point += f'&msg={message}'
        requests.get(self.sms_end_point, verify=False)

    def promotional_sms(self, message):
        message = message.format(full_name=self.candidate_assessment.candidate_job.candidate.full_name,
                                 candidate_job=self.candidate_assessment.candidate_job.job.title)
        self.sms_end_point += f'&msg={message}'
        requests.get(self.sms_end_point, verify=False)
