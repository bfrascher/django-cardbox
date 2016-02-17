from django.conf.urls import url

from . import views


app_name = 'cardbox'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/', views.login_view, name='login'),
    url(r'^logout/', views.logout_view, name='logout'),
    url(r'^collection/', views.collection, name='collection'),
]
