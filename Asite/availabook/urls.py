from django.conf.urls import url

from . import views

app_name = 'availabook'
urlpatterns = [
    url(r'^$', views.index, name='index'),
]
