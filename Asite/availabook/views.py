#from django.shortcuts import render
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.core import serializers
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
from availabook.models import Users, Signup, Event, get_event_list
import time
import uuid



# Create your views here.
def index(request):
    ''' render homepage'''
    auth_logout(request)
    return render(request, 'homepage.html')
    event_list = get_event_list()
    return render(request, 'index.html',{'event_list':event_list})

def home(request):
    event_list = get_event_list()
    if request.user.username:
		return render(request, 'index.html',{'event_list':event_list})
    print request.user.is_authenticated()
    print request.user.username
    return redirect('/availabook/')

def login(request, onsuccss = '/availabook/home', onfail = '/availabook/'):
 	user_id = request.POST.get("id")
 	pwd = request.POST.get("psw")

 	user = authenticate(username=user_id, password=pwd)
 	if user is not None:
 		auth_login(request, user)
 	else:
 		messages.add_message(request, messages.ERROR, 'Login Failed. Try again.', 'login', True)

 	user = Users(user_id, pwd)
 	if user.authen_user():
 		user.authorize()
 		print "correct"
 		print request.user.username
 		print request.user.is_authenticated()
 		return redirect(onsuccss)
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

    signup_handler = Signup(user_id, pwd, pwd_a, firstname, lastname, age, city, zipcode)

    if pwd == pwd_a:
        if not user_exists(user_id):
            signup_handler.push_to_dynamodb()
            user = User(username=user_id, email=user_id)
            user.set_password(pwd)
            user.save()
            authenticate(username=user_id, password=pwd)
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            auth_login(request, user)
        else:
            messages.add_message(request, messages.INFO, 'User exists. Try again', 'signup', True)
    else:
        messages.add_message(request, messages.INFO, 'Input passwprds inconsistent! Try again', 'signup', True)

    user = Users(user_id, pwd)
    event_list = get_event_list()
    if user.verify_email() == False:
        if pwd == pwd_a:
            Item={
                'email': user_id,
                'age': age,
                'city': city,
                'first_name': firstname,
                'last_name': lastname,
                'password': pwd,
                'zipcode': zipcode,
            }
            try:
                user.push_to_dynamodb(Item)
            except Exception as e:
                print e
            return render(request, 'index.html',{'event_list':event_list})
        else:
            return render(request, 'index.html')
    else:
        return render(request, 'index.html')

def user_exists(username):
    ''' check if user exists'''
    user_count = User.objects.filter(username=username).count()
    if user_count == 0:
        return False
    return True


def logout(request):
    ''' logout and redirect'''
    if request.user.username:
        auth_logout(request)
        return redirect('/availabook/')
    else:
        return redirect('/availabook/')


def post_event(request):
    print('post event')
    content = request.POST.get("content")
    print(content)
    event_date, event_time = request.POST.get("meeting").split("T")
    print(event_date,event_time)
    ###### EId to be modify
    event = Event(EId=str(uuid.uuid4()),content=content,date=event_date,time=event_time,label='movie',like=[],place='beijing',)
    timestamp = time.strftime('%Y-%m-%d %A %X %Z',time.localtime(time.time()))  

    event.put_into_db(timestamp =timestamp,user_email='xx@aa.com')
    event_list = get_event_list()
    return render(request,'index.html',{'event_list':event_list})
