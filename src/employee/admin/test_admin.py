import math

# Needed for optional Features
# from django.db.models import Count, Case, When, Value, BooleanField


# base admin class for this all model


def sToTime(duration):
    minutes = math.floor((duration / 60) % 60)
    hours = math.floor((duration / (60 * 60)) % 24)

    return f"{hours:01}h: {minutes:01}m"
