from django.shortcuts import render,redirect
from .forms import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from main.models import UserProfile
from .data_processing import enqueue, hrv_generator, get_ppg,calorie_calc
from collections import deque
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.views.generic import TemplateView
import csv
from django.forms.models import model_to_dict

ppg_data = deque()
ppg = []
measures = {}
num = 0
entries = {}

# average of user data
def Average(l):
	if(len(l) != 0):
		return sum(l) / len(l)
	else:
		return None

# should have been an insights template with how the user's data compares to others
# and how it increases their risks of various ailments
def mood(request):

	context = {}
	return render(request, 'mood.html', context)




# Basal metabolic rate for maintenance calorie calculator
def get_bmr(gender, weight, height, age):
	if(gender=="Female"):
		return int(655 + ((4.35 * weight) + (4.7 * height) - (4.7 * age)))
	else:
		return int(66 + ((6.3 * weight) + (12.9 * height) - (6.8 * age)))


# Filter and provide relevant data
def data_filtration(request):
	up = UserProfile.objects.filter(user__username__startswith = "yousuf")[0]
	json_string = json.dumps(up.data)
	unfiltered_data = json.loads(json_string)

	# Borders for datetime filtration
	startDate = datetime.strptime(request.GET.get( 	"begin"), "%d/%m/%Y %H:%M")
	endDate = datetime.strptime(request.GET.get("end"), "%d/%m/%Y %H:%M")

	# lists to be filled
	raw_labels = []
	raw_data = []
	final_labels = []
	final_data = []
	data = {}
	heartbeat = []
	steps = []
	sleep = []
	calories = []
	user_percentages = None


	# modify data structure
	for key, value in unfiltered_data.items():
		key = datetime.strptime(key,"%d/%m/%Y")
		if(key > startDate and key < endDate):
			heartbeat.append(value["avg_bpm"])
			steps.append(value["steps"])
			sleep.append(value["Sleep"])
			calories.append(value["calories"])
			final_labels.append(key)


	# average healthy values
	user_calories = get_bmr(up.sex,up.weight,up.height,up.age)

	# average user values
	user_health = [Average(heartbeat),Average(steps),Average(sleep),Average(calories)]
	if(user_health[0] == None):
		pass
	else:
		user_percentages = [
		(user_health[0]/80),
		(user_health[1]/3000),
		(user_health[2]/7),
		(user_health[3]/user_calories),
	]

	# ^ is % of healthy limit the user's data is achieving

	# all the dictionarty entires feed data to the frontend charts
	data["heartbeat"] = {
			"labels": final_labels,
            "datasets":[{
                "label": "Heartbeat",
                "data": heartbeat,
                "backgroundColor": "#FF7F00",
                "borderColor": "#FF7F00",
                "pointRadius": 2,
                "tension": .25,


            }]
		}

	data["radar"] = {
				"labels": ['Heart rate', 'Steps', "Sleep", "Calories burned"],
	            "datasets":[{
	                "label": "Your Average Health Data",
	                "data": user_percentages,
	                "backgroundColor": 'rgba(00, 255, 00, 0.1)',
	                "borderColor": 'rgba(00, 255, 00)',
	                "borderWidth": 2,
	            },{
	                "label": "Healthy Limits",
	                "data": [1,1,1,1],
	                "backgroundColor": 'rgba(255, 00, 00, 0.1)',
	                "borderColor": 'rgba(255, 00, 00)',
	                "borderWidth": 2,
	            }]


			}

	data["steps"] = {
			"labels": final_labels,
            "datasets":[{
                "label": "Steps",
                "data": steps,
                "backgroundColor": "#FF7F00",
                "borderColor": "#FF7F00",
                "pointRadius": 2,
                "tension": .25,


            }]
		}

	data["sleep"] = {
			"labels": final_labels,
            "datasets":[{
                "label": "Sleep",
                "data": sleep,
                "backgroundColor": "#FF7F00",
                "borderColor": "#FF7F00",
                "pointRadius": 2,
                "tension": .25,


            }]
		}

	data["calories"] = {
			"labels": final_labels,
            "datasets":[{
                "label": "Calories burned",
                "data": calories,
                "backgroundColor": "#FF7F00",
                "borderColor": "#FF7F00",
                "pointRadius": 2,
                "tension": .25,


            }]
		}

	return JsonResponse(data = data, safe = False)



def index(request):
  context = {}
  return render(request, 'index.html', context)
class HelloView(APIView):
	permission_classes = (IsAuthenticated,)

	def get(self, request):
		content = {'message': 'Hello, World!'}
		return Response(content)
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

			# Update our variable to tell the template registration was success
			# ful.
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
				return redirect(reverse('index'))
			else:
				return HttpResponse("Your account is disabled.")
		else:
			print ("Invalid login details: {0}, {1}".format(username, password))
			return HttpResponse("Invalid login details supplied.")

	else:
		return render(request, 'login.html', {})

