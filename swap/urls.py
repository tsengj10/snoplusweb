from django.conf.urls import include, url

from . import views

urlpatterns = [
  url(r'^$', views.bookings, name='bookings'),
  url(r'^bookings/$', views.bookings_json, name='bookings_json'),
  url(r'^resources/$', views.ResourceList.as_view(), name='resource_list'),
]

