from sys import maxsize
from django.db import models
from django.contrib.auth.models import User
# from django.contrib.auth.models import User

# # Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.SmallIntegerField()
    height = models.SmallIntegerField()
    weight = models.SmallIntegerField()
    Female = 'Female'
    Male = 'Male'
    sex_choices = [(Female, 'Female'),(Male, 'Male')]
    sex = models.CharField(choices=sex_choices, max_length=7)

    # Override the __unicode__() method to return out something meaningful!
    def __unicode__(self):
        return self.user.username