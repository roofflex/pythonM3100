import string
from django.shortcuts import render
from django.http import*
from django.contrib.auth import logout
from django.views.generic.edit import FormView
from django.views.generic.base import View
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from myui.forms import *
from myui.models import *
from django.core.mail import send_mail
import hashlib, datetime, random
from django.utils import timezone
from django.http import Http404



# class Error(View):
#     def get(self, request):
#         print(1)
#         return render(self.request, 'error.html')

def Errorfunc(request):
    return render(request, 'error.html')


def todolist_create(request):
    data = dict()
    if request.method == 'POST':
        form = TasklistForm(request.POST)
        if form.is_valid():
            body = request.POST.dict()
            avt = body.get('available_to').split(', ')
            if len(avt) == 1:
                avt = body.get('available_to').split(',')
            users = MyApiRequests("GET", '/users/').get_todolists()
            if users == False:
                context = {'form': form, 'errors': ['Sorry, something went wrong. Try later']}
                data['html_form'] = render_to_string('partial_list_create.html',
                                                     context,
                                                     request=request
                                                     )
                return JsonResponse(data)
            AVIAILABLE_TO = [i.get('username') for i in
                             users]
            avt3 = list(set(avt)-(set(avt) - set(AVIAILABLE_TO)))
            body.update({'available_to': avt3})
            if not body['available_to'].count(request.session.get('user')):
                body['available_to'].append(request.session.get('user'))
            del body['csrfmiddlewaretoken']
            _ = MyApiRequests(request.method, '/todolists/', headers={
                'authorization': request.session['token']}, data = body).post_todolists()
            if _ == False:
                context = {'form': form, 'errors': ['Sorry, something went wrong. Try later']}
                data['html_form'] = render_to_string('partial_list_create.html',
                                                     context,
                                                     request=request
                                                     )
                return JsonResponse(data)
            data['form_is_valid'] = True
            queryset = MyApiRequests("GET", '/todolists/', headers={
                'authorization': request.session['token']}).get_todolists()
            data['html_book_list'] = ''
            for q in queryset:
                data['html_book_list'] += render_to_string('partial_list_list.html', {
                    'tasklist': q
                })
        else:
            data['form_is_valid'] = False
    else:
        form = TasklistForm()

    context = {'form': form}
    data['html_form'] = render_to_string('partial_list_create.html',
        context,
        request=request
    )
    return JsonResponse(data)

class LoginFormView(FormView):
    def dispatch(self, request, *args, **kwargs):
        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if self.request.session.get('user') != None:
            return HttpResponseRedirect('/todolists/')
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        self.request = request
        self.args = args
        self.kwargs = kwargs
        return handler(request, *args, **kwargs)
    form_class = AuthenticationForm

    # Аналогично регистрации, только используем шаблон аутентификации.
    template_name = "registration/login.html"

    # В случае успеха перенаправим на главную.
    success_url = '/todolists/'

    def form_valid(self, form):
        # Получаем объект пользователя на основе введённых в форму данных.
        username = password = ''
        username = self.request.POST.get('username')
        password = self.request.POST.get('password')
        queryset = MyApiRequests("POST", "",
                                 data={'username':username, 'password':password}).get_token()  # , auth = (username, password)
        if not queryset == {'non_field_errors': ['Unable to log in with provided credentials.']}:
            self.request.session['token'] = 'Token ' + str(queryset.get('token'))
            self.request.session['user'] = username
        #    self.user = authenticate(username=username, password = password)
            # Выполняем аутентификацию пользователя.
       ##         if self.user.is_active:
       #             loginn(self.request, self.user)
            return super(LoginFormView, self).form_valid(form)
        else:
            data = {}
            data['error_message'] = 'Your username and password didn\'t match. Please try again.'
            return JsonResponse(data)

class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect("/login/")

