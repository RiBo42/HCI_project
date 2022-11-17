from django.shortcuts import render


def index(request):
	context = {}
	return render(request, 'index.html', context)


#def chart_data(request):


