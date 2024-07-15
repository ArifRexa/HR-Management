from django.db import models

class WomanEmpowerment(models.Model):
    title = models.CharField(max_length=200)
    short_description = models.TextField()
    banner_image = models.ImageField(upload_to='empowerment_banners/')

    environment_title = models.CharField(max_length=200, null=True, blank=True)
    environment_short_description = models.TextField(null=True, blank=True)
    environment_image = models.ImageField(upload_to='work_environment_images/')

    def __str__(self):
        return self.title
    
class WomanAchievement(models.Model):
    empowerment = models.ForeignKey(WomanEmpowerment, related_name='achievements', on_delete=models.CASCADE)
    achievement_title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='achievement_images/')

    def __str__(self):
        return self.achievement_title

class WomanInspiration(models.Model):
    empowerment = models.ForeignKey(WomanEmpowerment, related_name='inspirations', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='inspiration_images/')

    def __str__(self):
        return self.name
    
class Environment(models.Model):
    empowerment = models.ForeignKey(WomanEmpowerment, related_name='environments', on_delete=models.CASCADE)
    subtitle = models.CharField(max_length=200)
    sub_short_description = models.TextField()
    icon = models.ImageField(upload_to='environment_icons/')

    def __str__(self):
        return self.subtitle

class Photo(models.Model):
    empowerment = models.ForeignKey(WomanEmpowerment, related_name='photos', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='empowerment_photos/')

    def __str__(self):
        return f"Photo for {self.empowerment.title}"