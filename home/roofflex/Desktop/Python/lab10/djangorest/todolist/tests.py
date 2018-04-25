from rest_framework import generics, viewsets
from rest_framework import permissions
from .permissions import IsOwner
from .serializers import TaskSerializer, TasklistSerializer, TagSerializer, UserSerializer
from .models import Task, Tasklist, Tag
from django.contrib.auth.models import User
from rest_framework.generics import CreateAPIView
from django.contrib.auth import get_user_model

class CreateUserView(CreateAPIView):

    model = get_user_model()
    permission_classes = [
        permissions.AllowAny # Or anon users can't register
    ]
    serializer_class = UserSerializer

class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class TasklistCreateView(generics.ListCreateAPIView):
    serializer_class = TasklistSerializer
    queryset = Tasklist.objects.all()
    def get_queryset(self):
        queryset = Tasklist.objects.filter(owner=self.request.user)
        return queryset

    permission_classes = (
        permissions.IsAuthenticated, IsOwner)

    def perform_create(self, serializer):
        """Save the post data when creating a new bucketlist.
        :type serializer: object
        """
        serializer.save(owner=self.request.user)

class TasklistDetailsView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tasklist.objects.all()
    serializer_class = TasklistSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        IsOwner)

class TagCreateView(generics.ListCreateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class TagDetailsView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class TaskCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        queryset = Task.objects.all()
        list_id = self.kwargs.get('list_id', None)
        if list_id is not None:
            queryset = queryset.filter(tasklist_id = list_id, owner=self.request.user)
        return queryset

    permission_classes = (
        permissions.IsAuthenticated, IsOwner)

    def perform_create(self, serializer):
        list_id = self.kwargs.get('list_id', None)
        try:
            tasklist = Tasklist.objects.get(pk=list_id)
        except Tasklist.DoesNotExist:
            raise NotFound()
        serializer.save(owner=self.request.user, tasklist=tasklist)


class TaskDetailsView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        queryset = Task.objects.all()
        list_id = self.kwargs.get('list_id', None)
        if list_id is not None:
            queryset = queryset.filter(tasklist_id = list_id, owner=self.request.user)
        return queryset

    permission_classes = (
        permissions.IsAuthenticated,
        IsOwner)

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
