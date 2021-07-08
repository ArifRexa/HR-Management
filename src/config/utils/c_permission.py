import datetime

from django.db.models import Model


def older(object_id: int, model: Model):
    three_day_earlier = datetime.datetime.today() - datetime.timedelta(days=2)
    obj = model.objects.filter(id=object_id, created_at__gte=three_day_earlier).filter()
    if obj:
        return True
    return False
