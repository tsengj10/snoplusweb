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
import time
import datetime
import pytz

from .models import Resource, Booking, Zone, now_timestamp

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
    logger.info('Bookings request')
    qs = request.POST
    s = request.body.decode('utf-8')
    logger.info('Request:  {0}'.format(s))
    data = json.loads(s)
    logger.info('  method {0}'.format(data['m']))
    if data['m'] == 'r':
      # request
      messages = request_resource(request.user, data)

    elif data['m'] == 'x':
      # cancel booking
      logger.info('Delete ' + s)

    elif data['m'] == 'e':
      # edit booking
      logger.info('Edit ' + s)

    else:
      # unrecognized command
      messages = [ 'Unrecognized post response ' + s ]
      #return redirect('swap:bookings')
      # we'd also like to return updated list of bookings
    return JsonResponse({ 'messages': messages })

  # respond to GET request
  context = { 'messages': messages }
  return render(request, 'swap/bookings_list.html', context)

# booking list in json form
@login_required
def bookings_json(request):
  qd = request.GET
  # list bookings according to query
  # by default, go back 31 days, forward 92 days
  #now = datetime.datetime.now(datetime.timezone.utc)
  #past = (now + datetime.timedelta(-31))
  #future = (now + datetime.timedelta(92))
  now = now_timestamp()
  sday = 24*60*60
  past = now - 31*sday
  future = now + 92*sday

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
      logger.info('Bookings filter {0}: {1}'.format(v,n))
  for k,v in [ ('b0', 'begin_time__gte'), # minimum begin_time
               ('b1', 'begin_time__lte'), # maximum begin_time
               ('e0', 'end_time__gte'), # minimum end_time
               ('e1', 'end_time__lte'), # maximum end_time
             ]:
    n = qd.get(k)
    if n != None and n.isnumeric():
      kwargs[v] = int(n)
  jb = []
  for b in Booking.objects.filter(**kwargs).order_by('begin_time'):
    #z = pytz.timezone(b.resource.default_zone.name)
    z = pytz.utc
    #tb = localtime(b.begin_time, z)
    #te = localtime(b.end_time, z)
    tr = localtime(b.request_time, z)
    tm = localtime(b.modification_time, z)
    jb.append({ 'bpk': b.pk,
                'u': b.user.pk,
                'b': b.booker.pk,
                'g': b.charge_group.pk,
                'r': b.resource.pk,
                'tb': b.begin_time,
                'te': b.end_time,
                'tr': date_array(tr),
                'tm': date_array(tm),
              })
  # above sends time arrays in UTC.
  ## probably want to change above times to local time,
  ## as javascript seems to want to take out time offset
  logger.info('Bookings response = {0}'.format(jb))
  return JsonResponse({ 'b': jb })

def date_array(t):
  return [ t.year, t.month, t.day, t.hour, t.minute ]

# request/approve bookings

def request_resource(user, data):
  logger.info('request_resource')
  messages = []
  ngs = user.groups.count()
  if ngs >= 1:
    rg = user.groups.first()
  else:
    rg = None
    messages.append('User {0} does not have a group'.format(user))
  logger.info('Resources requested = {0}'.format(data['r']))
  ri = [ int(e) for e in data['r'] ]
  logger.info('  turned into numbers {0}'.format(ri))
  rr = []
  for e in ri:
    logger.info('resource pk = {0}'.format(e))
    try:
      rr.append(Resource.objects.get(pk=e))
    except ObjectDoesNotExist:
      messages.append('Illegal resource id {0} (internal error)'.format(e))
      # also need to check availability and conflicts

  upk = int(data['u'])
  try:
    tenant = User.objects.get(pk=upk)
  except:
    messages.append('User {0} does not exist'.format(upk))

  logger.info('Resource request by booker {0} for user {1}'.format(user, tenant))

  if data['z'] == "":
    messages.append('No time zone specified')
    return messages
  else:
    zone = pytz.timezone(data['z'])
  td = data['b']
  logger.info('  begin time {0}'.format(td))
  bdtu = int(td / 1000)
  #if td == "" or len(td) < 5:
  #  messages.append('Begin time invalid')
  #else:
  #  bdt = datetime.datetime(td[0], td[1], td[2], td[3], td[4]) # assume seconds = 0!
  #  bdtu = make_aware(bdt, zone)
  #  logger.info('  begin time aware {0}'.format(bdtu))
  td = data['e']
  logger.info('  end time {0}'.format(td))
  edtu = int(td / 1000)
  #if td == "" or len(td) < 5:
  #  messages.append('End time invalid')
  #else:
  #  edt = datetime.datetime(td[0], td[1], td[2], td[3], td[4]) # assume seconds = 0!
  #  edtu = make_aware(edt, zone)
  #  logger.info('  end time aware {0}'.format(edtu))

  logger.info('Number of messages = {0}'.format(len(messages)))

  if len(messages) == 0:
    for e in rr:
      b = Booking(user=tenant, booker=user, charge_group=rg, resource=e,
                  begin_time=bdtu, end_time=edtu)
      b.save()
      logger.info('Booking created {0}'.format(b))

  return messages

