from sys import maxsize
from django.db import models
from django.contrib.auth.models import User
# from django.contrib.auth.models import User

# # Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.SmallIntegerField(null=True)
    height = models.SmallIntegerField(null=True)
    weight = models.SmallIntegerField(null=True)
    Female = 'Female'
    Male = 'Male'
    sex_choices = [(Female, 'Female'),(Male, 'Male')]
    sex = models.CharField(choices=sex_choices, max_length=7,null=True)
    data = models.JSONField(null=True)

    # Override the __unicode__() method to return out something meaningful!
    def __unicode__(self):
        return self.user.username
class PPG(models.Model):
    date = models.DateTimeField('date inserted')
    time_stamp = models.IntegerField(default=0)
    ppg_signal = models.FloatField(default=0.0)