#from django.shortcuts import render
from django.shortcuts import render, redirect

# Create your views here.
def index(request):
    ''' render homepage'''
    print "reder index"
    return render(request, 'index.html')
