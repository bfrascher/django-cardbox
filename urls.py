from django.conf.urls import url

from . import views


app_name = 'mtgcardbox'
urlpatterns = [
    # ex: /mtgcardbox!/
    url(r'^$', views.index, name='index'),
]
