from django.conf.urls import url

from . import views


app_name = 'cardbox'
urlpatterns = [
    # ex: /cardbox!/
    url(r'^$', views.index, name='index'),
]
