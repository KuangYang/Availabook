#from django.shortcuts import render
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.core import serializers
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.contrib.auth import logout as auth_logout
from availabook.models import User

# Create your views here.
def index(request):
    ''' render homepage'''
    print "reder index"
    print len(request.user.username)
    print request.user.is_authenticated()
    if request.user.is_authenticated():
    	print "index"
    	return render(request, 'index.html')
    return render(request, 'homepage.html')

def login(request, onsuccss = '/availabook/home', onfail = '/availabook/'):
 	user_id = request.POST.get("id")
 	pwd = request.POST.get("psw")

 	user = User(user_id, pwd)
 	if user.authen_user():
 		user.authorize()
 		print "correct"
 		request.user.username = user_id
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

    user = User(user_id, pwd)

    if user.verify_email() == False:
        if user.check_input_passwd(pwd, pwd_a) == True:
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
            return render(request, 'index.html')
        else:
            return render(request, 'index.html')
    else:
        return render(request, 'index.html')

