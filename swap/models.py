from django.db import models

from datetime import datetime, time, timedelta, timezone

# Create your models here.

def now_utc():
  return datetime.now(timezone.utc)

class Zone(models.Model):
  name = models.CharField(max_length=40)
  utc_offset = models.CharField(max_length=10)

  def __str__(self):
    return "{0} ({1})".format(self.name, self.utc_offset)

class Resource(models.Model):
  # a resource to be swapped
  name = models.CharField(max_length=40) # short name
  description = models.TextField(blank=True) # more detailed description
  # also use to make name for static information page
  user_group = models.ForeignKey('auth.Group', related_name="user_resources") # can book themselves in
  admin_group = models.ForeignKey('auth.Group', related_name="admin_resources") # can mod bookings, book others
  # default booking information
  default_begin_time = models.TimeField(default=time(14,0)) # 2pm (in default_zone)
  default_end_time = models.TimeField(default=time(14,0)) # 12 noon (in default_zone)
  default_zone = models.ForeignKey('Zone', null=True, default=None)
  # maximum booking range
  advance_period = models.IntegerField(default=90) # days
  # history fields:  when this resource started/stopped taking bookings.
  # (a resource is active when a future booking date falls within range,
  # so to inactivate a resource we change close_time to current time)
  open_time = models.DateTimeField(default=now_utc) # start taking bookings (UTC)
  close_time = models.DateTimeField(null=True, blank=True) # store in UTC
  # bookkeeping
  modification_time = models.DateTimeField(auto_now=True) # store in UTC

  def __str__(self):
    return self.name

class Booking(models.Model):
  # a booking of a resource by a person
  user = models.ForeignKey('auth.User', related_name="user_bookings") # person for whom resource is booked
  booker = models.ForeignKey('auth.User', related_name="booker_bookings") # person booking the resource
  charge_group = models.ForeignKey('auth.Group', help_text='group to charge')
  resource = models.ForeignKey('Resource', related_name='booking')
  begin_time = models.DateTimeField(['%Y-%m-%d %H:%M:%S'])
  end_time = models.DateTimeField(['%Y-%m-%d %H:%M:%S'])
  request_time = models.DateTimeField(auto_now_add=True)
  modification_time = models.DateTimeField(auto_now=True)

  def __str__(self):
    return "{0} {1} ({2})".format(self.begin_time, self.user, self.resource)

