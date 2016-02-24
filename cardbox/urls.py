# django-cardbox -- A collection manager for Magic: The Gathering
# Copyright (C) 2016 Benedikt Rascher-Friesenhausen
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
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
