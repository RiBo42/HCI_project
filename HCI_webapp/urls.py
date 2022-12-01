"""HCI_webapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from main.views import index
from main import views
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/',views.user_login,name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('search_results/<slug:username>', views.search_results, name='search_results'),
    path('add_friend/<slug:username>/<friend>', views.add_friend, name='add_friend'),
    path('confirm_request/<slug:username>/<friend>', views.confirm_request, name='confirm_request'),
    path('post/',views.post,name='post'),
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('hello/', views.HelloView.as_view(), name='hello'),
    path('user/<slug:username>',views.user, name = 'user'),
    path('user/<slug:username>/allstats', views.all_stats, name='allstats'),
    path('user/<slug:username>/friends', views.friends, name= 'friends'),
    path('user/<slug:username>/friendrequests', views.friend_requests, name='friendrequests'),
    path('user/<slug:username>/settings', views.settings,name='settings'),
    path('post/',views.post,name='post'),   
    path("filter/", views.data_filtration, name="filter"),   
    path('mood/',views.mood,name='mood'),   

]
