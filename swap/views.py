from django.views.generic.list import ListView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.utils.timezone import utc, localtime, now
import json
import logging
import datetime
from pytz import timezone

from .models import Resource, Approver, Booking, Comment, Zone

# Used for logging events
logger =  logging.getLogger(__name__)

# Create your views here.

class ResourceList(ListView):
  model = Resource

# bookings

@login_required
def bookings(request):
  messages = []
  if request.method == 'POST':
    # booking request or request approval
    # then redirect to bookings list
    s = request.body.decode('utf-8')
    data = json.loads(s)
    if data['m'] == 'r':
      # request
      ngs = request.user.groups.count()
      if ngs >= 1:
        rg = request.user.groups.first()
      else:
        rg = None
        messages.append('User {0} does not have a group'.format(request.user))
      ri = int(data['r'])
      try:
        rr = Resource.objects.get(pk=ri)
        if not rr.available:
          messages.append('Resource {0} not currently available'.format(rr))
      except ObjectDoesNotExist:
        messages.append('Illegal resource id {0} (internal error)'.format(data['r']))
      #bdt = datetime.datetime.fromtimestamp(data['b'], datetime.timezone.utc)
      #edt = datetime.datetime.fromtimestamp(data['e'], datetime.timezone.utc)
      td = data['b']
      logger.info('{0}'.format(td))
      bdt = datetime.datetime(td[0], td[1], td[2], td[3], td[4]) # assume seconds = 0!
      logger.info('{0}'.format(bdt))
      bdt = datetime.datetime(td[0], td[1], td[2], td[3], td[4]) # assume seconds = 0!
      td = data['e']
      edt = datetime.datetime(td[0], td[1], td[2], td[3], td[4]) # assume seconds = 0!
      logger.info('{0}'.format(edt))
      logger.info('{0}'.format(data['z']))
      zone = pytz.timezone(data['z'])
# problem
      logger.info('before begin {0} end {1}'.format(bdt, edt))
      bdtu = localtime(bdt, zone)
      edtu = localtime(edt, zone)
      logger.info('begin {0} end {1}'.format(bdtu, edtu))

      if len(messages) == 0:
        logger.info('book')
        b = Booking(user=request.user, group=rg, resource=rr,
                    begin_time=bdtu, end_time=edtu)
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
              'messages': messages,
            }
  return render(request, 'swap/bookings_list.html', context)

# request/approve bookings

def request_resource(request, resource):
  pass

def approve_request(request, req):
  pass

