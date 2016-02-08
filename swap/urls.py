from django.conf.urls import include, url

from . import views

urlpatterns = [
  url(r'^$', views.bookings),
  url(r'^bookings/$', views.bookings, name='bookings'),
  url(r'^resources/$', views.ResourceList.as_view(), name='resource_list'),
]

