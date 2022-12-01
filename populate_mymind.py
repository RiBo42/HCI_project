import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
'HCI_webapp.settings')

import django
django.setup()

from main.models import UserProfile
from main.data_processing import calorie_calc, get_minutes
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
import random
import json
import string
testing = False
def populate():
    f = open('data.json')
    data_file = json.load(f)
    keys = list(data_file.keys())
    n = int(len(data_file.keys())/10)
    items = list((data_file.items()))
    filtered_data = {}
    f_items = dict(items)
    c = 0
    hrate = []
    nrate = []
    lrate = []
    for dtime in keys:
        bpm = f_items[dtime]['bpm']
        filtered_data[dtime] =bpm
        if bpm <= 100.0 and bpm >= 60:
            nrate.append(bpm)
        elif bpm >= 100.0:
            hrate.append(bpm)
        elif bpm < 60.0:
            lrate.append(bpm)
    generate_data({"hrate":hrate,"nrate":nrate,"lrate":lrate},False,62,21,"Male")
    #{"date":{"avg_bpm":avg_bpm,"steps":steps,"Sleep":sleep,"24hr_heart":{"00:00":avg_rate,...,"23:00":avg_rate}}}
    users = [{'username': 'Yousuf','age':21,'height':183,
                'weight':62,'sex':'Male','data':generate_data({"hrate":hrate,"nrate":nrate,"lrate":lrate},False,62,21,"Male")},
            {'username': 'Marianna','age':25,'height':173,
                        'weight':62,'sex':'Female','data':generate_data({"hrate":hrate,"nrate":nrate,"lrate":lrate},False,62,25,"Female")},
            {'username': 'Joseph','age':19,'height':183,
                        'weight':74,'sex':'Male','data':generate_data({"hrate":hrate,"nrate":nrate,"lrate":lrate},True,74,19,"Male")},
            {'username': 'Adam','age':55,'height':193,
                        'weight':90,'sex':'Male','data':generate_data({"hrate":hrate,"nrate":nrate,"lrate":lrate},True,90,55,"Male")},
            {'username': 'Rebecca','age':18,'height':153,
                        'weight':55,'sex':'Female','data':generate_data({"hrate":hrate,"nrate":nrate,"lrate":lrate},True,55,18,"Female")},
            {'username': 'Roberta','age':19,'height':167,
                        'weight':59,'sex':'Female','data':generate_data({"hrate":hrate,"nrate":nrate,"lrate":lrate},False,59,19,"Female")},
            {'username': 'Isabella','age':34,'height':160,
                        'weight':75,'sex':'Female','data':generate_data({"hrate":hrate,"nrate":nrate,"lrate":lrate},True,75,34,"Female")},
            {'username': 'Smith','age':40,'height':199,
                        'weight':130,'sex':'Male','data':generate_data({"hrate":hrate,"nrate":nrate,"lrate":lrate},True,130,40,"Male")},
            {'username': 'Lars','age':64,'height':140,
                        'weight':100,'sex':'Male','data':generate_data({"hrate":hrate,"nrate":nrate,"lrate":lrate},True,100,64,"Male")},
            {'username': 'Leopold','age':20,'height':153,
                        'weight':100,'sex':'Male','data':generate_data({"hrate":hrate,"nrate":nrate,"lrate":lrate},True,100,20,"Male")},]
    for user in users:
        try:
            if not testing:
                u,mypass = add_UserProfile(user['username'],user['age'],user['height'],user['weight'],user['sex'],user['data'])
                print("Successfully created user",u.user,'with password:',mypass)
            else:
                print("Test passed")
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
def add_UserProfile(username,age, height, weight,sex,data):
    mypass = get_random_string(8)
    user = create_user(username)
    u = UserProfile.objects.get_or_create(user= user)[0]
    u.user = user
    u.age = age
    u.height = height
    u.weight=weight
    u.sex=sex
    u.data=data
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
        date = str(i+1)+',1,'+'2022'
        steps[date] = step
    return steps
def step():
    step = random.randrange(5000,7000)
    return step
def generate_data(bpm_dict,stressed,kg,age,sex):
    lists = ["hrate","nrate","lrate"]
    bpm = []
    calories = 0.0
    data = {}
    days = ["01/01/2022","02/01/2022","03/01/2022"]
    c= 0
    #{"date":{"avg_bpm":avg_bpm,"steps":steps,"Sleep":sleep,"24hr_heart":{"00:00":avg_rate,...,"23:00":avg_rate}}}
    for i in range(72):
        if stressed:
            myList = random.choices(lists, cum_weights=(60,40,20), k=1)
        else:
            myList = random.choices(lists, cum_weights=(20, 50, 70), k=1)
        bpm.append(random.choice(bpm_dict[myList[0]]))
        if len(bpm) ==24:
            calories = r_calorie_calc(bpm,kg,age,sex)
            data[days[c]] ={"avg_bpm":sum(bpm)/24,"steps":step(),"calories":calories,"Sleep":random.randrange(5,10),"24hr_heart":bpm}
            bpm =[]
            c+=1
    return data
def r_calorie_calc(arr,kg,age,sex):
    bpm = 0.0
    sex = sex.lower()
    sexes = {'male':[0.6309,0.1988,0.2017,55.0969,4.184],'female':[0.4472,-0.1263,0.074,20.4022,4.184]}
    count = len(arr)
    for entry in arr:
        bpm+=entry
    avg_bpm = bpm/count
    calories_burnt = (24*60*60)*(sexes[sex][0]*avg_bpm +sexes[sex][1]*kg+sexes[sex][2]*age - sexes[sex][2])/sexes[sex][3]
    return calories_burnt
# Start execution here!
if __name__ == '__main__':
    print("Starting MyMind population script...")
    populate()