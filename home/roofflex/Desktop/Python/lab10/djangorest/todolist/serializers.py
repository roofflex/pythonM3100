from rest_framework import serializers, generics
from django.contrib.auth.models import User
from .models import Task, Tasklist, Tag
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class UserSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user = UserModel.objects.create(
            username=validated_data['username'],
            email = validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            is_active=False
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

       # user = UserModel.objects.get
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'username', 'password', 'is_active')
        write_only_fields = ('password',)
        read_only_fields = ('id',)

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name')

class TaskSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    available_to = serializers.SlugRelatedField(many=True, slug_field='username', queryset=User.objects.all())
    tags = serializers.SlugRelatedField(many=True, slug_field='name', queryset=Tag.objects.all())
    class Meta:
        model = Task
        fields = ('id', 'owner', 'name', 'description', 'completed', 'date_created', 'date_modified', 'due_date', 'tags', 'priority', 'available_to')
        read_only_fields = ('date_created', 'date_modified')

class TasklistSerializer(serializers.ModelSerializer):
    tasks = serializers.StringRelatedField(many=True, read_only=True)
    owner = serializers.ReadOnlyField(source='owner.username')
    available_to = serializers.SlugRelatedField(many=True, slug_field='username', queryset=User.objects.all())
    class Meta:
        model = Tasklist
        fields = ('id', 'name', 'owner', 'available_to', 'tasks')
