from django.shortcuts import render,redirect
from .forms import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
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

ppg_data = deque()
ppg = []
measures = {}
num = 0
entries = {}
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
	userprofile = UserProfile.objects.filter(user__username__startswith = "yousuf")[0]
	stored_measures = userprofile.data #ensure that data field is populated!
	if request.method == 'POST':
		num += 1
		print(num)
		data = json.loads(request.body)
		if len(data):
			with open('innovators.csv', 'w', newline='') as file:
				writer = csv.writer(file)
				time = data['time']
				ppg_data = enqueue(ppg_data, data)
				sampling_rate, ppg, ppg_data = get_ppg(ppg_data, 60)
				working_data, measures = hrv_generator(measures, ppg, sampling_rate)
				if len(ppg) and len(measures):
					print("SUCCESS!")
					try:
						s_measures = {}
						s_measures[time] = measures
						writer.writerow(s_measures)
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

def user(request,username):
	userprofile = UserProfile.objects.filter(user__username__startswith = username)[0]
	return render(request, 'user.html', context = {"userprofile":userprofile,})

class TodayPageView(TemplateView):
    template_name = "today.html"


class AllStatsPageView(TemplateView):
    template_name = "allstats.html"

class FriendsPageView(TemplateView):
    template_name = 'friends.html'

class FriendRequestsView(TemplateView):
    template_name = 'friendrequests.html'

class SettingsView(TemplateView):
    template_name = 'settings.html'
