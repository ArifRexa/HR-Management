from django import template

from job_board.models.assessment import AssessmentQuestion, AssessmentAnswer
from job_board.models.candidate import CandidateAssessmentAnswer, CandidateAssessment

register = template.Library()


@register.filter
def get_candidate_answer(assessment_question: AssessmentQuestion, candidate_assessment: CandidateAssessment):
    candidate_assessment_answer = CandidateAssessmentAnswer.objects.filter(
        question=assessment_question,
        candidate_job=candidate_assessment.candidate_job
    ).first()
    formatted_answer = ''

    if candidate_assessment_answer is not None:
        for answer in candidate_assessment_answer.answers:
            formatted_answer += f"{answer['title']}"
        formatted_answer += f"{candidate_assessment_answer.score_achieve} </br>"
    return formatted_answer