class RegisterFormView(FormView):
    def dispatch(self, request, *args, **kwargs):
        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if self.request.session.get('user') != None:
            return HttpResponse('/todolists/')
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        self.request = request
        self.args = args
        self.kwargs = kwargs
        return handler(request, *args, **kwargs)
    form_class = RegistrationForm

    # Ссылка, на которую будет перенаправляться пользователь в случае успешной регистрации.
    # В данном случае указана ссылка на страницу входа для зарегистрированных пользователей.
    success_url = "/login/"

    # Шаблон, который будет использоваться при отображении представления.
    template_name = "register.html"
    def form_valid(self, form):
        # Создаём пользователя, если данные в форму были введены корректно.
        if validate_username(self.request).content == b'{"is_taken1": 0, "is_taken2": 0}':
            d1 = self.request.POST.dict()
            d1.update({"password": d1['password1']})
            del d1['csrfmiddlewaretoken']
            del d1['password1']
            del d1['password2']
            salt_bytes = (string.ascii_letters + string.digits).encode('ascii')
            salt = bytes([random.choice(salt_bytes) for _ in range(5)])
            activation_key = hashlib.sha1(salt + d1['email'].encode('utf8')).hexdigest()
            key_expires = datetime.datetime.today() + datetime.timedelta(2)
            MyApiRequests("POST", self.request.path_info, data=d1).create_user()
            new_profile = UserProfile(user=d1['username'], activation_key=activation_key,
                                      key_expires=key_expires)
            new_profile.save()
            # Send email with activation key
            email_subject = 'Подтверждение регистрации'
            email_body = "Hey %s, thanks for signing up. To activate your account, click this link within 48hours http://127.0.0.1:8001/accounts/confirm/%s"\
                         % (d1['username'], activation_key)
            send_mail(email_subject, email_body, 'katherine.andrhn2@gmail.com',
                      [d1['email']], fail_silently=False)
          #  return HttpResponseRedirect('/accounts/register_success')
            return HttpResponseRedirect("/login/")
            # Вызываем метод базового класса
        return super(RegisterFormView, self).form_valid(form)

def register_confirm(request, activation_key):
    #check if user is already logged in and if he is redirect him to some other url, e.g. home
    if request.session.get('user'):
        HttpResponseRedirect('/todolists/')
    # check if there is UserProfile which matches the activation key (if not then display 404)
    user_profile = get_object_or_404(UserProfile, activation_key=activation_key)
    #check if the activation key has expired, if it hase then render confirm_expired.html
    if user_profile.key_expires < timezone.now():
        return HttpResponse("<p>Activation key has expired.</p>")
    #if the key hasn't expired save user and set him as active and render some template to confirm activation
    user = user_profile.user
    users = MyApiRequests("GET", '/users/').get_todolists()
    if users == False:
        context = {'form': form, 'errors': ['Sorry, something went wrong. Try later']}
        data['html_form'] = render_to_string('partial_list_create.html',
                                             context,
                                             request=request
                                             )
        return JsonResponse(data)
    for i in users:
        if i.get('username') == user:
            i.update({'is_active' : 1})
            id = str(i.get('id'))
            data = i
            break
    MyApiRequests("PUT", '/users/' + id + '/', data = data).activate_user()
  #  return render_to_response('user_profile/confirm.html')
    return HttpResponseRedirect("/login/")

def validate_username(request):
    username = request.GET.get('username', None)
    email = request.GET.get('email', None)
    data1 =MyApiRequests("GET", '/users/').get_todolists()
    if data1 == False:
        context = {'form': form, 'errors': ['Sorry, something went wrong. Try later']}
        data['html_form'] = render_to_string('partial_list_create.html',
                                             context,
                                             request=request
                                             )
        return JsonResponse(data)
    data = {
        'is_taken1': [i.get('username') for i in data1.count(username)],
        'is_taken2': [i.get('email') for i in data1.count(email)]
    }
    if data['is_taken1']:
        data['error_message1'] = 'A user with this username already exists.'
    if data['is_taken2']:
        data['error_message2'] = 'This email is already taken.'
    return JsonResponse(data)

