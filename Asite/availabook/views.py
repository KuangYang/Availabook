#from django.shortcuts import render
from django.shortcuts import render, redirect
from django.http import HttpResponse

from availabook.models import User

# Create your views here.
def index(request):
    ''' render homepage'''
    print "reder index"
    return render(request, 'index.html')

def login(request):
 	user_id = request.POST.get("id")
 	pwd = request.POST.get("psw")

 	user = User(user_id, psw)
 	if user.authen_user():
 		user.authorize()
 		return render(request, 'index.html')
 	else:
 		alert("User Information Not exists")
 		return render(request, 'index.html')

