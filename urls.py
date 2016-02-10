from django.conf.urls import url

from . import views


app_name = 'polls'
urlpatterns = [
    # ex: /tccm/
    url(r'^$', views.IndexView.as_view(), name='index'),
]
