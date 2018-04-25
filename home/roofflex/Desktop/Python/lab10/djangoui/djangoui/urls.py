"""djangoui URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib.auth.views import login, logout
from django.contrib import admin
#from myui.views import ListDataView
from myui.views import *
from django.conf.urls import url

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^register/$', RegisterFormView.as_view(), name='register'),
    url(r'^ajax/validate_username/$', validate_username, name='validate_username'),
    url(r'^accounts/confirm/(?P<activation_key>\w+)/', register_confirm, name = 'register_confirm'),
    url(r'^login/$' , LoginFormView.as_view(), name='login'),
    url(r'^error/$', Errorfunc, name='error'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^todolists/$', todolists, name='list'),
    url(r'^todolists/create/$', todolist_create, name='todolist_create'),
    url(r'^todolists/(?P<pk>[0-9]+)/$', todolist_detail, name='list-detail'),
    url(r'^todolists/(?P<pk>[0-9]+)/update/$', todolist_update, name='todolist_update'),
    url(r'^todolists/(?P<pk>[0-9]+)/delete/$', todolist_delete, name='todolist_delete'),
    url(r'^todolists/(?P<list_id>[0-9]+)/tasks/$', tasks, name="tasks"),
    url(r'^todolists/(?P<list_id>[0-9]+)/tasks/create/$', task_create, name="task_create"),
    url(r'^todolists/(?P<list_id>[0-9]+)/tasks/(?P<pk>[0-9]+)/$', task_detail, name="task-detail"),
    url(r'^todolists/(?P<list_id>[0-9]+)/tasks/(?P<pk>[0-9]+)/update/$', task_update, name="task_update"),
    url(r'^todolists/(?P<list_id>[0-9]+)/tasks/(?P<pk>[0-9]+)/delete/$', task_delete, name="task_delete"),

]

handler404 = Errorfunc