import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
'HCI_webapp.settings')

import django
django.setup()

from main.models import UserProfile
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
import random
import json
import string
testing = False
def populate():
    f = open('data.json')
    data_file = json.load(f)
    n = int(len(data_file.keys())/10)
    items = list((data_file.items()))
    users = [{'username': 'Yousuf','age':21,'height':183,
                'weight':62,'sex':'Male','data':dict(items[0:n]),'steps':generate_steps()},
            {'username': 'Marianna','age':25,'height':173,
                        'weight':62,'sex':'Female','data':dict(items[n:2*n]),'steps':generate_steps()},
            {'username': 'Joseph','age':19,'height':183,
                        'weight':74,'sex':'Male','data':dict(items[2*n:3*n]),'steps':generate_steps()},
            {'username': 'Adam','age':55,'height':193,
                        'weight':90,'sex':'Male','data':dict(items[3*n:4*n]),'steps':generate_steps()},
            {'username': 'Rebecca','age':18,'height':153,
                        'weight':55,'sex':'Female','data':dict(items[4*n:5*n]),'steps':generate_steps()},
            {'username': 'Roberta','age':19,'height':167,
                        'weight':59,'sex':'Female','data':dict(items[5*n:6*n]),'steps':generate_steps()},
            {'username': 'Isabella','age':34,'height':160,
                        'weight':75,'sex':'Female','data':dict(items[6*n:7*n]),'steps':generate_steps()},
            {'username': 'Smith','age':40,'height':199,
                        'weight':130,'sex':'Male','data':dict(items[7*n:8*n]),'steps':generate_steps()},
            {'username': 'Lars','age':64,'height':140,
                        'weight':100,'sex':'Male','data':dict(items[8*n:9*n]),'steps':generate_steps()},
            {'username': 'Leopold','age':20,'height':153,
                        'weight':100,'sex':'Male','data':dict(items[9*n:10*n]),'steps':generate_steps()},]
    for user in users:
        try:
            if not testing:
                u,mypass = add_UserProfile(user['username'],user['age'],user['height'],user['weight'],user['sex'],user['data'],user['steps'])
                print("Successfully created user",u.user,'with password:',mypass)
            else:
                print("test")
        except Exception as e:
            print('Failed to add UserProfile',e)
    if not testing:
        superuser=User.objects.create_user('y', password = 'y')
        superuser.is_superuser=True
        superuser.is_staff=True
        superuser.save()
def create_user(username):
    try:
        mypass = get_random_string(8)
        user=User.objects.create_user(username, password=mypass)
        user.is_superuser=True
        user.is_staff=True
        user.save()
        return user
    except Exception as e:
        print(e)
def add_UserProfile(username,age, height, weight,sex,data,steps):
    mypass = get_random_string(8)
    user = create_user(username)
    u = UserProfile.objects.get_or_create(user= user)[0]
    u.user = user
    u.age = age
    u.height = height
    u.weight=weight
    u.sex=sex
    u.data=data
    u.steps=steps
    u.save()
    return u,mypass
def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str
def generate_steps():
    date = [1,1,2022]
    dates = []
    steps = {}
    for i in range(30):
        dates.append([i+1,1,2022])
        step = random.randrange(5000,7000)
        date = str(i+1)+'1'+'2022'
        steps[date] = step
    return steps
# Start execution here!
if __name__ == '__main__':
    print("Starting MyMind population script...")
    populate()
