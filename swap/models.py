from django.db import models

from datetime import datetime, time, timedelta, timezone

# Create your models here.

def now_utc():
  return datetime.now(timezone.utc)

class Zone(models.Model):
  name = models.CharField(max_length=40)

  def __str__(self):
    return self.name

class Resource(models.Model):
  # a resource to be swapped
  name = models.CharField(max_length=100)
  # also use to make name for static information page
  group = models.ForeignKey('auth.Group')
  default_begin_time = models.TimeField(default=time(14,0)) # 2pm
  default_end_time = models.TimeField(default=time(12,0)) # 12 noon
  default_zone = models.ForeignKey('Zone', null=True, default=None)
  available = models.BooleanField(default=True)
  advance_period = models.DurationField(default=timedelta(90)) # 90 days
  # history fields:  when this resource started/stopped taking bookings
  open_time = models.DateTimeField(default=now_utc) # start taking bookings
  close_time = models.DateTimeField(null=True)
  modification_time = models.DateTimeField(auto_now=True)

  def __str__(self):
    return self.name

class Approver(models.Model):
  # a mapping between persons who can approve use of a resource, and the resource
  user = models.ForeignKey('auth.User')
  resource = models.ForeignKey('Resource', related_name='approver')

  def __str__(self):
    return "{0} ({1})".format(self.user, self.resource)

class Booking(models.Model):
  # a booking of a resource by a person
  user = models.ForeignKey('auth.User')
  group = models.ForeignKey('auth.Group', help_text='group to charge')
  resource = models.ForeignKey('Resource', related_name='booking')
  approval = models.ForeignKey('Approver', related_name='approval',
                               null=True, default=None,
                               help_text="booking approved by whom")
  begin_time = models.DateTimeField(['%Y-%m-%d %H:%M:%S'])
  end_time = models.DateTimeField(['%Y-%m-%d %H:%M:%S'])
  request_time = models.DateTimeField(auto_now_add=True)
  modification_time = models.DateTimeField(auto_now=True)

  def __str__(self):
    return "{0} {1} ({2})".format(self.begin_time, self.user, self.resource)

class Comment(models.Model):
  # a comment on a booking
  commenter = models.ForeignKey('auth.User')
  booking = models.ForeignKey('Booking', related_name='comment')
  time = models.DateTimeField(auto_now_add=True)
  text = models.TextField(blank=True)

  def __str__(self):
    return "{0} at {1} regarding {2}".format(
      self.commenter, self.time, self.booking)

