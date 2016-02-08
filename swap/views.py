from django.views.generic.list import ListView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.http import JsonResponse
import json
import logging
import datetime

from .models import Resource, Approver, Booking

# Create your views here.

class ResourceList(ListView):
  model = Resource

# bookings

@login_required
def bookings(request):
  # list bookings according to query
  qs = request.GET
  kwargs = {}
  for k,v in [ ('u', 'user__pk'), # user
               ('c', 'group__pk'), # group to charge
               ('o', 'resource__group__pk'), # resource "owner"
               ('a', 'approval__user__pk'), # approver
               ('r', 'resource__pk'), # resource id
             ]:
    n = qs.get(k)
    if n != None and n.isnumeric():
      kwargs[v] = n
  for k,v in [ ('b0', 'begin_time__gte'), # minimum begin_time
               ('b1', 'begin_time__lte'), # maximum begin_time
               ('e0', 'end_time__gte'), # minimum end_time
               ('e1', 'end_time__lte'), # maximum end_time
             ]:
    n = qs.get(k)
    if n != None and n.isnumeric():
      kwargs[v] = datetime.datetime.utcfromtimestamp(int(n))
  if len(kwargs) > 0:
    bs = Booking.objects.filter(kwargs).order_by('begin_time')
  else:
    bs = Booking.objects.order_by('begin_time')
  context = { 'bookings': bs }
  return render(request, 'swap/bookings_list.html', context)

# request/approve bookings

@login_required
def request_resource(request, resource):
  pass

@login_required
def approve_request(request, req):
  pass

