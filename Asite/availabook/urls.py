from django.conf.urls import url

from . import views

app_name = 'availabook'
print app_name
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/', views.login, name='login'),
]