def todolists(request):
    queryset = None
    if request.session.get('user'):
        request.user = request.session['user']
        queryset = MyApiRequests("GET", request.path_info, headers={
            'authorization': request.session['token']}).get_todolists()
        if queryset == False:
            context = {'form': form, 'errors': ['Sorry, something went wrong. Try later']}
            data['html_form'] = render_to_string('partial_list_create.html',
                                                 context,
                                                 request=request
                                                 )
            return JsonResponse(data)

    return render(request, 'todolists.html', {'p': queryset})



def todolist_detail(request, pk):
    queryset = None
    pk = None
    if request.session.get('user'):
        request.user = request.session['user']
        queryset = MyApiRequests("GET", request.path_info, headers={
            'authorization': request.session['token']}).get_todolists()
        if queryset == False:
            context = {'form': form, 'errors': ['Sorry, something went wrong. Try later']}
            data['html_form'] = render_to_string('partial_list_create.html',
                                                 context,
                                                 request=request
                                                 )
            return JsonResponse(data)
    if queryset == {'detail': 'Not found.'}:
        queryset = None
    return render(request, "todolist_detail.html", {'tasklist': queryset, 'pk': pk})

def todolist_update(request, pk):
    queryset = MyApiRequests("GET", request.path_info[:-7], headers={
        'authorization': request.session['token']}).get_todolists()
    if queryset == False:
        context = {'form': form, 'errors': ['Sorry, something went wrong. Try later']}
        data['html_form'] = render_to_string('partial_list_create.html',
                                             context,
                                             request=request
                                             )
        return JsonResponse(data)
    tagg = queryset.get('available_to')[0]
    for tag in queryset.get('available_to')[1:]:
        tagg += ', ' + tag
    queryset.update({'available_to': tagg})
    if request.method == 'POST':
        form = TasklistForm(request.POST)
    else:
        form = TasklistForm(initial=queryset)
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            body = request.POST.dict()
            avt = body.get('available_to').split(', ')
            if len(avt) == 1:
                avt = body.get('available_to').split(',')

            data1 = MyApiRequests("GET", '/users/').get_todolists()
            if data1 == False:
                context = {'form': form, 'errors': ['Sorry, something went wrong. Try later']}
                data['html_form'] = render_to_string('partial_list_create.html',
                                                     context,
                                                     request=request
                                                     )
                return JsonResponse(data)
            AVIAILABLE_TO = [i.get('username') for i in data1
                             ]
            avt3 = list(set(avt) - (set(avt) - set(AVIAILABLE_TO)))
            body.update({'available_to': avt3})
            if not body['available_to'].count(request.session.get('user')):
                body['available_to'].append(request.session.get('user'))
            del body['csrfmiddlewaretoken']
            MyApiRequests("PUT", '/todolists/' + str(pk) + '/', headers={
              'authorization': request.session['token']}, data=body).put_todolists()
            data['form_is_valid'] = True
            queryset = MyApiRequests("GET", '/todolists/', headers={
                'authorization': request.session['token']}).get_todolists()
            if queryset == False:
                context = {'form': form, 'errors': ['Sorry, something went wrong. Try later']}
                data['html_form'] = render_to_string('partial_list_create.html',
                                                     context,
                                                     request=request
                                                     )
                return JsonResponse(data)
            data['html_book_list'] = ''
            for q in queryset:
                data['html_book_list'] += render_to_string('partial_list_list.html', {
                    'tasklist': q
                })
        else:
            data['form_is_valid'] = False
    context = {'form': form, 'id':pk}
    data['html_form'] = render_to_string('partial_list_update.html', context, request)
    return JsonResponse(data)

