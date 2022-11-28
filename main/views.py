from django.shortcuts import render
from .forms import *
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from main.models import UserProfile
from .data_processing import enqueue, hrv_generator, get_ppg,calorie_calc
from collections import deque
import json

ppg_data = deque()
ppg = []
measures = {}
num = 0
entries = {}
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
	print(userprofile.age)
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
	print(type(userprofile.sex))
	calories = calorie_calc(stored_measures,userprofile.weight,userprofile.height,userprofile.sex)
	userprofile.calories_burnt = calories
	userprofile.save()
	return render(request, 'post.html',context = {'measures':measures,"stored_measures":stored_measures,"entries":entries,"calories":calories})
