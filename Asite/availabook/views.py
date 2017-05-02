#from django.shortcuts import render
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.core import serializers

from availabook.models import User

# Create your views here.
def index(request):
    ''' render homepage'''
    print "reder index"
    print "username " + request.user.username
    return render(request, 'index.html')

def login(request, onsuccss = '/availabook/', onfail = '/availabook/'):
 	user_id = request.POST.get("id")
 	pwd = request.POST.get("psw")

 	user = User(user_id, pwd)
 	if user.authen_user():
 		user.authorize()
 		return redirect(onsucess)
 	else:
 		#alert("User Information Not exists")
 		messages.add_message(request, messages.ERROR, 'Login Failed. Try again.', 'login', True)
 		print messages
 		return redirect(onfail)

