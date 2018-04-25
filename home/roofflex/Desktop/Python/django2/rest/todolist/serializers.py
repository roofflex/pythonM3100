from rest_framework import serializers
from .models import Task,Tasklist,Tag, User
from django.core.mail import send_mail
import random
class UserSerializer(serializers.ModelSerializer):
    vipusers = serializers.PrimaryKeyRelatedField(many=True, queryset=Task.objects.all())
    view_users = serializers.PrimaryKeyRelatedField(many=True, queryset=Task.objects.all())
    class Meta:
        model = 'auth.User'
        fields = ('id', 'username', 'vipusers', 'view_users', )

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name','task_set')
        read_only_fields = ('task_set',)

class TaskSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(many=True, slug_field='name', queryset=Tag.objects.all())

    class Meta:
        model = Task
        fields = ('id', 'name', 'description', 'completed', 'date_created', 'date_modified', 'due_date', 'priority','tags')
        read_only_fields = ('date_created', 'date_modified',)



class TasklistSerializer(serializers.ModelSerializer):
    tasks = serializers.StringRelatedField(many=True)

    class Meta:
        model = Tasklist
        fields = ('name', 'tasks', 'id','vipusers', 'view_users' )
        read_only_fields = ('owner',)



class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email',  )
        write_only_fields = ('password', )
        read_only_fields = ('id', )

    def create(self, validated_data):
        activation_key=str(random.randint(10**9, 10**10-1))
        email=validated_data['email']
        user = User.objects.create(
            username=validated_data['username'],
            email=email,
            is_active=False,
        )
        t = Token.objects.create(user=user)
        user.set_password(validated_data['password'])
        user.save()
        new_profile = UserProfile(user=user, activation_key=activation_key)
        new_profile.save()
        email_subject = 'Confirmation'
        email_body = 'Hey! Follow this link: http://127.0.0.1:8000/activate/{}'.format(activation_key)
        send_mail(email_subject, email_body, 'prikladnaya16@yandex.ru', [email], fail_silently=False)
        return user