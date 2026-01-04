"""
URL configuration for VotingProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path
from VotingApp import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('common/', views.common, name='common'),
    path('CandidateRegistration/', views.CandidateRegistration, name='CandidateRegistration'),
    path('VoterRegistration/', views.VoterRegistration, name='VoterRegistration'),
    path('login/', views.login, name='login'),
    path('vhome/', views.vhome, name='vhome'),
    path('voting/', views.voting, name='voting'),
    path('adminhome/', views.adminhome, name='adminhome'),
    path('adminviewcandidates/', views.adminviewcandidates, name='adminviewcandidates'),
    path('adminviewvoters/', views.adminviewvoters, name='adminviewvoters'),
    path('adminviewelections/', views.adminviewelections, name='adminviewelections'),
    path('adminaddelection/', views.adminaddelection, name='adminaddelection'),
    path('adminviewresults/', views.adminviewresults, name='adminviewresults'),
    path('otpverification/', views.otpvalidation, name='otpverification'),
]