def todolist_delete(request, pk):
    data = dict()
    queryset = MyApiRequests("GET", '/todolists/' + str(pk) + '/', headers={
        'authorization': request.session['token']}).get_todolists()
    if queryset == False:
        context = {'form': form, 'errors': ['Sorry, something went wrong. Try later']}
        data['html_form'] = render_to_string('partial_list_create.html',
                                             context,
                                             request=request
                                             )
        return JsonResponse(data)
    if request.method == 'POST':
        MyApiRequests("DELETE", '/todolists/' + str(pk) + '/', headers={
          'authorization': request.session['token']}, data={'name': request.POST.get('name')}).delete_todolists()
        data['form_is_valid'] = True  # This is just to play along with the existing code
        queryset = MyApiRequests("GET", '/todolists/', headers={
            'authorization': request.session['token']}).get_todolists()
        if queryset == False:
            context = {'form': form, 'errors': ['Sorry, something went wrong. Try later']}
            data['html_form'] = render_to_string('partial_list_create.html',
                                                 context,
                                                 request=request
                                                 )
            return JsonResponse(data)
        data['html_book_list'] = ''
        for q in queryset:
            data['html_book_list'] += render_to_string('partial_list_list.html', {
                'tasklist': q
            })
    else:
        context = {'tasklist': queryset, 'id':pk, 'todolist_name': queryset['name']}
        data['html_form'] = render_to_string('partial_list_delete.html',
            context,
            request=request,
        )
    return JsonResponse(data)

def tasks(request, list_id):
    queryset = None
    if request.session.get('user'):
        request.user = request.session['user']
        queryset = MyApiRequests("GET", request.path_info, headers={
            'authorization': request.session['token']}).get_todolists()
        if queryset == False:
            context = {'form': form, 'errors': ['Sorry, something went wrong. Try later']}
            data['html_form'] = render_to_string('partial_list_create.html',
                                                 context,
                                                 request=request
                                                 )
            return JsonResponse(data)
    return render(request, 'tasks.html', {'p': queryset, 'list_id':list_id})

def task_create(request, list_id):
    data = dict()
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            body = request.POST.dict()
          ##  if not body.get('available_to'):
          ##      body.update({'available_to':[]})
          #  body.update({'available_to': [body.get('available_to')]}) #???
          #  if not body['available_to'].count(request.session.get('user')):
          #      body['available_to'].append(request.session.get('user'))
            queryset22 = MyApiRequests("GET", "/todolists/"+list_id+"/", headers={
                'authorization': request.session['token']}).get_todolists().get('available_to')
            del body['csrfmiddlewaretoken']
            tags = body.get('tags').split(', ')
            if len(tags)==1:
                tags = body.get('tags').split(',')
            if tags != ['']:
                TAGS = [i.get('name') for i in MyApiRequests("GET", '/tags/').get_todolists()]
                tag3 = list(set(tags) - set(TAGS))
                for t in tag3:
                    MyApiRequests(request.method, '/tags/', headers={
                        'authorization': request.session['token']}, data={'name':t}).post_todolists()
            else:
                tags = []
            body.update({'tags': tags, 'available_to':queryset22})
            queryset = MyApiRequests(request.method, '/todolists/' + str(list_id) + '/tasks/', headers={
                'authorization': request.session['token']}, data = body).post_todolists()
            data['form_is_valid'] = True
            queryset = MyApiRequests("GET", '/todolists/' + str(list_id) + '/tasks/', headers={
                'authorization': request.session['token']}).get_todolists()
            data['html_book_list'] = ''
            for q in queryset:
                data['html_book_list'] += render_to_string('partial_tasks_list.html', {
                    'tasks': q, 'list_id': list_id
                })
        else:
            data['form_is_valid'] = False
    else:
        form = TaskForm()

    context = {'form': form, 'list_id':list_id}
    data['html_form'] = render_to_string('partial_task_create.html',
        context,
        request=request
    )
    return JsonResponse(data)

def task_detail(request, list_id, pk):
    queryset = None
    pk = None
    if request.session.get('user'):
        request.user = request.session['user']
        queryset = MyApiRequests("GET", request.path_info, headers={
            'authorization': request.session['token']}).get_todolists()
        if queryset == False:
            context = {'form': form, 'errors': ['Sorry, something went wrong. Try later']}
            data['html_form'] = render_to_string('partial_list_create.html',
                                                 context,
                                                 request=request
                                                 )
            return JsonResponse(data)
    if queryset == {'detail': 'Not found.'}:
        queryset = None
    return render(request, "task_detail.html", {'tasklist': queryset, 'pk': pk})

