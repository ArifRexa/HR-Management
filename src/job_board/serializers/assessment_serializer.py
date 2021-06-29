from rest_framework.serializers import ModelSerializer

from job_board.models import Assessment, AssessmentAnswer, AssessmentQuestion


class AssessmentSerializer(ModelSerializer):
    class Meta:
        model = Assessment
        fields = '__all__'


class AssessmentAnswerSerializer(ModelSerializer):
    class Meta:
        model = AssessmentAnswer
        fields = ('id', 'title')


class AssessmentQuestionSerializer(ModelSerializer):
    answers = AssessmentAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = AssessmentQuestion
        fields = ('id', 'title', 'score', 'type', 'answers')
