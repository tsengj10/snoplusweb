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

from .models import Resource, Approver, Booking, Comment, Zone

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
      #bdt = datetime.datetime.fromtimestamp(data['b'], datetime.timezone.utc)
      #edt = datetime.datetime.fromtimestamp(data['e'], datetime.timezone.utc)
      #logger.info('  begin {0} end {1}'.format(bdt, edt))
      ngs = request.user.groups.count()
      if ngs >= 1:
        rg = request.user.groups.first()
      else:
        rg = None
        logger.error('User {0} does not have a group'.format(request.user))
        return redirect('swap:bookings')
      ri = int(data['r'])
      rr = get_object_or_404(Resource, pk=ri)
      logger.info('resource {0}'.format(rr))
      logger.info('  available {0}'.format(rr.available))
      if not rr.available:
        logger.error('Resource {0} not currently available'.format(rr))
        return redirect('swap:bookings')
      logger.info('  b {0}'.format(data['b']))
      if data['b'] > 0:
        bdt = datetime.datetime.fromtimestamp(data['b'], datetime.timezone.utc)
        logger.info('  begin time {0}'.format(bdt))
      else:
        logger.error('Beginning time not specified')
        return redirect('swap:bookings')
      logger.info('  e {0}'.format(data['e']))
      if data['e'] > 0:
        edt = datetime.datetime.fromtimestamp(data['e'], datetime.timezone.utc)
      else:
        logger.error('Ending time not specified')
        return redirect('swap:bookings')
      logger.info('about to make booking')
      b = Booking(user=request.user, group=rg, resource=rr,
                  begin_time=bdt, end_time=edt)
      b.save()

    elif data['m'] == 'x':
      # cancel booking
      logger.info('Delete ' + s)

    elif data['m'] == 'e':
      # edit booking
      logger.info('Edit ' + s)

    elif data['m'] == 'a':
      # approve
      logger.info('Approve ' + s)

    elif data['m'] == 'v':
      # revoke approval
      logger.info('Revoke ' + s)

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
  context = { 'bookings': bs,
              'comments': comments,
            }
  return render(request, 'swap/bookings_list.html', context)

# request/approve bookings

def request_resource(request, resource):
  pass

def approve_request(request, req):
  pass