@login_required
def user_logout(request):
# Since we know the user is logged in, we can now just log them out.
	logout(request)
# Take the user back to the homepage.
	return redirect(reverse('index'))
def post(request):
	global ppg_data, ppg, sampling_rate
	global measures,num
	#userprofile = UserProfile.objects.filter(user__username__startswith = "yousuf")[0]
	stored_measures = userprofile.data #ensure that data field is populated!
	if request.method == 'POST':
		num += 1
		print(num)
		data = json.loads(request.body)
		if len(data):
			writer = csv.writer(file)
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
	calories = calorie_calc(stored_measures,userprofile.weight,userprofile.height,userprofile.sex)
	userprofile.calories_burnt = calories
	userprofile.save()
	return render(request, 'post.html',context = {'measures':measures,"stored_measures":stored_measures,"entries":entries,"calories":calories})

def user(request,username):
	userprofile = UserProfile.objects.filter(user__username__startswith = username)[0]
	sleep = userprofile.data["01/01/2022"]['Sleep']
	calories = userprofile.data["01/01/2022"]['calories']
	steps = userprofile.data["01/01/2022"]['steps']
	heart_24 = userprofile.data["01/01/2022"]['24hr_heart']
	bpm = userprofile.data["01/01/2022"]['avg_bpm']
	print(bpm)
	return render(request, 'user.html', context = {"userprofile":userprofile,"sleep":sleep,'steps':steps,'heart_24':heart_24,'bpm':bpm,'calories':calories})




def all_stats(request, username):
	return render(request, 'allstats.html', context = {})

def friends(request, username):
	userprofile = UserProfile.objects.filter(user__username__startswith = username)[0]
	friends = userprofile.friends
	friends_list = []
	for f in list(friends.keys()):
		friends_list.append(UserProfile.objects.filter(user__username__startswith = f)[0])
	friends = friends_list
	return render(request, 'friends.html', context = {'friends':friends})

def friend_requests(request, username):
	userprofile = UserProfile.objects.filter(user__username__startswith = username)[0]
	friend_requests = userprofile.friend_requests
	return render(request, 'friendrequests.html', context = {"friend_requests":friend_requests})

def settings(request, username):
	return render(request, 'settings.html', context = {})
def add_friend(request, username,friend):
	userprofile = UserProfile.objects.filter(user__username__startswith = username)[0]
	friend_profile = UserProfile.objects.filter(user__username__startswith = friend)[0]
	friends = userprofile.friends
	friends_list = []
	for f in list(friends.keys()):
		friends_list.append(UserProfile.objects.filter(user__username__startswith = f)[0])
	friends = friends_list
	user_username = userprofile.user.username
	friend_username = friend_profile.user.username
	sent_requests = userprofile.sent_requests
	sent_requests[friend_username] = friend_username
	userprofile.sent_requests = dict(sent_requests)
	userprofile.save()
	friend_requests = friend_profile.friend_requests
	friend_requests[user_username] = user_username
	friend_profile.friend_requests = friend_requests
	friend_profile.save()
	return render(request, 'friends.html',context = {'friends':friends})
def search_results(request, username):
	userprofile = UserProfile.objects.filter(user__username__startswith = username)[0]
	ref = request.headers['Referer']
	search = request.GET['q']
	results = UserProfile.objects.filter(user__username__startswith = search).exclude(user__username__startswith=username)
	friends = userprofile.friends
	friends_list = []
	for f in list(friends.keys()):
		friends_list.append(UserProfile.objects.filter(user__username__startswith = f)[0])
	friends = friends_list
	sent_requests = list(userprofile.sent_requests.keys())
	friend_requests = list(userprofile.friend_requests.keys())
	print(sent_requests)
	return render(request, 'friends.html',context = {'results':results,'friends':friends, 'sent_requests':sent_requests,'friend_requests':friend_requests})
def confirm_request(request, username, friend):
	userprofile = UserProfile.objects.filter(user__username__startswith = username)[0]
	friend_profile = UserProfile.objects.filter(user__username__startswith = friend)[0]
	friends = userprofile.friends
	friend_friends = friend_profile.friends
	user_username = userprofile.user.username
	friend_username = friend_profile.user.username
	friends[friend_username] = friend_username
	userprofile.friends = friends
	userprofile.friend_requests.pop(friend_username)
	friend_requests = userprofile.friend_requests
	userprofile.save()
	friend_friends[user_username] = user_username
	friend_profile.sent_requests.pop(user_username)
	friend_profile.friends = friend_friends
	friend_profile.save()
	friends_list = []
	for f in list(friends.keys()):
		friends_list.append(UserProfile.objects.filter(user__username__startswith = f)[0])
	friends = friends_list
	for f in list(friends.keys()):
		friends_list.remove(UserProfile.objects.filter(user__username__startswith = f)[0])
	friends = friends_list
	return render(request, 'friends.html',context = {'friend_requests':friend_requests})