def task_update(request, list_id, pk):
    queryset = MyApiRequests("GET", request.path_info[:-7], headers={
        'authorization': request.session['token']}).get_todolists()
    if queryset == False:
        context = {'form': form, 'errors': ['Sorry, something went wrong. Try later']}
        data['html_form'] = render_to_string('partial_list_create.html',
                                             context,
                                             request=request
                                             )
        return JsonResponse(data)
    tagg=queryset.get('tags')[0]
    for tag in queryset.get('tags')[1:]:
        tagg+=', ' + tag
    queryset.update({'tags': tagg})
    if request.method == 'POST':
        form = TaskForm(request.POST)
    else:
        form = TaskForm(initial=queryset)
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            body = request.POST.dict()
          #  if not body.get('available_to'):
          #      body.update({'available_to': []})
          #  body.update({'available_to': [body.get('available_to')]})  # ???
          #  if not body['available_to'].count(request.session.get('user')):
          #      body['available_to'].append(request.session.get('user'))
            tags = body.get('tags').split(', ')
            if len(tags) == 1:
                tags = body.get('tags').split(',')
            TAGS = [i.get('name') for i in MyApiRequests("GET", '/tags/').get_todolists()]
            tag3 = list(set(tags) - set(TAGS))
            for t in tag3:
                MyApiRequests(request.method, '/tags/', headers={
                    'authorization': request.session['token']}, data={'name': t}).post_todolists()
            body.update({'tags': tags})
            del body['csrfmiddlewaretoken']
            MyApiRequests("PUT", '/todolists/' + str(list_id) + '/tasks/' + str(pk) + '/', headers={
              'authorization': request.session['token']}, data=body).put_todolists()
            data['form_is_valid'] = True
            queryset = MyApiRequests("GET", '/todolists/' + str(list_id) + '/tasks/', headers={
                'authorization': request.session['token']}).get_todolists()
            if queryset == False:
                context = {'form': form, 'errors': ['Sorry, something went wrong. Try later']}
                data['html_form'] = render_to_string('partial_list_create.html',
                                                     context,
                                                     request=request
                                                     )
                return JsonResponse(data)
            data['html_book_list'] = ''
            for q in queryset:
                data['html_book_list'] += render_to_string('partial_tasks_list.html', {
                    'tasks': q, 'list_id':list_id
                })
        else:
            data['form_is_valid'] = False
    context = {'form': form, 'list_id':list_id, 'id':pk}
    data['html_form'] = render_to_string('partial_task_update.html', context, request)
    return JsonResponse(data)

def task_delete(request, list_id, pk):
    data = dict()
    queryset = MyApiRequests("GET", '/todolists/' + str(list_id) + '/tasks/' + str(pk) + '/', headers={
        'authorization': request.session['token']}).get_todolists()
    if request.method == 'POST':
        MyApiRequests("DELETE", '/todolists/' + str(list_id) + '/tasks/' + str(pk) + '/', headers={
          'authorization': request.session['token']}, data={'name': request.POST.get('name')}).delete_todolists()
        data['form_is_valid'] = True  # This is just to play along with the existing code
        queryset = MyApiRequests("GET", '/todolists/' + str(list_id) + '/tasks/', headers={
            'authorization': request.session['token']}).get_todolists()
        data['html_book_list'] = ''
        for q in queryset:
            data['html_book_list'] += render_to_string('partial_tasks_list.html', {
                 'tasks': q, 'list_id': list_id
        })
    else:
        context = {'tasks': queryset, 'list_id':list_id, 'id':pk, 'task_name': queryset['name']}
        data['html_form'] = render_to_string('partial_task_delete.html',
            context,
            request=request,
        )
    return JsonResponse(data)