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

from .models import Resource, Approver, Booking, Comment

# Used for logging events
logger =  logging.getLogger(__name__)

# Create your views here.

class ResourceList(ListView):
  model = Resource

# bookings

@login_required
def bookings(request):
  if request.method == 'POST':
    # booking request or request approval
    # then redirect to bookings list
    s = request.body.decode('utf-8')
    data = json.loads(s)
    if data['m'] == 'r':
      # request
      logger.info('Request ' + s)
      logger.info('  resource ' + data['r'])
      bdt = datetime.datetime.fromtimestamp(data['b'], datetime.timezone.utc)
      edt = datetime.datetime.fromtimestamp(data['e'], datetime.timezone.utc)
      logger.info('  begin {0} end {1}'.format(bdt, edt))
    elif data['m'] == 'a':
      # approve
      logger.info('Approve ' + s)
    elif data['m'] == 'c':
      # comment
      logger.info('Comment ' + s)
    else:
      # unrecognized command
      logger.error('Unrecognized post response ' + s)
    return redirect('swap:bookings')

  # list bookings according to query
  # by default, go back 1 year, forward 90 days
  qs = request.GET
  now = datetime.datetime.now(datetime.timezone.utc)
  #past = (now + datetime.timedelta(-90)).isoformat(' ')
  #future = (now + datetime.timedelta(90)).isoformat(' ')
  past = (now + datetime.timedelta(-90))
  future = (now + datetime.timedelta(90))
  kwargs = {}
  kwargs['begin_time__gte'] = past
  kwargs['begin_time__lte'] = future
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
  bs = Booking.objects.filter(**kwargs).order_by('begin_time')
  comments = Comment.objects.filter(time__gte=past)
  users = User.objects.all()
  groups = Group.objects.all()
  approvers = Approver.objects.all()
  resources = Resource.objects.all()
  context = { 'bookings': bs,
              'comments': comments,
              'users': users,
              'groups': groups,
              'approvers': approvers,
              'resources': resources,
            }
  return render(request, 'swap/bookings_list.html', context)

# request/approve bookings

def request_resource(request, resource):
  pass

def approve_request(request, req):
  pass

