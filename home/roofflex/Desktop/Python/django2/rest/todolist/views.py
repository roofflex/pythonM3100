
from django.views.generic.base import View
from rest_framework import generics
from rest_framework.exceptions import NotFound


from .serializers import TaskSerializer,TasklistSerializer,TagSerializer
from .models import Task,Tasklist,Tag
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic.edit import FormView
from django.contrib.auth import login,logout
from django.http import HttpResponse,HttpResponseRedirect

class TagCreateView(generics.ListCreateAPIView):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()

    def get_queryset(self):
        tags = Tag.objects.all().filter()
        #tag = Tag.objects.get(pk=self.kwargs.get('pk', None))
        return tags


class TagDetailView(generics.RetrieveUpdateDestroyAPIView):
    #queryset = Tag.objects.all()
    serializer_class = TagSerializer
    def get_queryset(self):
        queryset = Tag.objects.all()
        task_id = self.kwargs.get('pk', None)
        if task_id is not None:
            queryset = queryset.filter(pk=task_id )

        return queryset


class TasklistCreateView(generics.ListCreateAPIView):
    serializer_class = TasklistSerializer
    def get_queryset(self):
        queryset = Tasklist.objects.all()
        queryset = queryset.filter(owner=self.request.user.id,  )
        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user, )

class TasklistDetailsView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TasklistSerializer
    def get_queryset(self):
        taskList_id = self.kwargs.get('pk', None)
        try:
            vipusers = Tasklist.objects.get(vipusers = self.request.user.id, id = taskList_id)
            queryset = Tasklist.objects.filter( id=taskList_id).all()
            return queryset
        except:
            try:
                view_user = Tasklist.objects.get(view_users=self.request.user.id, id=taskList_id)
                queryset = Tasklist.objects.filter(id=taskList_id).all()
                return queryset
            except:
                if self.request.user.is_authenticated():
                    if taskList_id is not None:
                        queryset =  Tasklist.objects.filter(owner=self.request.user, id=taskList_id).all()
                        return queryset

    def perform_update(self, serializer):
        def if_view_user(tasklist_id):
            try:
                _ = Tasklist.objects.get(view_users=self.request.user, id=tasklist_id)
                return True
            except:
                print(1)
                return False
        if self.request.user.is_authenticated():
            taskList_id = self.kwargs.get('pk', None)
            if not if_view_user(taskList_id):
                instance = serializer.save()

class TaskCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):

        return Task.objects.filter(tasklist__owner=self.request.user, tasklist_id=self.kwargs['list_id'])


    def perform_create(self, serializer):
        list_id = self.kwargs.get('list_id', None)
        try:
            tasklist = Tasklist.objects.get(id=list_id, owner=self.request.user)
        except Tasklist.DoesNotExist:
            raise NotFound('=(')
        serializer.save(tasklist=tasklist)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        queryset = Task.objects.all()
        task_id = self.kwargs.get('pk', None)
        if self.request.user.is_authenticated():
            if task_id is not None:
                queryset = queryset.filter(pk=task_id)
        return queryset



class RegisterFormView(FormView):
    form_class = UserCreationForm
    success_url = '/todolists/login'


    template_name = "register.html"

    def form_valid(self, form):
        form.save()
        self.request.session["username"] = self.request.POST['username']
        return super(RegisterFormView, self).form_valid(form)



class LoginFormView(FormView):
    form_class = AuthenticationForm
    template_name = "login.html"

    def form_valid(self, form):
        self.user = form.get_user()
        login(self.request, self.user)
        self.request.session["username"] = self.request.POST['username']
        return super(LoginFormView, self).form_valid(form)
    success_url = '/todolists/'

class LogoutView(View):
    def get(self, request):
        # Выполняем выход для пользователя, запросившего данное представление.
        logout(request)
        # После чего, перенаправляем пользователя на главную страницу.
        return HttpResponseRedirect('/todolists/')
