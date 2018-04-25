from __future__ import unicode_literals
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from .queryset import MyApiRequests
class TasklistForm(forms.forms.Form):
    name = forms.CharField(max_length=100)
  #  AVIAILABLE_TO = [(i.get('username'), i.get('username')) for i in MyApiRequests("GET", '/users/').get_todolists()]
  #  available_to = forms.MultipleChoiceField(choices=AVIAILABLE_TO, required=False)
    available_to = forms.CharField(help_text='Введите пользователей через запятую.', max_length=200, required=False)
    class Meta:
        fields = (
        'id', 'owner', 'available_to', 'name')
        read_only_fields = ('owner')

class TaskForm(forms.forms.Form):
    name = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea,required = False)
    completed = forms.BooleanField(required=False)
    due_date = forms.DateField(help_text='YYYY-MM-DD', required = False)
  #  TAGS = [(i.get('name'),i.get('name')) for i in MyApiRequests("GET", '/tags/').get_todolists()]
  #  tags = forms.MultipleChoiceField(choices=TAGS, required = False)
    tags = forms.CharField(help_text='Введите теги через запятую.', max_length=200, required = False)
    PRIORITY = (
        ('h', 'High'),
        ('m', 'Medium'),
        ('l', 'Low'),
        ('n', 'None')
    )
    priority = forms.ChoiceField(required = False, choices=PRIORITY, initial='n')

    class Meta:
        fields = (
        'id', 'owner', 'name', 'description', 'completed', 'due_date', 'tags',
        'priority')
        read_only_fields = ('date_created', 'date_modified')

class UserCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
#   email = forms.EmailField()
    password1 = forms.CharField(label=_("Password"),
        widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"),
        widget=forms.PasswordInput,
        help_text=_("Enter the same password as above, for verification."))

    class Meta:
        model = User
        fields = ("username",)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Электронный адрес'}))
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'password1', 'password2')

class AuthenticationForm(forms.Form):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    """
    username = forms.CharField(max_length=254)
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)


