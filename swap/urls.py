from django.conf.urls import include, url

from . import views

urlpatterns = [
  url(r'^$', views.bookings),
  url(r'^bookings/$', views.bookings, name='bookings_list'),
  url(r'^resources/$', views.ResourceList.as_view(), name='resource_list'),
  url(r'^request/(?P<resource>[0-9]+)/$', views.request_resource, name='request_resource'),
  url(r'^approve/(?P<req>[0-9]+)/$', views.approve_request, name='approve_request'),
]

