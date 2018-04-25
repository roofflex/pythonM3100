from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from .views import TaskCreateView, TaskDetailView,TagCreateView
from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from .views import TasklistCreateView, TasklistDetailsView, TaskCreateView, TaskDetailView,TagDetailView
from rest_framework.authtoken.views import obtain_auth_token
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = {

    url(r'^todolists/$', TasklistCreateView.as_view(), name="lists"),
    url(r'^todolists/(?P<pk>[0-9]+)/$', TasklistDetailsView.as_view(), name="list-detail"),
    url(r'^todolists/(?P<list_id>[0-9]+)/tasks/$', TaskCreateView.as_view(), name="tasks"),
    url(r'^todolists/(?P<list_id>[0-9]+)/tasks/(?P<pk>[0-9]+)', TaskDetailView.as_view(), name="task-detail"),
    url(r'^todolists/tags', TagCreateView.as_view(), name="tags"),
    url(r'^todolists/(?P<pk>[0-9]+)/tagsview', TagDetailView.as_view(), name="tagsv"),
    url(r'^todolists/register/$', views.RegisterFormView.as_view()),
    url(r'^todolists/login/$', views.LoginFormView.as_view()),
    url(r'^todolists/logout/$', views.LogoutView.as_view()),
}

urlpatterns = format_suffix_patterns(urlpatterns)