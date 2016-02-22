from django.conf.urls import url

from . import views


app_name = 'cardbox'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login_view, name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^cards/$', views.cards, name='cards'),
    url(r'^card/(?P<card_id>[0-9]+)/$', views.card, name='card'),
    url(r'^collection/new/$', views.edit_collection, name='new_collection'),
    url(r'^collection/edit/(?P<collection_id>[0-9]+)/$', views.edit_collection, name='edit_collection'),
    url(r'^collection/delete/(?P<collection_id>[0-9]+)/$', views.delete_collection, name='delete_collection'),
    url(r'^collection/(?P<collection_id>[0-9]+)/$', views.collection, name='collection'),
    url(r'^collection/(?P<collection_id>[0-9]+)/add$', views.add_collection_entry, name='add_collection_entry'),
    url(r'^collection/(?P<collection_id>[0-9]+)/card/(?P<card_id>[0-9]+)/$', views.collection_card, name='collection_card'),
]
