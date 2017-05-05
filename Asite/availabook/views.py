#from django.shortcuts import render
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.core import serializers
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
from availabook.models import Users, Signup, Event, get_event_by_EId, get_event_list,put_event_into_db,get_recommended_event_list
from django.http import JsonResponse, HttpResponse
from django.core  import serializers
import time
import uuid
import json
from django.views.decorators.csrf import ensure_csrf_cookie
@ensure_csrf_cookie


# Create your views here.
def index(request):
    ''' render landing page'''
    if request.user.is_authenticated():
        event_list = get_recommended_event_list(request.user.username)
        print event_list
        return render(request, 'homepage.html',{'event_list':event_list, 'logedin': True})
    return render(request, 'landing.html')


def visitor(request):
    event_list = get_recommended_event_list(request.user.username)
    if request.user.is_authenticated():
        print event_list
        return render(request, 'homepage.html',{'event_list':event_list, 'logedin': True})
    return render(request, 'homepage.html',{'event_list':event_list, 'logedin': False})


def home(request):
    event_list = get_recommended_event_list(request.user.username)
    if request.user.username:
        print event_list
        return render(request, 'homepage.html',{'event_list':event_list, 'logedin': True})
    return render(request, 'homepage.html',{'event_list':event_list, 'logedin': False})


def login(request, onsuccess = '/availabook/home', onfail = '/availabook/visitor'):
    user_id = request.POST.get("id")
    pwd = request.POST.get("psw")
    print user_id, pwd

    user = authenticate(username=user_id, password=pwd)
    if user is not None:
        auth_login(request, user)
    else:
        messages.add_message(request, messages.ERROR, 'Login Failed. Try again.', 'login', True)

    login_user = Users(user_id, pwd)
    if login_user.authen_user():
        login_user.authorize()
        print "correct"
        print request.user.username
        print request.user.is_authenticated()
        return redirect(onsuccess)
    else:
 		#alert("User Information Not exists")
        messages.add_message(request, messages.ERROR, 'Login Failed. Try again.', 'login', True)
        print messages
        return redirect(onfail)


def signup(request):
    user_id = request.POST.get("email")
    pwd = request.POST.get("psw")
    pwd_a = request.POST.get("psw_a")
    firstname = request.POST.get("fn")
    lastname = request.POST.get("ln")
    age = request.POST.get("age")
    city = request.POST.get("city")
    zipcode = request.POST.get("zipcode")
    print user_id, pwd, pwd_a, firstname, lastname, age, city, zipcode

    signup_handler = Signup(user_id, pwd, pwd_a, firstname, lastname, age, city, zipcode)
    event_list = get_recommended_event_list(user_id)
    user_db = Users(user_id, pwd)

    if user_db.verify_email() == False:
        if pwd == pwd_a:
            if not user_exists(user_id):
                signup_handler.push_to_dynamodb()
                user = User(username=user_id, email=user_id)
                user.set_password(pwd)
                user.save()
                authenticate(username=user_id, password=pwd)
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                auth_login(request, user)
                return render(request, 'homepage.html',{'event_list':event_list, 'logedin': True})
            else:
                return render(request, 'homepage.html',{'event_list':event_list, 'logedin': False})
        else:
            messages.add_message(request, messages.INFO, 'Input passwprds inconsistent! Try again', 'signup', True)
            return render(request, 'homepage.html',{'event_list':event_list, 'logedin': False})
    else:
        return render(request, 'homepage.html',{'event_list':event_list, 'logedin': False})


def user_exists(username):
    ''' check if user exists'''
    user_count = User.objects.filter(username=username).count()
    if user_count == 0:
        return False
    return True


def logout(request):
    ''' logout and redirect'''
    if request.user.is_authenticated():
        print request.user.username
        auth_logout(request)
    return redirect('/availabook/home')


def profile(request):
    return render(request, 'profile.html')


def post_event(request):
    print('post event')
    content = request.POST.get("content")
    print(content)
    event_date, event_time = request.POST.get("meeting").split("T")
    print(event_date,event_time)
    username = request.user.username
    print(username)
    timestamp = time.strftime('%Y-%m-%d %A %X %Z',time.localtime(time.time()))
    EId = str(uuid.uuid4())
    put_event_into_db(EId=EId, content=content,date=event_date,time=event_time,label='movie',fave=[], place='beijing',timestamp=timestamp,user_email=username)
    return redirect('/availabook/home')


def get_fave(request):
    EId = request.POST.get("fave")
    print(EId)
    event = get_event_by_EId(EId)
    event = Event(event)
    event.add_fave(request.user.username)
    return redirect('/availabook/home')
