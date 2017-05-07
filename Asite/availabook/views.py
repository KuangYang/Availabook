import time
import uuid
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.core import serializers
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
from availabook.models import Users, Signup, Event, get_event_by_EId, get_event_list, put_event_into_db, get_recommended_event_list
from django.middleware import csrf
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt
import sys
from boto3.session import Session
import os
import json
from django.http import JsonResponse
from forms import UploadFileForm
from boto3.session import Session
from boto.s3.connection import S3Connection
from boto.s3.key import Key
"""reload intepretor, add credential path"""
reload(sys)
sys.setdefaultencoding('UTF8')

"""import credentials from root/AppCreds"""

print "path: " + os.path.dirname(sys.path[0])
with open(os.path.dirname(sys.path[0])+ '/Asite' + '/availabook/AppCreds/AWSAcct.json','r') as AWSAcct:
    awsconf = json.loads(AWSAcct.read())
#setup the bucket
#conn = S3Connection('<aws access key>', '<aws secret key>')
conn = S3Connection(awsconf["aws_access_key_id"], awsconf["aws_secret_access_key"])
bucket = conn.get_bucket('image-availabook')

# Create your views here.
def index(request):
    ''' render the landing page'''
    for key in request.session.keys():
        del request.session[key]
    if request.user.is_authenticated():
        event_list = get_recommended_event_list(request.user.username)
        print event_list
        return render(request, 'homepage.html',{'event_list':event_list, 'logedin': True})
    else:
        return render(request, 'landing.html')


def home(request):
    event_list = get_recommended_event_list(request.user.username)
    if request.user.is_authenticated():
        print event_list
        return render(request, 'homepage.html',{'event_list':event_list, 'logedin': True})
    else:
        return render(request, 'homepage.html',{'event_list':event_list, 'logedin': False})


@csrf_exempt
def fb_login(request, onsuccess="/availabook/home", onfail="/availabook/home"):
    print "fb_login"
    user_id = str(request.POST.get("email"))
    pwd = str(request.POST.get("psw"))
    pwd_a = pwd
    firstname = request.POST.get("fn")
    lastname = request.POST.get("ln")
    age = request.POST.get("age")
    picture = request.POST.get("picture")
    print user_id, pwd, firstname, lastname, age, picture
    city = 'ny'
    zipcode = '10027'
    signup_handler = Signup(user_id, pwd, pwd_a, firstname, lastname, age, city, zipcode)
    signup_handler.add_picture(picture)
    user_db = Users(user_id, pwd)
    if user_db.verify_email() == False:
        print "account not exist"
        try:
            if not user_exists(user_id):
                    user = User(username=user_id, email=user_id)
                    user.set_password(pwd)
                    user.save()
                    authenticate(username=user_id, password=pwd)
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    auth_login(request, user)
                    signup_handler.push_to_dynamodb()
                    print str(request.user.username) + " is signed up and logged in: " + str(request.user.is_authenticated())
                    return redirect(onsuccess)
            else:
                authenticate(username=user_id, password=pwd)
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                auth_login(request, user)
                print str(request.user.username) + " is signed up and logged in: " + str(request.user.is_authenticated())
                return redirect(onsuccess)
        except Exception as e:
            print e
    else:
        print user_id, pwd
        user = authenticate(username=user_id, password=pwd)
        print user
        try:
            if user is not None:
                auth_login(request, user)
                print "redirecting"
                return redirect(onsuccess)
            else:
                print "user is none"
                return redirect(onfail)
        except Exception as e:
            print e
            return redirect(onfail)


def login(request, onsuccess="/availabook/home", onfail="/availabook/home"):
    csrf_token = csrf.get_token(request)
    user_id = request.POST.get("id")
    pwd = request.POST.get("psw")
    print csrf_token, user_id, pwd

    user = authenticate(username=user_id, password=pwd)
    if user is not None:
        auth_login(request, user)
    else:
        messages.add_message(request, messages.ERROR, 'Login Failed. Try again.', 'login', True)

    login_user = Users(user_id, pwd)
    if login_user.authen_user():
        login_user.authorize()
        print str(request.user.username) + " is logged in: " + str(request.user.is_authenticated())
        return redirect(onsuccess)
    else:
 		#alert("User Information Not exists")
        messages.add_message(request, messages.ERROR, 'Login Failed. Try again.', 'login', True)
        print messages
        return redirect(onfail)


