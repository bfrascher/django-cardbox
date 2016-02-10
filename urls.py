from django.conf.urls import url

from . import views


app_name = 'polls'
urlpatterns = [
    # ex: /tccm/
    url(r'^$', views.index, name='index'),
]
