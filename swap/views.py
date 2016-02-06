from django.views.generic.list import ListView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render

from .models import Resource, Approver, Booking

# Create your views here.

class ResourceList(ListView):
  model = Resource

# bookings

def bookings_by_group_charged(request, group):
  if group != None:
    bs = Booking.objects.filter(group=group).order_by('begin_time')
  else:
    bs = Booking.objects.order_by('begin_time')
  context = { 'bookings': bs }
  return render(request, 'swap/bookings_list.html', context)

def bookings(request):
  # list bookings according to query
  qs = request.GET
  kwargs = {}
  for k in [ 'user', 'charged', 'owner', 'approver', 'resource',
             'min_begin', 'max_begin', 'min_end', 'max_end' ]:
    if qs.get(k) != None:
      kwargs[k] = qs.get(k)
  if len(kwargs) > 0:
    bs = Booking.objects.filter(kwargs).order_by('begin_time')
  else:
    bs = Booking.objects.order_by('begin_time')
  context = { 'bookings': bs }
  return render(request, 'swap/bookings_list.html', context)

# request/approve bookings

def request_resource(request, resource):
  pass

def approve_request(request, req):
  pass

