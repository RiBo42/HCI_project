from django.shortcuts import render
from .forms import *
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from main.models import UserProfile
from .data_processing import enqueue, hrv_generator, get_ppg
from collections import deque
import json
from django.utils.timezone import make_aware
from datetime import datetime


# BS testing data, delete once DB works
hb = [111.67241,107.87046,113.105446,113.11326,99.753075,98.87414]
l = ["2022-11-18 12:17:14.640", "2022-11-18T12:17:15.609", "2022-11-18T12:17:16.635",
"2022-11-18T12:17:17.599", "2022-11-18T12:17:18.609", "2022-11-18T12:17:19.592"]
l = [x.replace("T", " ") for x in l]
l = [x[:-4] for x in l]
steps = [1000, 1563, 895, 2111, 1192]

ppg_data = deque()
ppg = []
measures = {}
num = 0
entries = {}

#def filter_datetime(request):
	
def data_filtration(request):
	# needs to be currently logged in user
	up = UserProfile.objects.filter(user__username__startswith = "yousuf")[0]
	json_string = json.dumps(up.data)
	unfiltered_data = json.loads(json_string)

	raw_labels = []
	raw_data = []
	final_labels = []
	data = {}

	for key, value in unfiltered_data.items():
		raw_labels.append(key.replace("T", " "))
		raw_data.append(value)
	labels = [datetime.strptime(x[:-7],"%Y-%m-%d %H:%M") for x in raw_labels][::30]

	startDate = datetime.strptime(request.GET.get("begin"), "%Y-%m-%d %H:%M")
	endDate = datetime.strptime(request.GET.get("end"), "%Y-%m-%d %H:%M")
	print(labels[0])
	print(startDate)

	for x in labels:
		if(x > startDate and x < endDate):
			final_labels.append(x)

	# ^^ does nothing rn, just for when I know what to query data-wise, not just date-time wise

	data["heartbeat"] = {
			"labels": l,
            "datasets":[{
                "label": "Heartbeat",
                "data": hb,
                "backgroundColor": "#FF7F00",
                "borderColor": "#FF7F00",
                "pointRadius": 2.5,
                "tension": .25,


            }]
		}
	data["radar"] = {
			"labels": ['Weight', 'Steps', "Heart rate", "Calories burned"],
            "datasets":[{
                "label": "Radar",
                "data": [100,65,80,90],
                "backgroundColor": 'rgba(00, 255, 00, 0.1)',
                "borderColor": 'rgba(00, 255, 00)',
                "borderWidth": 2,


            }]


		}
	data["steps"] = {
			"labels": l,
            "datasets":[{
                "label": "Steps",
                "data": steps,
                "backgroundColor": "#FF7F00",
                "borderColor": "#FF7F00",
                "pointRadius": 2.5,
                "tension": .25,


            }]
		}

	return JsonResponse(data = data, safe = False)



def index(request):
	

	context = {}
	return render(request, 'index.html', context)

def register(request):
    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            # Now we save the UserProfile model instance.
            profile.save()

            # Update our variable to tell the template registration was successful.
            registered = True

        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            print (user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request,
            'register.html',
            {'user_form': user_form, 'profile_form': profile_form, 'registered': registered} )

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('')
            else:
                return HttpResponse("Your account is disabled.")
        else:
            print ("Invalid login details: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login details supplied.")

    else:
        return render(request, 'login.html', {})

def post(request):
	global ppg_data, ppg, sampling_rate
	global measures,num
	userprofile = UserProfile.objects.filter(user__username__startswith = "yousuf")[0]
	stored_measures = userprofile.data #ensure that data field is populated!
	if request.method == 'POST':
	    num += 1
	    print(num)
	    data = json.loads(request.body)
	    if len(data):
	        time = data['time']
	        ppg_data = enqueue(ppg_data, data)
	        sampling_rate, ppg, ppg_data = get_ppg(ppg_data, 60)
	        working_data, measures = hrv_generator(measures, ppg, sampling_rate)
	        if len(ppg) and len(measures):
	            print("SUCCESS!")
	            try:
	                stored_measures[time] = measures
	                userprofile.data = dict(stored_measures)
	                userprofile.save()
	            except Exception as e:
	                print(e)
	entries = len(stored_measures.keys())
	return render(request, 'post.html',context = {'measures':measures,"stored_measures":stored_measures,"entries":entries})
