from collections import OrderedDict

from django.db.models import Sum
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework.serializers import ModelSerializer

from job_board.models import Assessment, AssessmentAnswer, AssessmentQuestion, CandidateJob, CandidateAssessmentAnswer


class AssessmentSerializer(ModelSerializer):
    class Meta:
        model = Assessment
        fields = ['title', 'slug', 'description', 'score', 'duration']


class AssessmentAnswerSerializer(ModelSerializer):
    class Meta:
        model = AssessmentAnswer
        fields = ('id', 'title')


class AssessmentQuestionSerializer(ModelSerializer):
    answers = AssessmentAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = AssessmentQuestion
        fields = ('id', 'title', 'type', 'answers')


def valid_uuid(value):
    if not CandidateJob.objects.filter(unique_id=value).first():
        raise serializers.ValidationError('Your given uuid has been expire')


class GivenAssessmentAnswerSerializer(serializers.Serializer):
    """
    Most complicated part, Handle with care
    TODO : i need to modify the comment and it should be elaborate
    """
    uuid = serializers.UUIDField(validators=[valid_uuid])
    question_id = serializers.IntegerField(min_value=1)
    answers = serializers.ListField(child=serializers.IntegerField(min_value=1), min_length=1)

    candidate_job = CandidateJob
    question = AssessmentQuestion
    candidate_answer = CandidateAssessmentAnswer

    def validate(self, data: OrderedDict):
        self.candidate_job = CandidateJob.objects.filter(unique_id=data['uuid']).first()
        self.question = AssessmentQuestion.objects.get(pk=data['question_id'])
        if self.question.type == 'single_choice' and len(data['answers']) > 1:
            raise serializers.ValidationError(
                {
                    'answers': f'{self.question.get_type_display()} allow single answer, your answer {len(data["answers"])}'})
        return data

    def create(self, validated_data):
        assessment_answer = AssessmentAnswer.objects.filter(pk__in=validated_data['answers'],
                                                            assessment_question_id__exact=validated_data[
                                                                'question_id']
                                                            ).all()
        candidate_answer = CandidateAssessmentAnswer.objects.filter(question=self.question,
                                                                    candidate_job=self.candidate_job).first()
        if not candidate_answer:
            self._create_answer(assessment_answer=assessment_answer)
            return validated_data
        raise serializers.ValidationError({'message': 'This answer has been taken already'})

    def _create_answer(self, assessment_answer):
        candidate_answer = CandidateAssessmentAnswer()
        candidate_answer.candidate_job = self.candidate_job
        candidate_answer.question = self.question
        candidate_answer.answers = AssessmentAnswerSerializer(assessment_answer, many=True).data
        candidate_answer.total_score = self.question.score
        candidate_answer.score_achieve = assessment_answer.aggregate(score_achieve=Sum('score'))['score_achieve']
        candidate_answer.save()
        self._step_increment()
        self._add_mcq_mark(candidate_answer.score_achieve)

    def _step_increment(self):
        self.candidate_job.step['current_step'] += 1
        self.candidate_job.save()

    def _add_mcq_mark(self, score):
        self.candidate_job.mcq_exam_score += score
        self.candidate_job.save()
