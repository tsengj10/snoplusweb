from django.views.generic.list import ListView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.utils.timezone import utc, localtime, now, make_aware
import json
import logging
import datetime
import pytz

from .models import Resource, Booking, Zone

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
    messages = []
    qs = request.POST
    s = request.body.decode('utf-8')
    data = json.loads(s)
    if data['m'] == 'r':
      # request
      messages = request_resource(request.user, data)

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
      messages = [ 'Unrecognized post response ' + s ]
      #return redirect('swap:bookings')
    return JsonResponse({ 'messages': messages })

  else:
    qd = request.GET
    qs = {}
    for k in [ 'u', 'c', 'o', 'a', 'r', 'b0', 'b1', 'e0', 'e1' ]:
      n = qd.get(k)
      if n != None and n.isnumeric():
        qs[k] = n
    context = { 'query': qs }
  return render(request, 'swap/bookings_list.html', context)

# booking list in json form

@login_required
def bookings_json(request):
  qd = request.GET
  # list bookings according to query
  # by default, go back 31 days, forward 92 days
  now = datetime.datetime.now(datetime.timezone.utc)
  #past = (now + datetime.timedelta(-90)).isoformat(' ')
  #future = (now + datetime.timedelta(90)).isoformat(' ')
  past = (now + datetime.timedelta(-31))
  future = (now + datetime.timedelta(92))
  kwargs = {}
  kwargs['begin_time__gte'] = past
  kwargs['begin_time__lte'] = future
  for k,v in [ ('u', 'user__pk'), # user
               ('b', 'booker__pk'), # booker
               ('c', 'charge_group__pk'), # group to charge
               ('r', 'resource__pk'), # resource id
             ]:
    n = qd.get(k)
    if n != None and n.isnumeric():
      kwargs[v] = n
  for k,v in [ ('b0', 'begin_time__gte'), # minimum begin_time
               ('b1', 'begin_time__lte'), # maximum begin_time
               ('e0', 'end_time__gte'), # minimum end_time
               ('e1', 'end_time__lte'), # maximum end_time
             ]:
    n = qd.get(k)
    if n != None and n.isnumeric():
      kwargs[v] = datetime.datetime.utcfromtimestamp(int(n))
  jb = []
  for b in Booking.objects.filter(**kwargs).order_by('begin_time'):
    z = pytz.timezone(b.resource.default_zone.name)
    tb = localtime(b.begin_time, z)
    te = localtime(b.end_time, z)
    tr = localtime(b.request_time, z)
    tm = localtime(b.modification_time, z)
    jb.append({ 'u': b.user.pk,
                'b': b.booker.pk,
                'g': b.charge_group.pk,
                'r': b.resource.pk,
                'tb': date_array(tb),
                'te': date_array(te),
                'tr': date_array(tr),
                'tm': date_array(tm),
              })
  # probably want to change above times to local time,
  # as javascript seems to want to take out time offset
  logger.info('Bookings response = {0}'.format(jb))
  return JsonResponse({ 'b': jb })

def date_array(t):
  return [ t.year, t.month, t.day, t.hour, t.minute ]

# request/approve bookings

def request_resource(user, data):
  messages = []
  ngs = user.groups.count()
  if ngs >= 1:
    rg = user.groups.first()
  else:
    rg = None
    messages.append('User {0} does not have a group'.format(user))
  ri = int(data['r'])
  try:
    rr = Resource.objects.get(pk=ri)
    if not rr.available:
      messages.append('Resource {0} not currently available'.format(rr))
  except ObjectDoesNotExist:
    messages.append('Illegal resource id {0} (internal error)'.format(data['r']))

  if data['z'] == "":
    zone = pytz.timezone(rr.default_zone.name)
  else:
    zone = pytz.timezone(data['z'])
  td = data['b']
  if td == "" or len(td) < 5:
    messages.append('Begin time invalid')
  else:
    bdt = datetime.datetime(td[0], td[1], td[2], td[3], td[4]) # assume seconds = 0!
    bdtu = make_aware(bdt, zone)
  td = data['e']
  if td == "" or len(td) < 5:
    messages.append('End time invalid')
  else:
    edt = datetime.datetime(td[0], td[1], td[2], td[3], td[4]) # assume seconds = 0!
    edtu = make_aware(edt, zone)

  if len(messages) == 0:
    b = Booking(user=user, booker=user, charge_group=rg, resource=rr,
                begin_time=bdtu, end_time=edtu)
    b.save()

  return messages

