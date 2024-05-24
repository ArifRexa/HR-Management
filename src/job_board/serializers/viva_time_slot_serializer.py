from rest_framework import serializers
from job_board.models import VivaConfig, JobVivaTimeSlot


# class VivaConfigSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = VivaConfig
#         fields = '__all__'
#
#
# # class JobVivaTimeSlotSerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = JobVivaTimeSlot
# #         fields = '__all__'
# # serializers.py
#
#
# class JobVivaTimeSlotSerializer(serializers.ModelSerializer):
#     candidate_name = serializers.SerializerMethodField()
#
#     class Meta:
#         model = JobVivaTimeSlot
#         fields = ['id', 'start_time', 'end_time', 'date', 'job_post', 'candidate', 'candidate_name']
#
#     def get_candidate_name(self, obj):
#         if obj.candidate:
#             return obj.candidate.full_name
#         return None


# class BookedTimeSlotSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = JobVivaTimeSlot
#         # fields = ['id', 'job_post', 'candidate', 'start_time', 'end_time', 'date']
#         fields = ['date', 'start_time', 'end_time']
#
#
# class JobVivaTimeSlotSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = JobVivaTimeSlot
#         fields = ['date', 'start_time', 'end_time']
#
#
# class VivaConfigSerializer(serializers.ModelSerializer):
#     booked_slots = JobVivaTimeSlotSerializer(many=True, read_only=True)
#
#     class Meta:
#         model = VivaConfig
#         fields = ['start_date', 'end_date', 'start_time', 'end_time', 'booked_slots']

# class BookedTimeSlotSerializer(serializers.ModelSerializer):
#     start_date = serializers.SerializerMethodField()
#     end_date = serializers.SerializerMethodField()
#     start_time = serializers.SerializerMethodField()
#     end_time = serializers.SerializerMethodField()
#     booked_slots = serializers.SerializerMethodField()
#
#     class Meta:
#         model = JobVivaTimeSlot
#         fields = ['start_date', 'end_date', 'start_time', 'end_time', 'booked_slots']
#
#     def get_start_date(self, obj):
#         return obj.job_post.start_date.strftime("%Y-%m-%d") if obj.job_post else None
#
#     def get_end_date(self, obj):
#         return obj.job_post.end_date.strftime("%Y-%m-%d") if obj.job_post else None
#
#     def get_start_time(self, obj):
#         return obj.job_post.start_time.strftime("%H:%M:%S") if obj.job_post else None
#
#     def get_end_time(self, obj):
#         return obj.job_post.end_time.strftime("%H:%M:%S") if obj.job_post else None
#
#     def get_booked_slots(self, obj):
#         booked_slots = []
#         for slot in obj:
#             booked_slots.append({
#                 "date": slot.date.strftime("%Y-%m-%d"),
#                 "start_time": slot.start_time.strftime("%H:%M:%S"),
#                 "end_time": slot.end_time.strftime("%H:%M:%S")
#             })
#         return booked_slots

class JobVivaTimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobVivaTimeSlot
        fields = ['id', 'job_post', 'candidate', 'start_time', 'end_time', 'date']


class JobPostByStartTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobVivaTimeSlot
        fields = ['start_time']

class VivaConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = VivaConfig
        fields = ['id', 'job_post', 'duration', 'start_date', 'end_date', 'start_time', 'end_time']


class VivaConfigWithBookedSlotsSerializer(serializers.ModelSerializer):
    booked_slots = serializers.SerializerMethodField()

    class Meta:
        model = VivaConfig
        fields = ['start_date', 'end_date', 'start_time', 'end_time', 'booked_slots']

    def get_booked_slots(self, obj):
        booked_slots = JobVivaTimeSlot.objects.filter(
            job_post=obj.id,
            date__range=[obj.start_date, obj.end_date],
            start_time__gte=obj.start_time,
            end_time__lte=obj.end_time
        )
        return JobVivaTimeSlotSerializer(booked_slots, many=True).data