def signup(request, onsuccess="/availabook/home", onfail="/availabook/home"):
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
    signup_handler.add_picture("https://s3.amazonaws.com/image-availabook/default")
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
                print str(request.user.username) + " is signed up and logged in: " + str(request.user.is_authenticated())
                return redirect(onsuccess)
            else:
                return redirect(onfail)
        else:
            return redirect(onfail)
    else:
        return redirect(onfail)


def user_exists(username):
    ''' check if user exists'''
    user_count = User.objects.filter(username=username).count()
    if user_count == 0:
        return False
    return True


def logout(request):
    ''' logout and redirect'''
    if request.user.is_authenticated():
        print str(request.user.username) + " is logged out!"
        auth_logout(request)
    return redirect('/availabook/home')

def profile(request):
    if request.user.is_authenticated():
        print "views profile"
        # link = Users.get_image_by_id(request.user.username)
        # print link
        item = Users.get_user_info(request.user.username)
        if item is None:
            return redirect("/availabook/home")
        link = item['picture']
        fname = item['first_name']
        lname = item['last_name']
        city = item['city']
        zipcode = item['zipcode']
        age = item['age']
        print {'fname':fname,'lname':lname,'city':city,'age':age,'zipcode':zipcode}
        return render(request, 'profile.html', {'link':link, 'logedin': True, 'fname':fname,'lname':lname,'city':city,'age':age,'zipcode':zipcode})
    else:
        return redirect("/availabook/home")


def info(request):
    print "info"
    item = Users.get_user_info(request.user.username)
    if item is None:
        return redirect("/availabook/home")
    fname = item['first_name']
    lname = item['last_name']
    city = item['city']
    zipcode = item['zipcode']
    age = item['age']
    print "info send json", {'fname':fname,'lname':lname,'city':city,'age':age,'zipcode':zipcode}
    return JsonResponse({'fname':fname,'lname':lname,'city':city,'age':age,'zipcode':zipcode})


def edit(request):
    print "edit"
    fname = request.POST.get("fname")
    lname = request.POST.get("lname")
    city = request.POST.get("city")
    age = request.POST.get("age")
    zipcode = request.POST.get("zipcode")
    uid = request.user.username
    print fname, lname, age, city, zipcode, uid
    try:
        Signup.update_to_dynamodb(uid, fname, lname, age, city, zipcode)
    except Exception as e:
        print e
    return JsonResponse({'fname':fname,'lname':lname,'city':city,'age':age,'zipcode':zipcode})


def upload(request):
    print "uploading"
    profile_link = ""
    if request.method == 'POST':
        print "posting"
        print request.POST
        #print type(request.FILES['pic'].get('content_type'))
        #print type(request.FILES['pic']['file'])
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            print 'valid form'
            k = Key(bucket)
            k.key = request.user.username
            k.set_contents_from_file(request.FILES['pic'])
            print "upload!"
            profile_link = "https://s3.amazonaws.com/image-availabook/" + request.user.username
            profile_link = profile_link.replace('@','%40')
            print profile_link
            uploaded = Users.update_image_by_id(request.user.username, profile_link)
            print uploaded
            #print k.get_contents_to_filename
        else:
            print 'invalid form'
            print form.errors
    return redirect("/availabook/profile")
    # return render(request, 'profile.html', {
    #     'link':profile_link
    # })


def post_event(request):
    if request.user.is_authenticated():
        print('post event')
        content = request.POST.get("post_content")
        print(content)
        event_date, event_time = request.POST.get("dateandtime").split("T")
        print(event_date,event_time)
        username = request.user.username
        print(username)
        timestamp = time.strftime('%Y-%m-%d %A %X %Z',time.localtime(time.time()))
        EId = str(uuid.uuid4())
        put_event_into_db(EId=EId, content=content,date=event_date,time=event_time,label='movie',fave=[], place='beijing',timestamp=timestamp,user_email=username)
        return redirect('/availabook/home')
    else:
        print "Please log in first!"
        return HttpResponse(None)


def get_fave(request):
    print('test')
    if request.user.is_authenticated():
        EId = request.POST.get("fave")
        print(EId)
        event = get_event_by_EId(EId)
        event = Event(event)
        event.add_fave(request.user.username)
        return JsonResponse({"EId" : EId, "fave_num" : event.fave_num})
    else:
        print "Please log in first!"
        return JsonResponse({"EId" : "", "fave_num" : ""})
